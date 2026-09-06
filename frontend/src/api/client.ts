/**
 * HTTP 客户端：只请求相对路径 /api/v1 与 /health，由开发代理转发到后端。
 * 错误解析覆盖 FastAPI 的 422 校验数组、字符串 detail 以及网络/超时故障。
 * POST 不自动重试：超时可能发生在服务端写入之后，交由用户核对。
 */

export type ApiErrorKind =
  | 'validation'
  | 'not_found'
  | 'conflict'
  | 'server'
  | 'network'
  | 'timeout'
  | 'unknown';

export interface FieldError {
  field: string;
  message: string;
}

export class ApiError extends Error {
  readonly kind: ApiErrorKind;
  readonly status: number | null;
  readonly fieldErrors: FieldError[];

  constructor(
    kind: ApiErrorKind,
    message: string,
    status: number | null = null,
    fieldErrors: FieldError[] = [],
  ) {
    super(message);
    this.name = 'ApiError';
    this.kind = kind;
    this.status = status;
    this.fieldErrors = fieldErrors;
  }
}

interface ValidationItem {
  loc?: unknown;
  msg?: unknown;
}

function parseValidationDetail(detail: unknown): FieldError[] {
  if (!Array.isArray(detail)) return [];
  const errors: FieldError[] = [];
  for (const item of detail as ValidationItem[]) {
    const loc = Array.isArray(item?.loc) ? item.loc : [];
    const rawField = loc[loc.length - 1];
    const field = typeof rawField === 'string' ? rawField : '请求内容';
    const message = typeof item?.msg === 'string' ? item.msg : '取值不符合要求';
    errors.push({ field, message });
  }
  return errors;
}

function statusToKind(status: number): ApiErrorKind {
  if (status === 404) return 'not_found';
  if (status === 409) return 'conflict';
  if (status === 422) return 'validation';
  if (status >= 500) return 'server';
  return 'unknown';
}

const DEFAULT_MESSAGES: Record<ApiErrorKind, string> = {
  validation: '提交内容未通过校验，请检查标出的字段。',
  not_found: '没有找到目标记录，它可能从未保存成功。',
  conflict: '请求与已有记录冲突，请核对后再试。',
  server: '本地服务暂时出现问题，请稍后重试。',
  network: '无法连接本地服务，请确认后端已经启动。',
  timeout: '请求超时，暂时无法确认是否已保存。请勿重复提交，先到列表中核对。',
  unknown: '出现未预期的错误。',
};

async function parseErrorResponse(response: Response): Promise<ApiError> {
  const kind = statusToKind(response.status);
  let message = DEFAULT_MESSAGES[kind];
  let fieldErrors: FieldError[] = [];
  try {
    const body: unknown = await response.json();
    if (body && typeof body === 'object' && 'detail' in body) {
      const detail = (body as { detail: unknown }).detail;
      if (typeof detail === 'string' && detail.length > 0) {
        message = detail;
      } else {
        fieldErrors = parseValidationDetail(detail);
        if (fieldErrors.length > 0) {
          message = DEFAULT_MESSAGES.validation;
        }
      }
    }
  } catch {
    // 非 JSON 错误体，保留默认文案；不回显原始响应。
  }
  return new ApiError(kind, message, response.status, fieldErrors);
}

export interface RequestOptions {
  method?: 'GET' | 'POST';
  body?: unknown;
  timeoutMs?: number;
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { method = 'GET', body, timeoutMs = 20000 } = options;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  let response: Response;
  try {
    response = await fetch(path, {
      method,
      headers: body === undefined ? undefined : { 'Content-Type': 'application/json' },
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: controller.signal,
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new ApiError('timeout', DEFAULT_MESSAGES.timeout);
    }
    throw new ApiError('network', DEFAULT_MESSAGES.network);
  } finally {
    clearTimeout(timer);
  }
  if (!response.ok) {
    throw await parseErrorResponse(response);
  }
  return (await response.json()) as T;
}
