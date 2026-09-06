/**
 * 观点页：浏览个人命题；「记录自己的命题」仅接受用户主动写下的内容。
 * 来自来源的采用统一走回应流程（POST /responses），不在这里代建。
 */
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { ApiError } from '../../api/client';
import {
  createPersonalProposition,
  listPersonalPropositions,
} from '../../api/endpoints';
import { useLoad } from '../../lib/useLoad';
import { formatDate } from '../../lib/time';
import { EmptyView, ErrorView, LoadingView } from '../../components/StatusView';

export default function PropositionsPage() {
  const { state, reload } = useLoad(listPersonalPropositions);
  const [formOpen, setFormOpen] = useState(false);
  const [text, setText] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async () => {
    if (saving) return;
    if (text.trim().length === 0) {
      setError('命题正文不能为空。');
      return;
    }
    setError(null);
    setSaving(true);
    try {
      await createPersonalProposition({ text });
      setText('');
      setFormOpen(false);
      reload();
    } catch (err) {
      setError(
        err instanceof ApiError
          ? `${err.message} 输入内容已保留。`
          : '出现未预期的错误，输入内容已保留。',
      );
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <h1>观点</h1>
      <p className="muted">
        你的个人命题。来自来源的命题请在来源详情中通过「回应这个命题」明确采用后进入这里。
      </p>

      <p>
        <button
          type="button"
          className="button button--secondary"
          aria-expanded={formOpen}
          onClick={() => setFormOpen((open) => !open)}
        >
          {formOpen ? '收起' : '记录自己的命题'}
        </button>
      </p>

      {formOpen && (
        <form
          onSubmit={(event) => {
            event.preventDefault();
            void submit();
          }}
          style={{ maxWidth: 560 }}
        >
          <div className="field">
            <label htmlFor="proposition-text">命题正文</label>
            <textarea
              id="proposition-text"
              rows={3}
              value={text}
              disabled={saving}
              placeholder="直接写下你的判断，例如：……"
              onChange={(event) => setText(event.target.value)}
            />
            <p className="field-hint">
              默认保存为私人。这里只记录你主动写下的命题，不表示语义已被系统确认。
            </p>
          </div>
          {error && (
            <div className="notice notice--error" role="alert">
              {error}
            </div>
          )}
          <div className="button-row">
            <button type="submit" className="button" disabled={saving}>
              {saving ? '保存中…' : '保存命题'}
            </button>
          </div>
        </form>
      )}

      {state.status === 'loading' && <LoadingView text="正在读取命题…" />}
      {state.status === 'error' && <ErrorView error={state.error} onRetry={reload} />}
      {state.status === 'success' &&
        (state.data.length === 0 ? (
          <EmptyView>
            <p style={{ margin: 0 }}>
              还没有个人命题。可以在上方直接记录，或在来源中明确采用一条来源命题。
            </p>
          </EmptyView>
        ) : (
          <ul className="record-list">
            {[...state.data].reverse().map((proposition) => (
              <li key={proposition.id}>
                <Link to={`/responses?target=${encodeURIComponent(proposition.id)}`}>
                  <span className="excerpt verbatim">{proposition.text}</span>
                </Link>
                <p className="meta-line">
                  {proposition.id} · 记录于 {formatDate(proposition.created_at)}
                  {proposition.origin_source_proposition_id
                    ? ` · 采用自 ${proposition.origin_source_proposition_id}`
                    : ''}
                </p>
              </li>
            ))}
          </ul>
        ))}
    </div>
  );
}
