/**
 * 记录页：第一优先级。
 * - 保存成功只依据后端 201 与返回记录；不用计时器模拟成功。
 * - Ctrl/Cmd+Enter 保存；中文输入法组合输入期间不触发。
 * - 提交期间锁定输入防重复；超时/网络失败不自动重发，保留输入供核对。
 * - 未保存输入只是内存草稿，站内导航与关闭前提示，不承诺跨刷新恢复。
 */
import { useCallback, useEffect, useRef, useState } from 'react';
import { Link, useBlocker } from 'react-router-dom';
import { ApiError } from '../../api/client';
import { createMaterial } from '../../api/endpoints';
import type { Material, MaterialKind, Privacy } from '../../api/types';
import {
  buildMaterialPayload,
  validateMaterialDraft,
  type MaterialDraft,
} from '../../lib/payloads';
import { formatDateTime } from '../../lib/time';
import {
  MATERIAL_KIND_LABELS,
  PRIVACY_LABELS,
} from '../../lib/labels';

type SaveState =
  | { status: 'idle' }
  | { status: 'saving' }
  | { status: 'saved'; material: Material }
  | { status: 'failed'; message: string; fieldErrors: { field: string; message: string }[] }
  | { status: 'unknown'; message: string };

const isCoarsePointer = () =>
  typeof window !== 'undefined' &&
  window.matchMedia?.('(pointer: coarse)').matches === true;

