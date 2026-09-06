/**
 * 来源登记：只登记元信息，不抓取全文，不表示共鸣或认同。
 * 来源命题可在创建时一并登记，区分「作者明确表达」与「协作者归纳」。
 */
import { useState } from 'react';
import { ApiError } from '../../api/client';
import { createSource } from '../../api/endpoints';
import type { Source, SourceKind, PropositionAttribution } from '../../api/types';
import {
  buildSourcePayload,
  validateSourceDraft,
  type SourceDraft,
} from '../../lib/payloads';
import { ATTRIBUTION_LABELS, SOURCE_KIND_LABELS } from '../../lib/labels';

interface SourceFormProps {
  onCreated: (source: Source) => void;
  onDirtyChange: (dirty: boolean) => void;
}

const EMPTY_DRAFT: SourceDraft = {
  kind: 'web_article',
  originalUrl: '',
  title: '',
  platform: '',
  canonicalUrl: '',
  creator: '',
  publisher: '',
  publishedAt: '',
  language: '',
  topics: '',
  propositions: [],
};

export default function SourceForm({ onCreated, onDirtyChange }: SourceFormProps) {
  const [draft, setDraft] = useState<SourceDraft>(EMPTY_DRAFT);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [localError, setLocalError] = useState<string | null>(null);

  const update = (patch: Partial<SourceDraft>) => {
    setDraft((previous) => {
      const next = { ...previous, ...patch };
      onDirtyChange(
        next.title.trim().length > 0 || next.originalUrl.trim().length > 0,
      );
      return next;
    });
  };

  const updateProposition = (
    index: number,
    patch: Partial<{ text: string; attribution: PropositionAttribution }>,
  ) => {
    const propositions = draft.propositions.map((item, i) =>
      i === index ? { ...item, ...patch } : item,
    );
    update({ propositions });
  };

  const submit = async () => {
    if (saving) return;
    const validation = validateSourceDraft(draft);
    if (!validation.ok) {
      setLocalError(validation.message ?? '登记信息不完整。');
      return;
    }
    setLocalError(null);
    setError(null);
    setSaving(true);
    try {
      const source = await createSource(buildSourcePayload(draft));
      setDraft(EMPTY_DRAFT);
      onDirtyChange(false);
      onCreated(source);
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
      <div className="field">
        <label htmlFor="source-kind">种类（必选）</label>
        <select
          id="source-kind"
          value={draft.kind}
          disabled={saving}
          onChange={(event) =>
            update({ kind: event.target.value as SourceKind })
          }
        >
          {Object.entries(SOURCE_KIND_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
      </div>
      <div className="field">
        <label htmlFor="source-url">原始链接（必选，HTTP/HTTPS）</label>
        <input
          id="source-url"
          type="url"
          value={draft.originalUrl}
          disabled={saving}
          placeholder="https://example.com/article"
          onChange={(event) => update({ originalUrl: event.target.value })}
        />
        <p className="field-hint">
          即使是书籍或对话，当前后端也要求有效链接；无链接来源的登记是后端缺口。
        </p>
      </div>
      <div className="field">
        <label htmlFor="source-title">标题（必选）</label>
        <input
          id="source-title"
          type="text"
          value={draft.title}
          disabled={saving}
          onChange={(event) => update({ title: event.target.value })}
        />
      </div>

      <details className="disclosure">
        <summary>更多信息（作者、平台、出版信息、主题）</summary>
        <div className="field">
          <label htmlFor="source-creator">作者</label>
          <input
            id="source-creator"
            type="text"
            value={draft.creator}
            disabled={saving}
            placeholder="不知道就留空，显示为「作者未记录」"
            onChange={(event) => update({ creator: event.target.value })}
          />
        </div>
        <div className="field">
          <label htmlFor="source-platform">平台</label>
          <input
            id="source-platform"
            type="text"
            value={draft.platform}
            disabled={saving}
            onChange={(event) => update({ platform: event.target.value })}
          />
        </div>
        <div className="field">
          <label htmlFor="source-publisher">出版方</label>
          <input
            id="source-publisher"
            type="text"
            value={draft.publisher}
            disabled={saving}
            onChange={(event) => update({ publisher: event.target.value })}
          />
        </div>
        <div className="field">
          <label htmlFor="source-published">出版时间（自由文本，如 2024 年春）</label>
          <input
            id="source-published"
            type="text"
            value={draft.publishedAt}
            disabled={saving}
            onChange={(event) => update({ publishedAt: event.target.value })}
          />
        </div>
        <div className="field">
          <label htmlFor="source-language">语言</label>
          <input
            id="source-language"
            type="text"
            value={draft.language}
            disabled={saving}
            placeholder="如 zh、en"
            onChange={(event) => update({ language: event.target.value })}
          />
        </div>
        <div className="field">
          <label htmlFor="source-topics">主题（逗号分隔）</label>
          <input
            id="source-topics"
            type="text"
            value={draft.topics}
            disabled={saving}
            onChange={(event) => update({ topics: event.target.value })}
          />
        </div>
        <div className="field">
          <label htmlFor="source-canonical">规范链接（可选）</label>
          <input
            id="source-canonical"
            type="url"
            value={draft.canonicalUrl}
            disabled={saving}
            onChange={(event) => update({ canonicalUrl: event.target.value })}
          />
        </div>
      </details>

      <h3>来源命题（可选，创建后不可修改）</h3>
      <p className="muted small">
        逐条登记来源中的命题，并标明归属。登记不代表你认同它。
      </p>
      {draft.propositions.map((proposition, index) => (
        <div
          key={index}
          style={{
            borderLeft: '2px solid var(--color-border)',
            paddingLeft: 'var(--space-4)',
            marginBottom: 'var(--space-4)',
          }}
        >
          <div className="field">
            <label htmlFor={`prop-text-${index}`}>命题 {index + 1} 正文</label>
            <textarea
              id={`prop-text-${index}`}
              rows={2}
              value={proposition.text}
              disabled={saving}
              onChange={(event) =>
                updateProposition(index, { text: event.target.value })
              }
            />
          </div>
          <div className="field">
            <label htmlFor={`prop-attr-${index}`}>归属</label>
            <select
              id={`prop-attr-${index}`}
              value={proposition.attribution}
              disabled={saving}
              onChange={(event) =>
                updateProposition(index, {
                  attribution: event.target.value as PropositionAttribution,
                })
              }
            >
              {Object.entries(ATTRIBUTION_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>
          <button
            type="button"
            className="button button--secondary"
            disabled={saving}
            onClick={() =>
              update({
                propositions: draft.propositions.filter((_, i) => i !== index),
              })
            }
          >
            移除这条命题
          </button>
        </div>
      ))}
      <p>
        <button
          type="button"
          className="button button--secondary"
          disabled={saving}
          onClick={() =>
            update({
              propositions: [
                ...draft.propositions,
                { text: '', attribution: 'collaborator_summary' },
              ],
            })
          }
        >
          添加来源命题
        </button>
      </p>

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
              ? '为避免重复登记，本次没有自动重发，请先到列表核对。'
              : ''}
          </p>
        </div>
      )}

      <div className="button-row">
        <button type="submit" className="button" disabled={saving}>
          {saving ? '登记中…' : '登记来源'}
        </button>
      </div>
      <p className="muted small">
        登记只保存元信息，不抓取全文，不产生个人素材，也不表示共鸣或认同。
      </p>
    </form>
  );
}
