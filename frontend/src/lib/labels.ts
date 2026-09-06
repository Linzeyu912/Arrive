/** 枚举中文显示名。与 domain.py 逐项对应。 */

import type {
  Adoption,
  Agreement,
  Confidence,
  MaterialKind,
  Privacy,
  PropositionAttribution,
  Resonance,
  SourceKind,
  TimePrecision,
} from '../api/types';

export const MATERIAL_KIND_LABELS: Record<MaterialKind, string> = {
  thought: '想法',
  feeling: '感受',
  experience: '经历',
  contradiction: '矛盾',
  question: '疑问',
  quote: '引文',
  context: '背景',
};

export const PRIVACY_LABELS: Record<Privacy, string> = {
  private: '私人',
  anonymized: '匿名后可分享',
  shareable: '确认可分享',
};

export const SOURCE_KIND_LABELS: Record<SourceKind, string> = {
  web_article: '网页文章',
  book: '书籍',
  video: '视频',
  podcast: '播客',
  speech: '演讲',
  conversation: '对话',
  other: '其他',
};

export const ATTRIBUTION_LABELS: Record<PropositionAttribution, string> = {
  author_explicit: '作者明确表达',
  collaborator_summary: '协作者归纳',
};

export const RESONANCE_LABELS: Record<Resonance, string> = {
  unspecified: '未说明',
  none: '无共鸣',
  low: '弱',
  medium: '中',
  high: '强',
};

export const AGREEMENT_LABELS: Record<Agreement, string> = {
  unspecified: '未说明',
  agree: '认同',
  mostly_agree: '大体认同',
  partly_agree: '部分认同',
  uncertain: '不确定',
  disagree: '不认同',
};

export const ADOPTION_LABELS: Record<Adoption, string> = {
  undecided: '尚未决定',
  adopt: '采用',
  adapt: '调整后采用',
  cite: '仅引用',
  not_use: '不采用',
};

export const CONFIDENCE_LABELS: Record<Confidence, string> = {
  low: '低',
  medium: '中',
  high: '高',
};

export const TIME_PRECISION_LABELS: Record<TimePrecision, string> = {
  minute: '精确到分钟',
  day: '精确到天',
  month: '精确到月',
  year: '精确到年',
  unknown: '时间未知',
};
