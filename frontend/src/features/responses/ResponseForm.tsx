/**
 * 「记录一次回应」表单。
 * - 共鸣 / 认同 / 采用三组选择互不联动，不做任何自动推断。
 * - 信心默认后端值 medium，界面可见可改。
 * - 时间仅支持「这是我现在的回应」或明确的过去时间；不能用虚构日期表示未知。
 * - 只有采用/调整后采用 + 明确勾选 + 确认正文，才携带 creates_personal_proposition_text。
 * - supersedes 只列出同一目标的历史事件，默认不替代。
 */
import { useState } from 'react';
import { ApiError } from '../../api/client';
import { createResponseEvent } from '../../api/endpoints';
import type {
  Adoption,
  Agreement,
  Confidence,
  Resonance,
  ResponseEvent,
} from '../../api/types';
import {
  buildResponsePayload,
  validateResponseDraft,
  type ResponseDraft,
} from '../../lib/payloads';
import { localInputToIso } from '../../lib/time';
import {
  ADOPTION_LABELS,
  AGREEMENT_LABELS,
  CONFIDENCE_LABELS,
  RESONANCE_LABELS,
} from '../../lib/labels';

interface ResponseFormProps {
  targetId: string;
  targetText: string;
  history: ResponseEvent[];
  onCreated: (event: ResponseEvent) => void;
}

function AxisGroup<T extends string>({
  name,
  legend,
  hint,
  value,
  labels,
  disabled,
  onChange,
}: {
  name: string;
  legend: string;
  hint: string;
  value: T;
  labels: Record<T, string>;
  disabled: boolean;
  onChange: (value: T) => void;
}) {
  return (
    <fieldset
      style={{
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius-control)',
        padding: 'var(--space-3) var(--space-4)',
        margin: '0 0 var(--space-4)',
      }}
    >
      <legend style={{ padding: '0 var(--space-2)' }}>{legend}</legend>
      <p className="muted small" style={{ margin: '0 0 var(--space-2)' }}>
        {hint}
      </p>
      <div role="radiogroup" aria-label={legend}>
        {(Object.keys(labels) as T[]).map((option) => (
          <label
            key={option}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              marginRight: 16,
              marginBottom: 6,
              minHeight: 32,
              color: 'var(--color-text)',
              fontSize: '0.95rem',
            }}
          >
            <input
              type="radio"
              name={name}
              value={option}
              checked={value === option}
              disabled={disabled}
              onChange={() => onChange(option)}
            />
            {labels[option]}
          </label>
        ))}
      </div>
    </fieldset>
  );
}

