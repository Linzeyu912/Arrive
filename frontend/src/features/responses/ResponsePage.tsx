/**
 * 命题回应页：/responses?target=<P001 或 SRC-0001/P01>
 * 展示命题正文与归属、截至某时间的三轴摘要（服务端计算）、追加历史。
 */
import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { ApiError } from '../../api/client';
import {
  getResponseTimeline,
  getSource,
  getStanceSnapshot,
  listPersonalPropositions,
} from '../../api/endpoints';
import type {
  AxisSnapshot,
  ResponseEvent,
  StanceSnapshot,
} from '../../api/types';
import { formatDateTime, localInputToIso } from '../../lib/time';
import {
  ADOPTION_LABELS,
  AGREEMENT_LABELS,
  ATTRIBUTION_LABELS,
  CONFIDENCE_LABELS,
  RESONANCE_LABELS,
  TIME_PRECISION_LABELS,
} from '../../lib/labels';
import { EmptyView, ErrorView, LoadingView } from '../../components/StatusView';
import ResponseForm from './ResponseForm';

interface TargetInfo {
  id: string;
  text: string;
  description: string;
}

type TargetState =
  | { status: 'loading' }
  | { status: 'error'; error: unknown }
  | { status: 'ready'; target: TargetInfo };

async function resolveTarget(targetId: string): Promise<TargetInfo> {
  if (/^P\d{3,}$/.test(targetId)) {
    const propositions = await listPersonalPropositions();
    const found = propositions.find((item) => item.id === targetId);
    if (!found) {
      throw new ApiError('not_found', `没有找到个人命题 ${targetId}。`);
    }
    const origin = found.origin_source_proposition_id
      ? `采用自来源命题 ${found.origin_source_proposition_id}`
      : '由你直接记录';
    return { id: found.id, text: found.text, description: `个人命题 · ${origin}` };
  }
  const sourceMatch = /^(SRC-\d{4,})\/P\d{2,}$/.exec(targetId);
  if (sourceMatch) {
    const source = await getSource(sourceMatch[1]);
    const found = source.propositions.find((item) => item.id === targetId);
    if (!found) {
      throw new ApiError('not_found', `来源 ${source.id} 中没有命题 ${targetId}。`);
    }
    return {
      id: found.id,
      text: found.text,
      description: `来源命题 · ${ATTRIBUTION_LABELS[found.attribution]} · 出自《${source.title}》（${source.id}）`,
    };
  }
  throw new ApiError(
    'validation',
    '回应目标只能是个人命题（如 P001）或来源命题（如 SRC-0001/P01），不能直接回应素材或来源本身。',
  );
}

function AxisView({
  label,
  axis,
  valueLabels,
}: {
  label: string;
  axis: AxisSnapshot;
  valueLabels: Record<string, string>;
}) {
  return (
    <div className="field">
      <dt className="muted small">{label}</dt>
      <dd style={{ margin: 0 }}>
        {valueLabels[axis.value] ?? axis.value}
        {axis.event_id && (
          <span className="muted small">
            {' '}
            （来自 {axis.event_id}
            {axis.effective_at ? ` · 生效于 ${formatDateTime(axis.effective_at)}` : ''}）
          </span>
        )}
      </dd>
    </div>
  );
}

