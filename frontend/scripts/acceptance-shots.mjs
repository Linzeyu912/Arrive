/**
 * 验收截图脚本：合成数据，经 Vite 代理访问真实后端（临时数据根）。
 * 用法：node scripts/acceptance-shots.mjs <backendOrigin 仅说明> 
 * 前置：后端 127.0.0.1:8000 与前端 127.0.0.1:5173 已启动。
 * 输出：frontend/test-results/screenshots/（已 Git 忽略）。
 */
import { chromium } from 'playwright';
import { mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const BASE = 'http://127.0.0.1:5173';
const OUT = fileURLToPath(new URL('../test-results/screenshots/', import.meta.url));
mkdirSync(OUT, { recursive: true });

const shot = async (page, name) => {
  await page.screenshot({ path: `${OUT}${name}.png`, fullPage: true });
  console.log('saved', name);
};

const browser = await chromium.launch();

// ---------- 桌面 1440px ----------
const desktop = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const page = await desktop.newPage();

// 记录页：真实保存一段合成原话
await page.goto(`${BASE}/`, { waitUntil: 'networkidle' });
await shot(page, 'desktop-01-record-empty');
await page.getByRole('textbox', { name: '原话' }).fill('【合成】我在想，清单工具是不是总在催促我。\n第二行保留换行。');
await page.getByRole('button', { name: '保存', exact: true }).click();
await page.getByText(/已保存 M\d+/).waitFor();
await shot(page, 'desktop-02-record-saved');

// 素材列表与详情
await page.getByRole('link', { name: '素材', exact: true }).first().click();
await page.getByText(/M\d+ · 想法/).first().waitFor();
await shot(page, 'desktop-03-materials');
await page.getByRole('link', { name: /我在想，清单工具/ }).click();
await page.getByText('镜像确认、关键词语义确认').waitFor();
await shot(page, 'desktop-04-material-detail');

// 来源登记（真实表单提交）
await page.getByRole('link', { name: '来源', exact: true }).first().click();
await page.getByRole('button', { name: '登记来源' }).click();
await page.getByLabel('原始链接（必选，HTTP/HTTPS）').fill('https://example.com/synthetic-article');
await page.getByLabel('标题（必选）').fill('【合成】示例文章：慢清单');
await page.getByText('更多信息（作者、平台、出版信息、主题）').click();
await page.getByLabel('作者', { exact: true }).fill('合成作者');
await page.getByRole('button', { name: '添加来源命题' }).click();
await page.getByLabel('命题 1 正文').fill('【合成】清单应当等待人，而不是催促人。');
await page.getByLabel('归属').selectOption('author_explicit');
await shot(page, 'desktop-05-source-form');
await page.getByRole('button', { name: '登记来源', exact: true }).click();
await page.getByText(/已登记 SRC-\d+/).waitFor();
await shot(page, 'desktop-06-source-registered');

// 来源详情 → 回应这个命题
await page.getByRole('link', { name: '【合成】示例文章：慢清单' }).click();
await page.getByText('作者明确表达').waitFor();
await shot(page, 'desktop-07-source-detail');
await page.getByRole('link', { name: '回应这个命题' }).click();
await page.getByText('当前摘要').waitFor();
await shot(page, 'desktop-08-response-empty');

// 三轴独立选择 + 调整后采用 + 同步创建个人命题
await page.getByRole('radio', { name: '强' }).check();
await page.getByRole('radio', { name: '部分认同' }).check();
await page.getByRole('radio', { name: '调整后采用' }).check();
await page.getByLabel('补充你的原话（可选）').fill('【合成】这句话让我松了口气。');
await page.getByLabel('同时记录为我的命题').check();
await page.getByLabel('确认命题正文').fill('【合成】我的清单应该等我，而不是催我。');
await shot(page, 'desktop-09-response-form');
await page.getByRole('button', { name: '追加这次回应' }).click();
await page.getByText(/RSP-\d{8}-\d{3} · 共鸣/).first().waitFor();
await shot(page, 'desktop-10-response-saved');

// 观点页
await page.getByRole('link', { name: '观点', exact: true }).first().click();
await page.getByText(/P\d+ · 记录于/).waitFor();
await shot(page, 'desktop-11-propositions');

await desktop.close();

// ---------- 移动 390px ----------
const mobile = await browser.newContext({
  viewport: { width: 390, height: 844 },
  isMobile: true,
  hasTouch: true,
});
const m = await mobile.newPage();
await m.goto(`${BASE}/`, { waitUntil: 'networkidle' });
await shot(m, 'mobile-01-record');
await m.getByRole('button', { name: '打开导航菜单' }).click();
await m.waitForTimeout(300); // 等抽屉滑出过渡结束
await shot(m, 'mobile-02-drawer');
await m.getByRole('link', { name: '素材', exact: true }).first().click();
await m.getByText(/M\d+ · 想法/).first().waitFor();
await m.waitForTimeout(300); // 等抽屉收起过渡结束
await shot(m, 'mobile-03-materials');
await mobile.close();

await browser.close();
console.log('all screenshots done');
