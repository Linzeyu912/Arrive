/**
 * 时间工具。
 * 后端要求事件时间带时区：datetime-local 的裸字符串按用户本机时区解释，
 * 转换为 UTC ISO（带 Z 后缀），满足带时区要求，不把用户固定到某个时区。
 */

export function localInputToIso(value: string): string | null {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return date.toISOString();
}

export function nowIso(): string {
  return new Date().toISOString();
}

const dateTimeFormatter = new Intl.DateTimeFormat('zh-CN', {
  dateStyle: 'medium',
  timeStyle: 'short',
  hour12: false,
});

const dateFormatter = new Intl.DateTimeFormat('zh-CN', {
  dateStyle: 'medium',
});

export function formatDateTime(iso: string | null): string {
  if (!iso) return '未记录';
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return dateTimeFormatter.format(date);
}

export function formatDate(iso: string | null): string {
  if (!iso) return '未记录';
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return dateFormatter.format(date);
}
