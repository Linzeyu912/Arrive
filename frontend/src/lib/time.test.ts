import { describe, expect, it } from 'vitest';
import { formatDateTime, localInputToIso } from './time';

describe('时间转换', () => {
  it('datetime-local 按本机时区转换为带时区 ISO（UTC Z）', () => {
    const iso = localInputToIso('2026-08-01T10:30');
    expect(iso).not.toBeNull();
    // 必须带时区标记（Z 或偏移），不能是裸字符串
    expect(iso).toMatch(/(Z|[+-]\d{2}:\d{2})$/);
    expect(new Date(iso!).getTime()).toBe(new Date('2026-08-01T10:30').getTime());
  });

  it('空值与非法值返回 null', () => {
    expect(localInputToIso('')).toBeNull();
    expect(localInputToIso('not-a-date')).toBeNull();
  });

  it('非法 ISO 原样返回而不是崩溃', () => {
    expect(formatDateTime('not-iso')).toBe('not-iso');
    expect(formatDateTime(null)).toBe('未记录');
  });
});
