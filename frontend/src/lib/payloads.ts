/**
 * 提交负载构建与本地校验。
 * 规则来源：docs/前端设计与实施指导书.md 第 6 节。
 * - 素材：trim 判断是否空白，但提交原始字符串（保留换行与标点）。
 * - 来源：必须有效 HTTP(S) 链接；空可选字段不发送。
 * - 回应：只有 adopt/adapt 且用户明确勾选并确认文本时，才携带
 *   creates_personal_proposition_text；三轴互不推断。
 */

import type {
  Adoption,
  Agreement,
  Confidence,
  MaterialCreatePayload,
  MaterialKind,
  Privacy,
  Resonance,
  ResponseEventCreatePayload,
  SourceCreatePayload,
  SourceKind,
  SourcePropositionCreatePayload,
} from '../api/types';

export interface DraftValidation {
  ok: boolean;
  message?: string;
}

export interface MaterialDraft {
  kind: MaterialKind;
  content: string;
  privacy: Privacy;
  preserveVerbatim: boolean;
  context: string;
}

export function validateMaterialDraft(draft: MaterialDraft): DraftValidation {
  if (draft.content.trim().length === 0) {
    return { ok: false, message: '内容还是空白，先写点什么再保存。' };
  }
  return { ok: true };
}

export function buildMaterialPayload(draft: MaterialDraft): MaterialCreatePayload {
  const payload: MaterialCreatePayload = {
    kind: draft.kind,
    content: draft.content,
    privacy: draft.privacy,
    preserve_verbatim: draft.preserveVerbatim,
  };
  if (draft.context.trim().length > 0) {
    payload.context = draft.context;
  }
  return payload;
}

export interface SourceDraft {
  kind: SourceKind;
  originalUrl: string;
  title: string;
  platform: string;
  canonicalUrl: string;
  creator: string;
  publisher: string;
  publishedAt: string;
  language: string;
  topics: string;
  propositions: SourcePropositionCreatePayload[];
}

export function isValidHttpUrl(value: string): boolean {
  try {
    const url = new URL(value);
    return url.protocol === 'http:' || url.protocol === 'https:';
  } catch {
    return false;
  }
}

export function validateSourceDraft(draft: SourceDraft): DraftValidation {
  if (draft.title.trim().length === 0) {
    return { ok: false, message: '请填写来源标题。' };
  }
  if (!isValidHttpUrl(draft.originalUrl.trim())) {
    return { ok: false, message: '请填写有效的 HTTP(S) 原始链接。' };
  }
  if (
    draft.canonicalUrl.trim().length > 0 &&
    !isValidHttpUrl(draft.canonicalUrl.trim())
  ) {
    return { ok: false, message: '规范链接也需要是有效的 HTTP(S) 链接。' };
  }
  for (const proposition of draft.propositions) {
    if (proposition.text.trim().length === 0) {
      return { ok: false, message: '来源命题的正文不能为空。' };
    }
  }
  return { ok: true };
}

export function buildSourcePayload(draft: SourceDraft): SourceCreatePayload {
  const payload: SourceCreatePayload = {
    kind: draft.kind,
    original_url: draft.originalUrl.trim(),
    title: draft.title.trim(),
  };
  const optionalText = {
    platform: draft.platform,
    canonical_url: draft.canonicalUrl,
    creator: draft.creator,
    publisher: draft.publisher,
    published_at: draft.publishedAt,
    language: draft.language,
  } as const;
  for (const key of Object.keys(optionalText) as (keyof typeof optionalText)[]) {
    const trimmed = optionalText[key].trim();
    if (trimmed.length > 0) {
      payload[key] = trimmed;
    }
  }
  const topics = draft.topics
    .split(/[,，]/)
    .map((topic) => topic.trim())
    .filter((topic) => topic.length > 0);
  if (topics.length > 0) payload.topics = topics;
  if (draft.propositions.length > 0) {
    payload.propositions = draft.propositions.map((proposition) => ({
      text: proposition.text.trim(),
      attribution: proposition.attribution,
    }));
  }
  return payload;
}

export interface ResponseDraft {
  targetId: string;
  resonance: Resonance;
  agreement: Agreement;
  adoption: Adoption;
  confidence: Confidence;
  originalWords: string;
  context: string;
  /** null 表示“这是我现在的回应”；否则为带时区 ISO 的明确过去时间 */
  effectiveAtIso: string | null;
  supersedes: string;
  alsoCreatePersonalProposition: boolean;
  personalPropositionText: string;
  personalPropositionPrivacy: Privacy;
}

export function validateResponseDraft(draft: ResponseDraft): DraftValidation {
  if (
    (draft.adoption === 'adopt' || draft.adoption === 'adapt') &&
    draft.alsoCreatePersonalProposition &&
    draft.personalPropositionText.trim().length === 0
  ) {
    return { ok: false, message: '已勾选记录为我的命题，请确认命题正文。' };
  }
  return { ok: true };
}

export function buildResponsePayload(
  draft: ResponseDraft,
): ResponseEventCreatePayload {
  const payload: ResponseEventCreatePayload = {
    target_id: draft.targetId,
    resonance: draft.resonance,
    agreement: draft.agreement,
    adoption: draft.adoption,
    confidence: draft.confidence,
  };
  if (draft.effectiveAtIso) {
    payload.effective_at = draft.effectiveAtIso;
    payload.time_precision = 'minute';
  }
  if (draft.originalWords.trim().length > 0) {
    payload.original_words = draft.originalWords;
  }
  if (draft.context.trim().length > 0) {
    payload.context = draft.context;
  }
  if (draft.supersedes) {
    payload.supersedes = draft.supersedes;
  }
  if (
    (draft.adoption === 'adopt' || draft.adoption === 'adapt') &&
    draft.alsoCreatePersonalProposition
  ) {
    payload.creates_personal_proposition_text = draft.personalPropositionText;
    payload.personal_proposition_privacy = draft.personalPropositionPrivacy;
  }
  return payload;
}
