import { afterEach, describe, expect, it, vi } from 'vitest';
import { ApiError, apiRequest } from './client';

function jsonResponse(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('apiRequest 错误解析', () => {
  it('成功时返回解析后的 JSON', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(jsonResponse(200, { status: 'ok' })),
    );
    await expect(apiRequest('/health')).resolves.toEqual({ status: 'ok' });
  });

  it('422 校验数组映射为字段错误', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        jsonResponse(422, {
          detail: [
            { loc: ['body', 'content'], msg: 'Field required' },
            { loc: ['body', 'kind'], msg: 'Input should be ...' },
          ],
        }),
      ),
    );
    const error = await apiRequest('/api/v1/materials', {
      method: 'POST',
      body: {},
    }).catch((e: unknown) => e);
    expect(error).toBeInstanceOf(ApiError);
    const apiError = error as ApiError;
    expect(apiError.kind).toBe('validation');
    expect(apiError.fieldErrors).toEqual([
      { field: 'content', message: 'Field required' },
      { field: 'kind', message: 'Input should be ...' },
    ]);
  });

  it('422 字符串 detail 原样作为消息', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        jsonResponse(422, { detail: 'target_id must be a source proposition' }),
      ),
    );
    const error = await apiRequest('/x', { method: 'POST', body: {} }).catch(
      (e: unknown) => e,
    );
    expect((error as ApiError).message).toBe(
      'target_id must be a source proposition',
    );
  });

  it('404 与 409 分类正确', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(jsonResponse(404, { detail: 'not found' })),
    );
    const notFound = await apiRequest('/x').catch((e: unknown) => e);
    expect((notFound as ApiError).kind).toBe('not_found');

    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(jsonResponse(409, { detail: 'conflict' })),
    );
    const conflict = await apiRequest('/x').catch((e: unknown) => e);
    expect((conflict as ApiError).kind).toBe('conflict');
  });

  it('网络故障归为 network，不回显异常栈', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockRejectedValue(new TypeError('Failed to fetch')),
    );
    const error = await apiRequest('/x').catch((e: unknown) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).kind).toBe('network');
    expect((error as ApiError).message).not.toContain('Failed to fetch');
  });

  it('非 JSON 错误体保留默认文案', async () => {
    vi.stubGlobal(
      'fetch',
      vi
        .fn()
        .mockResolvedValue(new Response('<html>oops</html>', { status: 500 })),
    );
    const error = await apiRequest('/x').catch((e: unknown) => e);
    expect((error as ApiError).kind).toBe('server');
  });
});
