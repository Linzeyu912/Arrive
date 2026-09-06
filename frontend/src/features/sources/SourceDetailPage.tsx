/**
 * 来源详情：归属可追溯；来源命题区分作者明确表达 / 协作者归纳。
 * 「回应这个命题」以来源命题为目标进入观点回应页，不是来源定位批注。
 */
import { Link, useParams } from 'react-router-dom';
import { getSource } from '../../api/endpoints';
import { useLoad } from '../../lib/useLoad';
import { formatDateTime } from '../../lib/time';
import {
  ATTRIBUTION_LABELS,
  SOURCE_KIND_LABELS,
} from '../../lib/labels';
import { EmptyView, ErrorView, LoadingView } from '../../components/StatusView';

export default function SourceDetailPage() {
  const { sourceId } = useParams<{ sourceId: string }>();
  const { state, reload } = useLoad(
    () => getSource(sourceId ?? ''),
    [sourceId],
  );

  if (state.status === 'loading') {
    return <LoadingView text="正在读取来源…" />;
  }
  if (state.status === 'error') {
    return (
      <div>
        <ErrorView error={state.error} onRetry={reload} />
        <p>
          <Link to="/sources">返回来源列表</Link>
        </p>
      </div>
    );
  }

  const source = state.data;

  return (
    <article>
      <p className="meta-line">
        <Link to="/sources">← 来源</Link>
      </p>
      <h1 style={{ fontSize: '1.3rem' }}>{source.title}</h1>
      <p className="meta-line">
        {source.id} · {SOURCE_KIND_LABELS[source.kind]} · 登记于{' '}
        {formatDateTime(source.created_at)}
      </p>

      <dl style={{ margin: 0 }}>
        <div className="field">
          <dt className="muted small">作者</dt>
          <dd style={{ margin: 0 }}>{source.creator ?? '作者未记录'}</dd>
        </div>
        <div className="field">
          <dt className="muted small">原始链接</dt>
          <dd style={{ margin: 0, overflowWrap: 'anywhere' }}>
            <a href={source.original_url} target="_blank" rel="noreferrer noopener">
              {source.original_url}
            </a>
          </dd>
        </div>
        {source.platform && (
          <div className="field">
            <dt className="muted small">平台</dt>
            <dd style={{ margin: 0 }}>{source.platform}</dd>
          </div>
        )}
        {source.publisher && (
          <div className="field">
            <dt className="muted small">出版方</dt>
            <dd style={{ margin: 0 }}>{source.publisher}</dd>
          </div>
        )}
        {source.published_at && (
          <div className="field">
            <dt className="muted small">出版时间</dt>
            <dd style={{ margin: 0 }}>{source.published_at}</dd>
          </div>
        )}
        {source.topics.length > 0 && (
          <div className="field">
            <dt className="muted small">主题</dt>
            <dd style={{ margin: 0 }}>{source.topics.join('、')}</dd>
          </div>
        )}
      </dl>

      <hr className="divider" />

      <h2>来源命题</h2>
      {source.propositions.length === 0 ? (
        <EmptyView>
          <p style={{ margin: 0 }}>
            这条来源还没有登记命题。当前后端没有单独追加来源命题的接口，
            如需补充只能重新登记来源。
          </p>
        </EmptyView>
      ) : (
        <ul className="record-list">
          {source.propositions.map((proposition) => (
            <li key={proposition.id}>
              <p className="verbatim" style={{ margin: 0 }}>
                {proposition.text}
              </p>
              <p className="meta-line">
                {proposition.id} · {ATTRIBUTION_LABELS[proposition.attribution]}
              </p>
              <p style={{ margin: '4px 0 0' }}>
                <Link
                  to={`/responses?target=${encodeURIComponent(proposition.id)}`}
                >
                  回应这个命题
                </Link>
              </p>
            </li>
          ))}
        </ul>
      )}

      <p className="muted small">
        来源快照、原句定位批注与全文抓取尚未实现；以上是登记时的元信息。
      </p>
    </article>
  );
}
