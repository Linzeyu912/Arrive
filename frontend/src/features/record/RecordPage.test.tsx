/**
 * 记录页保存流程测试：使用内存路由 + mock fetch。
 * 覆盖：原始字符串提交、成功后显示编号、保存中防重复提交。
 */
import { afterEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { createMemoryRouter, RouterProvider } from 'react-router-dom';
import RecordPage from './RecordPage';

function renderRecordPage() {
  const postFetch = globalThis.fetch;
  vi.stubGlobal('fetch', (url: RequestInfo | URL, init?: RequestInit) =>
    init?.method === 'GET'
      ? Promise.resolve(new Response('[]', { headers: { 'Content-Type': 'application/json' } }))
      : postFetch(url, init));
  const router = createMemoryRouter([{ path: '/', element: <RecordPage /> }], {
    initialEntries: ['/'],
  });
  return render(<RouterProvider router={router} />);
}

const SYNTHETIC_MATERIAL = {
  id: 'M001',
  kind: 'thought',
  content: '【合成示例】第一行\n第二行',
  privacy: 'private',
  preserve_verbatim: true,
  recorded_at: '2026-09-06T05:30:00+00:00',
  effective_at: '2026-09-06T05:30:00+00:00',
  context: null,
};

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('记录页', () => {
  it('提交原始字符串并在真实响应后显示回执', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(SYNTHETIC_MATERIAL), {
        status: 201,
        headers: { 'Content-Type': 'application/json' },
      }),
    );
    vi.stubGlobal('fetch', fetchMock);

    renderRecordPage();
    const user = userEvent.setup();
    const textarea = screen.getByLabelText('原话');
    await user.click(textarea);
    await user.paste(SYNTHETIC_MATERIAL.content);
    await user.click(screen.getByRole('button', { name: '保存' }));

    await waitFor(() => {
      expect(screen.getByText(/已保存 M001/)).toBeInTheDocument();
    });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe('/api/v1/materials');
    const body = JSON.parse(init.body as string) as Record<string, unknown>;
    expect(body.content).toBe(SYNTHETIC_MATERIAL.content);
    expect(body.preserve_verbatim).toBe(true);
    expect(body).not.toHaveProperty('mirror_status');
  });

  it('空白内容不发起请求', async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
    renderRecordPage();
    const user = userEvent.setup();
    const textarea = screen.getByLabelText('原话');
    await user.click(textarea);
    await user.paste('   ');
    // 保存按钮在内容全空白时被禁用
    expect(screen.getByRole('button', { name: '保存' })).toBeDisabled();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('保存期间输入被锁定，防止连点重复提交', async () => {
    let resolveFetch: (value: Response) => void = () => {};
    const fetchMock = vi.fn().mockImplementation(
      () =>
        new Promise<Response>((resolve) => {
          resolveFetch = resolve;
        }),
    );
    vi.stubGlobal('fetch', fetchMock);
    renderRecordPage();
    const user = userEvent.setup();
    await user.click(screen.getByLabelText('原话'));
    await user.paste('合成内容');
    const button = screen.getByRole('button', { name: '保存' });
    await user.click(button);
    expect(screen.getByLabelText('原话')).toBeDisabled();
    expect(screen.getByRole('button', { name: '保存中…' })).toBeDisabled();
    expect(fetchMock).toHaveBeenCalledTimes(1);
    resolveFetch(
      new Response(JSON.stringify(SYNTHETIC_MATERIAL), {
        status: 201,
        headers: { 'Content-Type': 'application/json' },
      }),
    );
    await waitFor(() => {
      expect(screen.getByText(/已保存 M001/)).toBeInTheDocument();
    });
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it('网络失败保留输入并提示核对，不自动重发', async () => {
    const fetchMock = vi.fn().mockRejectedValue(new TypeError('Failed to fetch'));
    vi.stubGlobal('fetch', fetchMock);
    renderRecordPage();
    const user = userEvent.setup();
    await user.click(screen.getByLabelText('原话'));
    await user.paste('不能丢的合成内容');
    await user.click(screen.getByRole('button', { name: '保存' }));
    await waitFor(() => {
      expect(screen.getByText(/暂时无法确认是否已保存/)).toBeInTheDocument();
    });
    expect(screen.getByLabelText('原话')).toHaveValue('不能丢的合成内容');
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});
