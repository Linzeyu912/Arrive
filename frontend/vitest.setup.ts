import '@testing-library/jest-dom/vitest';
import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';

// vitest 未启用 globals，需显式注册 DOM 清理，避免跨测试残留渲染
afterEach(() => {
  cleanup();
});
