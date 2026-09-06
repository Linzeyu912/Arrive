/**
 * 素材列表：GET /api/v1/materials 全量加载，本地筛选明确标注“仅筛选已加载内容”。
 */
import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { listMaterials } from '../../api/endpoints';
import { useLoad } from '../../lib/useLoad';
import { formatDate } from '../../lib/time';
import { MATERIAL_KIND_LABELS, PRIVACY_LABELS } from '../../lib/labels';
import { EmptyView, ErrorView, LoadingView } from '../../components/StatusView';

export default function MaterialsPage() {
  const { state, reload } = useLoad(listMaterials);
  const [filter, setFilter] = useState('');

  const materials = useMemo(() => {
    if (state.status !== 'success') return [];
    const keyword = filter.trim().toLowerCase();
    const sorted = [...state.data].reverse(); // 最新在前（本地排序）
    if (!keyword) return sorted;
    return sorted.filter((material) =>
      material.content.toLowerCase().includes(keyword),
    );
  }, [state, filter]);

  return (
    <div>
      <h1>素材</h1>
      <p className="muted">保存下来的原话。镜像确认尚未接入，这里只做忠实回看。</p>

      {state.status === 'loading' && <LoadingView text="正在读取素材…" />}
      {state.status === 'error' && <ErrorView error={state.error} onRetry={reload} />}
      {state.status === 'success' && (
        <>
          {state.data.length > 0 && (
            <div className="field" style={{ maxWidth: 360 }}>
              <label htmlFor="material-filter">筛选已加载内容</label>
              <input
                id="material-filter"
                type="text"
                value={filter}
                placeholder="输入关键词"
                onChange={(event) => setFilter(event.target.value)}
              />
              <p className="field-hint">仅筛选当前已加载的列表，不查询服务器。</p>
            </div>
          )}
          {state.data.length === 0 ? (
            <EmptyView>
              <p style={{ margin: 0 }}>还没有素材。</p>
              <p style={{ margin: '8px 0 0' }}>
                <Link to="/">去记录第一段原话</Link>
              </p>
            </EmptyView>
          ) : materials.length === 0 ? (
            <EmptyView>
              <p style={{ margin: 0 }}>已加载内容中没有匹配「{filter}」的素材。</p>
            </EmptyView>
          ) : (
            <ul className="record-list">
              {materials.map((material) => (
                <li key={material.id}>
                  <Link to={`/materials/${material.id}`}>
                    <span className="excerpt verbatim">{material.content}</span>
                  </Link>
                  <p className="meta-line">
                    {material.id} · {MATERIAL_KIND_LABELS[material.kind]} ·{' '}
                    {PRIVACY_LABELS[material.privacy]} · 录入于{' '}
                    {formatDate(material.recorded_at)}
                    {material.preserve_verbatim ? ' · 保留原话' : ''}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </div>
  );
}