export default function ResponseForm({
  targetId,
  targetText,
  history,
  onCreated,
}: ResponseFormProps) {
  const [draft, setDraft] = useState<ResponseDraft>({
    targetId,
    resonance: 'unspecified',
    agreement: 'unspecified',
    adoption: 'undecided',
    confidence: 'medium',
    originalWords: '',
    context: '',
    effectiveAtIso: null,
    supersedes: '',
    alsoCreatePersonalProposition: false,
    personalPropositionText: '',
    personalPropositionPrivacy: 'private',
  });
  const [timeMode, setTimeMode] = useState<'now' | 'past'>('now');
  const [pastInput, setPastInput] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [localError, setLocalError] = useState<string | null>(null);

  const adoptionCreates = draft.adoption === 'adopt' || draft.adoption === 'adapt';

  const update = (patch: Partial<ResponseDraft>) =>
    setDraft((previous) => ({ ...previous, ...patch }));

  const submit = async () => {
    if (saving) return;
    const effectiveAtIso =
      timeMode === 'past' ? localInputToIso(pastInput) : null;
    if (timeMode === 'past' && !effectiveAtIso) {
      setLocalError('请填写有效的过去时间，或选择「这是我现在的回应」。');
      return;
    }
    const nextDraft: ResponseDraft = { ...draft, effectiveAtIso };
    const validation = validateResponseDraft(nextDraft);
    if (!validation.ok) {
      setLocalError(validation.message ?? '回应内容不完整。');
      return;
    }
    setLocalError(null);
    setError(null);
    setSaving(true);
    try {
      const event = await createResponseEvent(buildResponsePayload(nextDraft));
      onCreated(event);
      setDraft((previous) => ({
        ...previous,
        resonance: 'unspecified',
        agreement: 'unspecified',
        adoption: 'undecided',
        originalWords: '',
        context: '',
        supersedes: '',
        alsoCreatePersonalProposition: false,
        personalPropositionText: '',
      }));
      setTimeMode('now');
      setPastInput('');
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err);
      } else {
        setError(new ApiError('unknown', '出现未预期的错误，表单内容已保留。'));
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        void submit();
      }}
    >
      <AxisGroup<Resonance>
        name="resonance"
        legend="共鸣"
        hint="是否被表达、情绪或经验打动。与认同、采用互不影响。"
        value={draft.resonance}
        labels={RESONANCE_LABELS}
        disabled={saving}
        onChange={(resonance) => update({ resonance })}
      />
      <AxisGroup<Agreement>
        name="agreement"
        legend="认同"
        hint="是否接受命题本身。选了共鸣强不会自动认同。"
        value={draft.agreement}
        labels={AGREEMENT_LABELS}
        disabled={saving}
        onChange={(agreement) => update({ agreement })}
      />
      <AxisGroup<Adoption>
        name="adoption"
        legend="采用"
        hint="是否愿意纳入自己的思考或表达。选择采用也不会自动推断共鸣或认同。"
        value={draft.adoption}
        labels={ADOPTION_LABELS}
        disabled={saving}
        onChange={(adoption) => update({ adoption })}
      />

      <div className="field">
        <label htmlFor="response-confidence">这次判断的信心（默认「中」，可改）</label>
        <select
          id="response-confidence"
          value={draft.confidence}
          disabled={saving}
          onChange={(event) =>
            update({ confidence: event.target.value as Confidence })
          }
        >
          {Object.entries(CONFIDENCE_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
        <p className="field-hint">由你标记，不代表系统判断。</p>
      </div>

      <fieldset
        style={{
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-control)',
          padding: 'var(--space-3) var(--space-4)',
          margin: '0 0 var(--space-4)',
        }}
      >
        <legend style={{ padding: '0 var(--space-2)' }}>这次回应属于何时</legend>
        <label
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            color: 'var(--color-text)',
            fontSize: '0.95rem',
            minHeight: 32,
          }}
        >
          <input
            type="radio"
            name="response-time-mode"
            checked={timeMode === 'now'}
            disabled={saving}
            onChange={() => setTimeMode('now')}
          />
          这是我现在的回应
        </label>
        <label
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            color: 'var(--color-text)',
            fontSize: '0.95rem',
            minHeight: 32,
          }}
        >
          <input
            type="radio"
            name="response-time-mode"
            checked={timeMode === 'past'}
            disabled={saving}
            onChange={() => setTimeMode('past')}
          />
          属于一个明确的过去时间
        </label>
        {timeMode === 'past' && (
          <div className="field" style={{ marginTop: 8 }}>
            <label htmlFor="response-past-time">过去时间（按你本机时区）</label>
            <input
              id="response-past-time"
              type="datetime-local"
              value={pastInput}
              disabled={saving}
              onChange={(event) => setPastInput(event.target.value)}
            />
          </div>
        )}
        <p className="field-hint">
          「只记得大概年份」这类模糊时间当前后端契约还不支持，需要等后端完善时间语义。
        </p>
      </fieldset>

      <div className="field">
        <label htmlFor="response-words">补充你的原话（可选）</label>
        <textarea
          id="response-words"
          rows={3}
          value={draft.originalWords}
          disabled={saving}
          placeholder="这次回应里你想保留下来的说法"
          onChange={(event) => update({ originalWords: event.target.value })}
        />
      </div>
      <div className="field">
        <label htmlFor="response-context">适用情境（可选）</label>
        <input
          id="response-context"
          type="text"
          value={draft.context}
          disabled={saving}
          placeholder="例如：只适用于工作场合"
          onChange={(event) => update({ context: event.target.value })}
        />
      </div>

      {history.length > 0 && (
        <div className="field">
          <label htmlFor="response-supersedes">替代哪一条旧判断（默认不替代）</label>
          <select
            id="response-supersedes"
            value={draft.supersedes}
            disabled={saving}
            onChange={(event) => update({ supersedes: event.target.value })}
          >
            <option value="">不替代任何旧判断（默认）</option>
            {history.map((event) => (
              <option key={event.id} value={event.id}>
                {event.id}（{event.effective_at.slice(0, 10)}）
              </option>
            ))}
          </select>
          <p className="field-hint">
            只有明确替代同一适用范围内的旧判断时才选择；历史事件不会被删除。
          </p>
        </div>
      )}

      {adoptionCreates && (
        <div
          style={{
            border: '1px solid var(--color-accent)',
            borderRadius: 'var(--radius-control)',
            padding: 'var(--space-4)',
            marginBottom: 'var(--space-4)',
            background: 'var(--color-accent-soft)',
          }}
        >
          <div className="checkbox-row">
            <input
              id="response-create-pp"
              type="checkbox"
              checked={draft.alsoCreatePersonalProposition}
              disabled={saving}
              onChange={(event) =>
                update({ alsoCreatePersonalProposition: event.target.checked })
              }
            />
            <span>
              <label htmlFor="response-create-pp" style={{ display: 'inline' }}>
                同时记录为我的命题
              </label>
              <span className="muted small">
                {' '}
                勾选后，本次回应会通过一次请求同步创建一条个人命题，保留来源归属。
              </span>
            </span>
          </div>
          {draft.alsoCreatePersonalProposition && (
            <div className="field">
              <label htmlFor="response-pp-text">确认命题正文</label>
              <textarea
                id="response-pp-text"
                rows={2}
                value={draft.personalPropositionText}
                disabled={saving}
                placeholder={targetText}
                onChange={(event) =>
                  update({ personalPropositionText: event.target.value })
                }
              />
              <p className="field-hint">
                采用时可以保持原文；调整后采用请在这里写出你的版本。
              </p>
            </div>
          )}
        </div>
      )}

      {localError && (
        <div className="notice notice--error" role="alert">
          {localError}
        </div>
      )}
      {error && (
        <div className="notice notice--error" role="alert">
          <p style={{ margin: 0 }}>{error.message}</p>
          {error.fieldErrors.length > 0 && (
            <ul style={{ margin: '8px 0 0' }}>
              {error.fieldErrors.map((item, index) => (
                <li key={index}>
                  {item.field}：{item.message}
                </li>
              ))}
            </ul>
          )}
          <p className="small" style={{ margin: '8px 0 0' }}>
            表单内容已保留。
            {error.kind === 'timeout' || error.kind === 'network'
              ? '回应可能已经写入，本次没有自动重发，请先查看下方历史核对。'
              : ''}
          </p>
        </div>
      )}

      <div className="button-row">
        <button type="submit" className="button" disabled={saving}>
          {saving ? '保存中…' : '追加这次回应'}
        </button>
      </div>
      <p className="muted small">
        回应只会追加，不能覆盖或删除历史。保存成功以后端返回为准。
      </p>
    </form>
  );
}
