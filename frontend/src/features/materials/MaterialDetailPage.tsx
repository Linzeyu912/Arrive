/**
 * 素材详情：后端没有单条 GET，先加载列表再按 ID 查找；
 * 加载完成前不闪现“找不到素材”。
 */
import { Link, useParams } from 'react-router-dom';
import { listMaterials } from '../../api/endpoints';
import { useLoad } from '../../lib/useLoad';
import { formatDateTime } from '../../lib/time';
import { MATERIAL_KIND_LABELS, PRIVACY_LABELS } from '../../lib/labels';
import { EmptyView, ErrorView, LoadingView } from '../../components/StatusView';

export default function MaterialDetailPage() {
  const { materialId } = useParams<{ materialId: string }>();
  const { state, reload } = useLoad(listMaterials, [materialId]);

  if (state.status === 'loading') {
    return <LoadingView text="正在读取素材…" />;
  }
  if (state.status === 'error') {
    return <ErrorView error={state.error} onRetry={reload} />;
  }

  const material = state.data.find((item) => item.id === materialId);
  if (!material) {
    return (
      <div>
        <h1>素材</h1>
        <EmptyView>
          <p style={{ margin: 0 }}>
            已加载全部素材，没有找到编号为「{materialId}」的记录。
          </p>
          <p style={{ margin: '8px 0 0' }}>
            <Link to="/materials">返回素材列表</Link>
          </p>
        </EmptyView>
      </div>
    );
  }

  return (
    <article>
      <p className="meta-line">
        <Link to="/materials">← 素材</Link>
      </p>
      <h1 style={{ fontSize: '1.2rem' }}>
        {material.id} · {MATERIAL_KIND_LABELS[material.kind]}
      </h1>

      <p className="verbatim" style={{ fontSize: '1.05rem' }}>
        {material.content}
      </p>

      <hr className="divider" />

      <dl style={{ margin: 0 }}>
        <div className="field">
          <dt className="muted small">编号</dt>
          <dd style={{ margin: 0 }}>{material.id}</dd>
        </div>
        <div className="field">
          <dt className="muted small">隐私状态</dt>
          <dd style={{ margin: 0 }}>{PRIVACY_LABELS[material.privacy]}</dd>
        </div>
        <div className="field">
          <dt className="muted small">录入时间</dt>
          <dd style={{ margin: 0 }}>{formatDateTime(material.recorded_at)}</dd>
        </div>
        <div className="field">
          <dt className="muted small">思想发生时间</dt>
          <dd style={{ margin: 0 }}>
            {formatDateTime(material.effective_at)}
            <span className="muted small">
              {' '}
              （当前后端在未填写时回退为录入时间；本记录不具备可靠的「未知 / 当下」区分，
              请勿把该值当作已确认的思想发生时间。）
            </span>
          </dd>
        </div>
        {material.context && (
          <div className="field">
            <dt className="muted small">上下文</dt>
            <dd style={{ margin: 0 }} className="verbatim">
              {material.context}
            </dd>
          </div>
        )}
        <div className="field">
          <dt className="muted small">保留原话</dt>
          <dd style={{ margin: 0 }}>{material.preserve_verbatim ? '是' : '否'}</dd>
        </div>
      </dl>

      <hr className="divider" />
      <p className="muted small">
        镜像确认、关键词语义确认与进入正式思考地图的准入尚未接入后端，
        本条素材当前仅供回看。
      </p>
    </article>
  );
}
