/**
 * 后端 DTO。逐项对照 backend/src/arrive/schemas.py 与 domain.py。
 * 读取模型与页面展示模型分开；不通过 any 或类型断言绕过契约。
 */

export type Privacy = 'private' | 'anonymized' | 'shareable';

export type MaterialKind =
  | 'thought'
  | 'feeling'
  | 'experience'
  | 'contradiction'
  | 'question'
  | 'quote'
  | 'context';

export interface Material {
  id: string;
  kind: MaterialKind;
  content: string;
  privacy: Privacy;
  preserve_verbatim: boolean;
  recorded_at: string;
  effective_at: string;
  context: string | null;
}

export interface MaterialCreatePayload {
  kind: MaterialKind;
  content: string;
  privacy: Privacy;
  preserve_verbatim: boolean;
  recorded_at?: string;
  context?: string;
}

export type SourceKind =
  | 'web_article'
  | 'book'
  | 'video'
  | 'podcast'
  | 'speech'
  | 'conversation'
  | 'other';

export type SourceStance =
  | 'pending'
  | 'endorsed'
  | 'partially_endorsed'
  | 'reference'
  | 'questioned'
  | 'opposed';

export type ContentStatus =
  | 'registered'
  | 'metadata_only'
  | 'summarized'
  | 'mapped'
  | 'cited'
  | 'unavailable';

export type Rights =
  | 'third_party_copyright'
  | 'licensed'
  | 'public_domain'
  | 'user_owned'
  | 'unknown';

export type PropositionAttribution = 'author_explicit' | 'collaborator_summary';

export interface SourceProposition {
  id: string;
  ordinal: number;
  text: string;
  attribution: PropositionAttribution;
  created_at: string;
}

export interface Source {
  id: string;
  kind: SourceKind;
  platform: string | null;
  original_url: string | null;
  canonical_url: string | null;
  title: string;
  creator: string | null;
  publisher: string | null;
  published_at: string | null;
  language: string | null;
  topics: string[];
  stance: SourceStance;
  stance_as_of: string | null;
  content_status: ContentStatus;
  rights: Rights;
  raw_archive_path: string | null;
  raw_archive_sha256: string | null;
  raw_archive_bytes: number | null;
  created_at: string;
  propositions: SourceProposition[];
}

export interface SourcePropositionCreatePayload {
  text: string;
  attribution: PropositionAttribution;
}

export interface SourceCreatePayload {
  kind: SourceKind;
  original_url: string;
  title: string;
  platform?: string;
  canonical_url?: string;
  creator?: string;
  publisher?: string;
  published_at?: string;
  language?: string;
  topics?: string[];
  propositions?: SourcePropositionCreatePayload[];
}

export interface PersonalProposition {
  id: string;
  text: string;
  origin_source_proposition_id: string | null;
  privacy: Privacy;
  created_at: string;
}

export interface PersonalPropositionCreatePayload {
  text: string;
  origin_source_proposition_id?: string;
  privacy?: Privacy;
}

export type Resonance = 'high' | 'medium' | 'low' | 'none' | 'unspecified';

export type Agreement =
  | 'agree'
  | 'mostly_agree'
  | 'partly_agree'
  | 'uncertain'
  | 'disagree'
  | 'unspecified';

export type Adoption = 'adopt' | 'adapt' | 'cite' | 'not_use' | 'undecided';

export type Confidence = 'low' | 'medium' | 'high';

export type TimePrecision = 'minute' | 'day' | 'month' | 'year' | 'unknown';

export interface ResponseEventCreatePayload {
  target_id: string;
  recorded_at?: string;
  effective_at?: string;
  time_precision?: TimePrecision;
  resonance?: Resonance;
  agreement?: Agreement;
  adoption?: Adoption;
  confidence?: Confidence;
  original_words?: string;
  context?: string;
  supersedes?: string;
  creates_personal_proposition_text?: string;
  personal_proposition_privacy?: Privacy;
}

export interface ResponseEvent {
  id: string;
  target_id: string;
  target_type: 'source_proposition' | 'personal_proposition';
  recorded_at: string;
  effective_at: string;
  time_precision: TimePrecision;
  resonance: Resonance;
  agreement: Agreement;
  adoption: Adoption;
  confidence: Confidence;
  original_words: string | null;
  context: string | null;
  assistant_summary: string | null;
  supersedes: string | null;
  creates_personal_proposition_id: string | null;
}

export interface AxisSnapshot {
  value: string;
  event_id: string | null;
  effective_at: string | null;
}

export interface StanceSnapshot {
  target_id: string;
  as_of: string;
  resonance: AxisSnapshot;
  agreement: AxisSnapshot;
  adoption: AxisSnapshot;
  event_count: number;
}

export interface Health {
  status: string;
  service: string;
  version: string;
}
