import { describe, expect, it } from 'vitest';
import {
  buildMaterialPayload,
  buildResponsePayload,
  buildSourcePayload,
  isValidHttpUrl,
  validateMaterialDraft,
  validateResponseDraft,
  validateSourceDraft,
} from './payloads';

describe('素材负载', () => {
  it('trim 为空白时拒绝提交', () => {
    const result = validateMaterialDraft({
      kind: 'thought',
      content: '   \n\t ',
      privacy: 'private',
      preserveVerbatim: true,
      context: '',
    });
    expect(result.ok).toBe(false);
  });

  it('提交原始字符串，保留换行与首尾空格', () => {
    const raw = '  第一行\n\n第二行，保留标点！  ';
    const payload = buildMaterialPayload({
      kind: 'thought',
      content: raw,
      privacy: 'private',
      preserveVerbatim: true,
      context: '',
    });
    expect(payload.content).toBe(raw);
    expect(payload.preserve_verbatim).toBe(true);
    expect(payload).not.toHaveProperty('context');
    // 不发送后端没有的字段
    expect(payload).not.toHaveProperty('title');
    expect(payload).not.toHaveProperty('mirror_status');
    expect(payload).not.toHaveProperty('effective_at');
  });

  it('上下文非空时才携带', () => {
    const payload = buildMaterialPayload({
      kind: 'feeling',
      content: '合成内容',
      privacy: 'private',
      preserveVerbatim: false,
      context: '通勤路上',
    });
    expect(payload.context).toBe('通勤路上');
  });
});

describe('来源负载', () => {
  const base = {
    kind: 'web_article' as const,
    originalUrl: 'https://example.com/a',
    title: '【合成】示例文章',
    platform: '',
    canonicalUrl: '',
    creator: '',
    publisher: '',
    publishedAt: '',
    language: '',
    topics: '',
    propositions: [],
  };

  it('要求有效 HTTP(S) 链接', () => {
    expect(isValidHttpUrl('https://example.com')).toBe(true);
    expect(isValidHttpUrl('http://example.com')).toBe(true);
    expect(isValidHttpUrl('ftp://example.com')).toBe(false);
    expect(isValidHttpUrl('example.com')).toBe(false);
    expect(validateSourceDraft({ ...base, originalUrl: 'not-a-url' }).ok).toBe(false);
  });

  it('要求标题非空', () => {
    expect(validateSourceDraft({ ...base, title: '  ' }).ok).toBe(false);
  });

  it('空可选字段不发送，主题按中英文逗号拆分', () => {
    const payload = buildSourcePayload({
      ...base,
      creator: '合成作者',
      topics: '清单, 笔记，工具',
    });
    expect(payload.creator).toBe('合成作者');
    expect(payload.topics).toEqual(['清单', '笔记', '工具']);
    expect(payload).not.toHaveProperty('platform');
    expect(payload).not.toHaveProperty('stance');
    expect(payload).not.toHaveProperty('raw_archive_path');
  });

  it('来源命题归属保持分开', () => {
    const payload = buildSourcePayload({
      ...base,
      propositions: [
        { text: '作者原话命题', attribution: 'author_explicit' },
        { text: '归纳命题', attribution: 'collaborator_summary' },
      ],
    });
    expect(payload.propositions).toEqual([
      { text: '作者原话命题', attribution: 'author_explicit' },
      { text: '归纳命题', attribution: 'collaborator_summary' },
    ]);
  });
});

describe('回应负载', () => {
  const base = {
    targetId: 'SRC-0001/P01',
    resonance: 'high' as const,
    agreement: 'partly_agree' as const,
    adoption: 'undecided' as const,
    confidence: 'medium' as const,
    originalWords: '',
    context: '',
    effectiveAtIso: null,
    supersedes: '',
    alsoCreatePersonalProposition: false,
    personalPropositionText: '',
    personalPropositionPrivacy: 'private' as const,
  };

  it('三轴独立携带，互不推断', () => {
    const payload = buildResponsePayload(base);
    expect(payload.resonance).toBe('high');
    expect(payload.agreement).toBe('partly_agree');
    expect(payload.adoption).toBe('undecided');
    expect(payload).not.toHaveProperty('creates_personal_proposition_text');
  });

  it('仅引用 / 未决定时即使勾选也不创建个人命题', () => {
    const payload = buildResponsePayload({
      ...base,
      adoption: 'cite',
      alsoCreatePersonalProposition: true,
      personalPropositionText: '合成命题',
    });
    expect(payload).not.toHaveProperty('creates_personal_proposition_text');
  });

  it('采用但未勾选时不创建个人命题', () => {
    const payload = buildResponsePayload({ ...base, adoption: 'adopt' });
    expect(payload).not.toHaveProperty('creates_personal_proposition_text');
  });

  it('采用且勾选但正文为空时校验失败', () => {
    const result = validateResponseDraft({
      ...base,
      adoption: 'adapt',
      alsoCreatePersonalProposition: true,
      personalPropositionText: '   ',
    });
    expect(result.ok).toBe(false);
  });

  it('采用且勾选并确认正文时一次请求同步创建', () => {
    const payload = buildResponsePayload({
      ...base,
      adoption: 'adapt',
      alsoCreatePersonalProposition: true,
      personalPropositionText: '我的调整版本',
    });
    expect(payload.creates_personal_proposition_text).toBe('我的调整版本');
    expect(payload.personal_proposition_privacy).toBe('private');
  });

  it('supersedes 默认不发送', () => {
    expect(buildResponsePayload(base)).not.toHaveProperty('supersedes');
    const payload = buildResponsePayload({
      ...base,
      supersedes: 'RSP-20260906-001',
    });
    expect(payload.supersedes).toBe('RSP-20260906-001');
  });

  it('明确过去时间才携带 effective_at 与精度', () => {
    expect(buildResponsePayload(base)).not.toHaveProperty('effective_at');
    const payload = buildResponsePayload({
      ...base,
      effectiveAtIso: '2026-08-01T10:00:00.000Z',
    });
    expect(payload.effective_at).toBe('2026-08-01T10:00:00.000Z');
    expect(payload.time_precision).toBe('minute');
  });
});
