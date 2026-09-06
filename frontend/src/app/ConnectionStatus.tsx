import { useEffect, useState } from 'react';
import { fetchHealth } from '../api/endpoints';

type ConnectionState = 'checking' | 'ok' | 'down';

export default function ConnectionStatus() {
  const [state, setState] = useState<ConnectionState>('checking');

  useEffect(() => {
    let cancelled = false;
    const check = async () => {
      try {
        await fetchHealth();
        if (!cancelled) setState('ok');
      } catch {
        if (!cancelled) setState('down');
      }
    };
    void check();
    const timer = setInterval(() => void check(), 30000);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, []);

  const className =
    state === 'ok'
      ? 'connection connection--ok'
      : state === 'down'
        ? 'connection connection--down'
        : 'connection';
  const text =
    state === 'ok'
      ? '本地服务已连接'
      : state === 'down'
        ? '本地服务未连接'
        : '正在检查连接…';

  return (
    <p className={className} role="status">
      <span className="connection-dot" aria-hidden="true" />
      {text}
    </p>
  );
}
