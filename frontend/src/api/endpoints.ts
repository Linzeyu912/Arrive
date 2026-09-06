/** 现有后端接口封装。路径与 api.py 一一对应；不虚构端点。 */

import { apiRequest } from './client';
import type {
  Health,
  Material,
  MaterialCreatePayload,
  PersonalProposition,
  PersonalPropositionCreatePayload,
  ResponseEvent,
  ResponseEventCreatePayload,
  Source,
  SourceCreatePayload,
  StanceSnapshot,
} from './types';

const API = '/api/v1';

/** 路径参数逐段编码：来源命题 ID 含 `/`，如 SRC-0001/P01。 */
export function encodePathParam(value: string): string {
  return encodeURIComponent(value);
}

export function fetchHealth(): Promise<Health> {
  return apiRequest<Health>('/health', { timeoutMs: 8000 });
}

export function createMaterial(payload: MaterialCreatePayload): Promise<Material> {
  return apiRequest<Material>(`${API}/materials`, { method: 'POST', body: payload });
}

export function listMaterials(): Promise<Material[]> {
  return apiRequest<Material[]>(`${API}/materials`);
}

export function createSource(payload: SourceCreatePayload): Promise<Source> {
  return apiRequest<Source>(`${API}/sources`, { method: 'POST', body: payload });
}

export function listSources(): Promise<Source[]> {
  return apiRequest<Source[]>(`${API}/sources`);
}

export function getSource(sourceId: string): Promise<Source> {
  return apiRequest<Source>(`${API}/sources/${encodePathParam(sourceId)}`);
}

export function createPersonalProposition(
  payload: PersonalPropositionCreatePayload,
): Promise<PersonalProposition> {
  return apiRequest<PersonalProposition>(`${API}/personal-propositions`, {
    method: 'POST',
    body: payload,
  });
}

export function listPersonalPropositions(): Promise<PersonalProposition[]> {
  return apiRequest<PersonalProposition[]>(`${API}/personal-propositions`);
}

export function createResponseEvent(
  payload: ResponseEventCreatePayload,
): Promise<ResponseEvent> {
  return apiRequest<ResponseEvent>(`${API}/responses`, {
    method: 'POST',
    body: payload,
  });
}

export function getResponseTimeline(targetId: string): Promise<ResponseEvent[]> {
  return apiRequest<ResponseEvent[]>(
    `${API}/responses/timeline/${encodePathParam(targetId)}`,
  );
}

export function getStanceSnapshot(
  targetId: string,
  asOf?: string,
): Promise<StanceSnapshot> {
  const params = new URLSearchParams();
  if (asOf) params.set('as_of', asOf);
  const query = params.size > 0 ? `?${params.toString()}` : '';
  return apiRequest<StanceSnapshot>(
    `${API}/responses/snapshot/${encodePathParam(targetId)}${query}`,
  );
}
