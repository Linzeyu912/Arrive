import { Link } from 'react-router-dom';
import { useState } from 'react';
import { apiRequest } from '../../api/client';
import { useLoad } from '../../lib/useLoad';
import { ErrorView, LoadingView } from '../../components/StatusView';
import { formatDateTime } from '../../lib/time';

type LocalRecord = { id: number; relative_key: string; source_id: string | null;
  status: string; note: string; recorded_at: string };
const list = () => apiRequest<LocalRecord[]>('/api/v1/local-records');
const labels: Record<string, string> = { imported: '已适配', archived: '原件档案', review: '待核对' };

function Original({ id }: { id: number }) {
  const { state, reload } = useLoad(() => apiRequest<{ content: string }>(`/api/v1/local-records/${id}`), [id]);
  if (state.status === 'loading') return <LoadingView />;
  if (state.status === 'error') return <ErrorView error={state.error} onRetry={reload} />;
  return <pre style={{ whiteSpace: 'pre-wrap', overflowWrap: 'anywhere', fontFamily: 'inherit' }}>{state.data.content}</pre>;
}

function RecordRow({ row }: { row: LocalRecord }) {
  const [opened, setOpened] = useState(false);
  return <article className="card" style={{ marginBottom: 16, padding: 20 }}>
    <p><strong>{row.relative_key}</strong> · {labels[row.status] ?? row.status}</p>
    <p className="muted">{row.note}</p>
    <p className="muted">适配入库时间：{formatDateTime(row.recorded_at)}</p>
    {row.source_id && <p><Link to={`/sources/${row.source_id}`}>查看来源 {row.source_id}</Link></p>}
    <details onToggle={(event) => { if (event.currentTarget.open) setOpened(true); }}>
      <summary>查看旧文件原件</summary>{opened && <Original id={row.id} />}
    </details>
  </article>;
}

export default function LocalRecords() {
  const { state, reload } = useLoad(list);
  return <section>
    <h1>本地档案</h1>
    <p className="muted">自动读取本地数据库。旧文件在后端启动时适配入库，原文件保留；文件变化会保留新版本。档案不表示已确认的个人观点。</p>
    <button className="button" onClick={reload}>刷新档案</button>
    {state.status === 'loading' && <LoadingView />}
    {state.status === 'error' && <ErrorView error={state.error} onRetry={reload} />}
    {state.status === 'success' && (state.data.length ? state.data.map(row => <RecordRow key={row.id} row={row} />) : <p>还没有旧文件档案。新录入内容请到“素材”或“来源”查看。</p>)}
  </section>;
}
