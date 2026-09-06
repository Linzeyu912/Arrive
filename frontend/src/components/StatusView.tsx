import type { ReactNode } from 'react';
import { ApiError } from '../api/client';

export function LoadingView({ text = '加载中…' }: { text?: string }) {
  return (
    <p className="notice notice--muted" role="status">
      {text}
    </p>
  );
}

export function EmptyView({ children }: { children: ReactNode }) {
  return <div className="notice notice--muted">{children}</div>;
}

export function ErrorView({
  error,
  onRetry,
}: {
  error: unknown;
  onRetry?: () => void;
}) {
  const apiError = error instanceof ApiError ? error : null;
  return (
    <div className="notice notice--error" role="alert">
      <p style={{ margin: 0 }}>
        {apiError ? apiError.message : '出现未预期的错误。'}
      </p>
      {apiError && apiError.fieldErrors.length > 0 && (
        <ul style={{ margin: '8px 0 0' }}>
          {apiError.fieldErrors.map((item, index) => (
            <li key={index}>
              {item.field}：{item.message}
            </li>
          ))}
        </ul>
      )}
      {onRetry && (
        <p style={{ margin: '8px 0 0' }}>
          <button type="button" className="button button--secondary" onClick={onRetry}>
            重试
          </button>
        </p>
      )}
    </div>
  );
}