export default function RecordPage() {
  const [draft, setDraft] = useState<MaterialDraft>({
    kind: 'thought',
    content: '',
    privacy: 'private',
    preserveVerbatim: true,
    context: '',
  });
  const [saveState, setSaveState] = useState<SaveState>({ status: 'idle' });
  const [receipts, setReceipts] = useState<Material[]>([]);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const composingRef = useRef(false);
  const requestSeq = useRef(0);

  const dirty = draft.content.trim().length > 0;

  // 桌面端默认聚焦；移动端不自动弹出键盘
  useEffect(() => {
    if (!isCoarsePointer()) textareaRef.current?.focus();
  }, []);

  // 站内导航拦截 + 关闭/刷新提示
  const blocker = useBlocker(dirty && saveState.status !== 'saved');
  useEffect(() => {
    if (!dirty) return;
    const handler = (event: BeforeUnloadEvent) => {
      event.preventDefault();
    };
    window.addEventListener('beforeunload', handler);
    return () => window.removeEventListener('beforeunload', handler);
  }, [dirty]);

  const save = useCallback(async () => {
    if (saveState.status === 'saving') return;
    const validation = validateMaterialDraft(draft);
    if (!validation.ok) {
      setSaveState({
        status: 'failed',
        message: validation.message ?? '内容不符合要求。',
        fieldErrors: [],
      });
      return;
    }
    const payload = buildMaterialPayload(draft);
    const seq = ++requestSeq.current;
    setSaveState({ status: 'saving' });
    try {
      const material = await createMaterial(payload);
      if (seq !== requestSeq.current) return;
      setReceipts((previous) => [material, ...previous]);
      setDraft((previous) => ({ ...previous, content: '' }));
      setSaveState({ status: 'saved', material });
      textareaRef.current?.focus();
    } catch (error) {
      if (seq !== requestSeq.current) return;
      if (error instanceof ApiError) {
        if (error.kind === 'timeout' || error.kind === 'network') {
          // 写入可能已完成：不自动重试，保留输入，提示人工核对
          setSaveState({ status: 'unknown', message: error.message });
        } else {
          setSaveState({
            status: 'failed',
            message: error.message,
            fieldErrors: error.fieldErrors,
          });
        }
      } else {
        setSaveState({
          status: 'failed',
          message: '出现未预期的错误，输入内容仍保留在输入框中。',
          fieldErrors: [],
        });
      }
    }
  }, [draft, saveState.status]);

  const onKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (
      event.key === 'Enter' &&
      (event.ctrlKey || event.metaKey) &&
      !composingRef.current &&
      !event.nativeEvent.isComposing
    ) {
      event.preventDefault();
      void save();
    }
  };

  const saving = saveState.status === 'saving';

  return (
    <div>
      <h1>先把此刻想说的放在这里。</h1>
      <p className="muted">零碎也可以，不用先整理。</p>

      <form
        onSubmit={(event) => {
          event.preventDefault();
          void save();
        }}
      >
        <div className="field">
          <label htmlFor="record-content">原话</label>
          <textarea
            id="record-content"
            ref={textareaRef}
            value={draft.content}
            placeholder="写下一句话，或一段想法……"
            rows={6}
            disabled={saving}
            style={{ borderRadius: 'var(--radius-input)' }}
            onChange={(event) =>
              setDraft((previous) => ({ ...previous, content: event.target.value }))
            }
            onKeyDown={onKeyDown}
            onCompositionStart={() => {
              composingRef.current = true;
            }}
            onCompositionEnd={() => {
              composingRef.current = false;
            }}
          />
          <p className="field-hint">
            Enter 换行，Ctrl/⌘+Enter 保存。内容原样保存，界面不会改写原文。
          </p>
        </div>

        <details className="disclosure">
          <summary>更多选项（类型、隐私、上下文）</summary>
          <div className="field">
            <label htmlFor="record-kind">内容类型</label>
            <select
              id="record-kind"
              value={draft.kind}
              disabled={saving}
              onChange={(event) =>
                setDraft((previous) => ({
                  ...previous,
                  kind: event.target.value as MaterialKind,
                }))
              }
            >
              {Object.entries(MATERIAL_KIND_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="record-privacy">隐私状态</label>
            <select
              id="record-privacy"
              value={draft.privacy}
              disabled={saving}
              onChange={(event) =>
                setDraft((previous) => ({
                  ...previous,
                  privacy: event.target.value as Privacy,
                }))
              }
            >
              {Object.entries(PRIVACY_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
            <p className="field-hint">
              隐私标签是数据状态，不代表访问权限或加密；当前服务仅供本地使用。
            </p>
          </div>
          <div className="field">
            <label htmlFor="record-context">上下文（可选）</label>
            <input
              id="record-context"
              type="text"
              value={draft.context}
              disabled={saving}
              placeholder="例如：通勤路上想到的"
              onChange={(event) =>
                setDraft((previous) => ({ ...previous, context: event.target.value }))
              }
            />
          </div>
          <div className="checkbox-row">
            <input
              id="record-verbatim"
              type="checkbox"
              checked={draft.preserveVerbatim}
              disabled={saving}
              onChange={(event) =>
                setDraft((previous) => ({
                  ...previous,
                  preserveVerbatim: event.target.checked,
                }))
              }
            />
            <span>
              <label htmlFor="record-verbatim" style={{ display: 'inline' }}>
                保留原话
              </label>
              <span className="muted small">
                {' '}
                标记这段内容在后续表达中不做风格改写。
              </span>
            </span>
          </div>
        </details>

        {saveState.status === 'failed' && (
          <div className="notice notice--error" role="alert">
            <p style={{ margin: 0 }}>{saveState.message}</p>
            {saveState.fieldErrors.length > 0 && (
              <ul style={{ margin: '8px 0 0' }}>
                {saveState.fieldErrors.map((item, index) => (
                  <li key={index}>
                    {item.field}：{item.message}
                  </li>
                ))}
              </ul>
            )}
            <p className="small" style={{ margin: '8px 0 0' }}>
              输入内容仍保留在输入框中。
            </p>
          </div>
        )}
        {saveState.status === 'unknown' && (
          <div className="notice notice--error" role="alert">
            <p style={{ margin: 0 }}>
              暂时无法确认是否已保存。{saveState.message}
            </p>
            <p className="small" style={{ margin: '8px 0 0' }}>
              为避免重复写入，本次没有自动重发。可以先到
              <Link to="/materials">素材列表</Link>
              按内容和时间人工核对，确认未保存后再提交。
            </p>
          </div>
        )}

        <div className="button-row">
          <button type="submit" className="button" disabled={saving || !dirty}>
            {saving ? '保存中…' : '保存'}
          </button>
          <span className="muted small">
            默认保存为「想法 · 私人 · 保留原话」
          </span>
        </div>
      </form>

      {blocker.state === 'blocked' && (
        <div className="notice" role="alertdialog" aria-label="未保存的输入">
          <p style={{ margin: 0 }}>输入框里还有未保存的内容，离开后将丢失。</p>
          <div className="button-row" style={{ marginTop: 8 }}>
            <button
              type="button"
              className="button"
              onClick={() => blocker.proceed?.()}
            >
              离开本页
            </button>
            <button
              type="button"
              className="button button--secondary"
              onClick={() => blocker.reset?.()}
            >
              继续编辑
            </button>
          </div>
        </div>
      )}

      {receipts.length > 0 && (
        <>
          <h2>本次已保存</h2>
          <ul className="record-list">
            {receipts.map((material) => (
              <li key={material.id}>
                <p className="notice--ok notice" role="status" style={{ margin: 0 }}>
                  已保存 {material.id} · 录入于 {formatDateTime(material.recorded_at)}
                </p>
                <p className="verbatim" style={{ margin: '8px 0 0' }}>
                  {material.content}
                </p>
                <p className="meta-line">
                  <Link to={`/materials/${material.id}`}>查看详情</Link>
                </p>
              </li>
            ))}
          </ul>
          <p className="muted small">
            以上来自本次会话的真实保存响应；刷新后可在
            <Link to="/materials">素材</Link>中继续回看。
          </p>
        </>
      )}
    </div>
  );
}
