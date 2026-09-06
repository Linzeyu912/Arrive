import { useState } from 'react';
import { Link } from 'react-router-dom';
import { listSources } from '../../api/endpoints';
import type { Source } from '../../api/types';
import { useLoad } from '../../lib/useLoad';
import { formatDate } from '../../lib/time';
import { SOURCE_KIND_LABELS } from '../../lib/labels';
import { EmptyView, ErrorView, LoadingView } from '../../components/StatusView';
import SourceForm from './SourceForm';

export default function SourcesPage() {
  const { state, reload } = useLoad(listSources);
  const [formOpen, setFormOpen] = useState(false);
  const [formDirty, setFormDirty] = useState(false);
  const [justCreated, setJustCreated] = useState<Source | null>(null);

  const onCreated = (source: Source) => {
    setJustCreated(source);
    setFormOpen(false);
    reload();
  };

  return (
    <div>
      <h1>来源</h1>
      <p className="muted">
        登记外部文章、书籍等来源的元信息。登记不等于抓取全文，也不表示认同。
      </p>

      <p>
        <button
          type="button"
          className="button"
          onClick={() => {
            if (formDirty && !window.confirm('登记表单里还有未提交的内容，确定收起吗？')) {
              return;
            }
            setFormOpen((open) => !open);
          }}
          aria-expanded={formOpen}
        >
          {formOpen ? '收起登记表单' : '登记来源'}
        </button>
      </p>

      {formOpen && (
        <section aria-label="登记来源表单">
          <SourceForm onCreated={onCreated} onDirtyChange={setFormDirty} />
          <hr className="divider" />
        </section>
      )}

      {justCreated && (
        <div className="notice notice--ok" role="status">
          已登记 <Link to={`/sources/${justCreated.id}`}>{justCreated.id}</Link>
          「{justCreated.title}」。这只是元信息登记，全文尚未抓取。
        </div>
      )}

      {state.status === 'loading' && <LoadingView text="正在读取来源…" />}
      {state.status === 'error' && <ErrorView error={state.error} onRetry={reload} />}
      {state.status === 'success' &&
        (state.data.length === 0 ? (
          <EmptyView>
            <p style={{ margin: 0 }}>还没有登记来源。</p>
          </EmptyView>
        ) : (
          <ul className="record-list">
            {[...state.data].reverse().map((source) => (
              <li key={source.id}>
                <Link to={`/sources/${source.id}`}>{source.title}</Link>
                <p className="meta-line">
                  {source.id} · {SOURCE_KIND_LABELS[source.kind]} ·{' '}
                  {source.creator ?? '作者未记录'} · 登记于{' '}
                  {formatDate(source.created_at)} ·{' '}
                  {source.propositions.length} 条来源命题
                </p>
              </li>
            ))}
          </ul>
        ))}
    </div>
  );
}