export default function ResponsePage() {
  const [searchParams] = useSearchParams();
  const targetId = searchParams.get('target') ?? '';

  const [targetState, setTargetState] = useState<TargetState>({ status: 'loading' });
  const [timeline, setTimeline] = useState<ResponseEvent[] | null>(null);
  const [snapshot, setSnapshot] = useState<StanceSnapshot | null>(null);
  const [loadError, setLoadError] = useState<unknown>(null);
  const [asOfInput, setAsOfInput] = useState('');
  const [asOfError, setAsOfError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setTargetState({ status: 'loading' });
    setTimeline(null);
    setSnapshot(null);
    setLoadError(null);
    if (!targetId) {
      setTargetState({ status: 'loading' });
      return;
    }
    (async () => {
      try {
        const target = await resolveTarget(targetId);
        const asOfIso = asOfInput ? localInputToIso(asOfInput) : undefined;
        const [events, snap] = await Promise.all([
          getResponseTimeline(targetId),
          getStanceSnapshot(targetId, asOfIso ?? undefined),
        ]);
        if (cancelled) return;
        setTargetState({ status: 'ready', target });
        setTimeline(events);
        setSnapshot(snap);
      } catch (error) {
        if (cancelled) return;
        if (error instanceof ApiError && error.kind !== 'not_found') {
          setTargetState({ status: 'error', error });
        } else {
          setTargetState({ status: 'error', error });
        }
        setLoadError(error);
      }
    })();
    return () => {
      cancelled = true;
    };
    // asOfInput 变化不自动刷新，由用户点击「按此时间汇总」
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [targetId, reloadKey]);

  const applyAsOf = () => {
    if (asOfInput && !localInputToIso(asOfInput)) {
      setAsOfError('请输入有效的汇总时间。');
      return;
    }
    setAsOfError(null);
    setReloadKey((key) => key + 1);
  };

  if (!targetId) {
    return (
      <div>
        <h1>命题回应</h1>
        <EmptyView>
          <p style={{ margin: 0 }}>
            请从<Link to="/propositions">观点</Link>或
            <Link to="/sources">来源</Link>中选择一条命题进入。
          </p>
        </EmptyView>
      </div>
    );
  }

  if (targetState.status === 'loading') {
    return <LoadingView text="正在读取命题与回应历史…" />;
  }
  if (targetState.status === 'error') {
    return (
      <div>
        <h1>命题回应</h1>
        <ErrorView
          error={loadError ?? targetState.error}
          onRetry={() => setReloadKey((key) => key + 1)}
        />
        <p>
          <Link to="/propositions">返回观点</Link>
        </p>
      </div>
    );
  }

  const { target } = targetState;

  return (
    <div>
      <p className="meta-line">
        <Link to="/propositions">← 观点</Link>
      </p>
      <h1 style={{ fontSize: '1.25rem' }}>{target.id}</h1>
      <p className="verbatim" style={{ fontSize: '1.05rem' }}>
        {target.text}
      </p>
      <p className="meta-line">{target.description}</p>

      <h2>当前摘要</h2>
      <div className="field" style={{ maxWidth: 320 }}>
        <label htmlFor="as-of">汇总截至（留空为现在）</label>
        <input
          id="as-of"
          type="datetime-local"
          value={asOfInput}
          onChange={(event) => setAsOfInput(event.target.value)}
        />
      </div>
      <p>
        <button
          type="button"
          className="button button--secondary"
          onClick={applyAsOf}
        >
          按此时间汇总
        </button>
      </p>
      {asOfError && (
        <div className="notice notice--error" role="alert">
          {asOfError}
        </div>
      )}
      {snapshot && (
        <>
          <dl style={{ margin: 0 }}>
            <AxisView
              label="共鸣"
              axis={snapshot.resonance}
              valueLabels={RESONANCE_LABELS}
            />
            <AxisView
              label="认同"
              axis={snapshot.agreement}
              valueLabels={AGREEMENT_LABELS}
            />
            <AxisView
              label="采用"
              axis={snapshot.adoption}
              valueLabels={ADOPTION_LABELS}
            />
          </dl>
          <p className="muted small">
            按生效时间汇总 · as_of {formatDateTime(snapshot.as_of)} · 共{' '}
            {snapshot.event_count} 条事件。「未说明 / 尚未决定」不会清空此前已表达的轴；
            该摘要是回看该时间的生效状态，不是当时系统已知状态的完整版本。
          </p>
        </>
      )}

      <h2>回应历史（追加式）</h2>
      {timeline && timeline.length === 0 && (
        <EmptyView>
          <p style={{ margin: 0 }}>还没有回应记录。</p>
        </EmptyView>
      )}
      {timeline && timeline.length > 0 && (
        <ul className="record-list">
          {timeline.map((event) => (
            <li key={event.id}>
              <p style={{ margin: 0 }}>
                {event.id} · 共鸣「{RESONANCE_LABELS[event.resonance]}」 · 认同「
                {AGREEMENT_LABELS[event.agreement]}」 · 采用「
                {ADOPTION_LABELS[event.adoption]}」 · 信心「
                {CONFIDENCE_LABELS[event.confidence]}」
              </p>
              {event.original_words && (
                <p className="verbatim" style={{ margin: '4px 0 0' }}>
                  {event.original_words}
                </p>
              )}
              <p className="meta-line">
                生效于 {formatDateTime(event.effective_at)}（
                {TIME_PRECISION_LABELS[event.time_precision]}）· 录入于{' '}
                {formatDateTime(event.recorded_at)}
                {event.context ? ` · 情境：${event.context}` : ''}
                {event.supersedes ? ` · 替代 ${event.supersedes}` : ''}
                {event.creates_personal_proposition_id
                  ? ` · 同步创建个人命题 ${event.creates_personal_proposition_id}`
                  : ''}
              </p>
            </li>
          ))}
        </ul>
      )}

      <h2>记录一次回应</h2>
      <ResponseForm
        key={`${target.id}-${timeline?.length ?? 0}`}
        targetId={target.id}
        targetText={target.text}
        history={timeline ?? []}
        onCreated={() => setReloadKey((key) => key + 1)}
      />
    </div>
  );
}
