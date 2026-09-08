import { afterEach, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import LocalRecords from './LocalRecords';
import SavedOverview from './SavedOverview';

afterEach(() => vi.unstubAllGlobals());
const json = (value: unknown) => new Response(JSON.stringify(value), { headers: { 'Content-Type': 'application/json' } });

it('重新挂载后从数据库读取来源，不依赖本次保存回执', async () => {
  vi.stubGlobal('fetch', vi.fn((url: string) => Promise.resolve(json(url.endsWith('/sources')
    ? [{ id: 'SRC-0099', title: '完全虚构的历史来源' }] : []))));
  const page = render(<MemoryRouter><SavedOverview /></MemoryRouter>);
  expect(await screen.findByText('完全虚构的历史来源')).toHaveAttribute('href', '/sources/SRC-0099');
  page.unmount();
  render(<MemoryRouter><SavedOverview /></MemoryRouter>);
  expect(await screen.findByText('来源 1 条')).toBeInTheDocument();
});

it('仅展开时读取原件，并作为文本显示而不执行 HTML', async () => {
  const fetch = vi.fn((url: string) => Promise.resolve(json(url.endsWith('/local-records') ? [{
    id: 1, relative_key: 'decisions/synthetic.md', source_id: null, status: 'archived',
    note: '完全虚构的档案', recorded_at: '2020-01-01T00:00:00+08:00',
  }] : { content: '<img src=x onerror=alert(1)>' })));
  vi.stubGlobal('fetch', fetch);
  render(<MemoryRouter><LocalRecords /></MemoryRouter>);
  expect(await screen.findByText('完全虚构的档案')).toBeInTheDocument();
  expect(fetch).toHaveBeenCalledTimes(1);
  await userEvent.click(screen.getByText('查看旧文件原件'));
  expect(await screen.findByText('<img src=x onerror=alert(1)>')).toBeInTheDocument();
  expect(screen.queryByRole('img')).not.toBeInTheDocument();
});
