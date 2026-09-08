# Arrive 前端（第一期）

“抵达 / Arrive”的业务前端：忠实采集、素材回看、来源登记、观点回应。
视觉为 Arrive 自有品牌规范（暖白、留白、克制侧边栏），不复制任何第三方标志；
不接入任何模型服务。页面与现有后端接口的对应及运行方式见下文。

## 边界

- 所有真实内容只通过后端 API 持久化到数据根（默认 `D:\emotion\arrive-data`）；
  浏览器不持久化原话和查询数据到 localStorage / IndexedDB / Service Worker。
- 前端只请求相对路径 `/api/v1/...` 与 `/health`，由 Vite 开发代理转发到
  `127.0.0.1:8000`，不剥离前缀。
- 没有编辑 / 删除素材、假镜像状态、假语义卡、假 AI 回复等后端不支持的功能。
- POST 不自动重试：超时可能已写入，界面保留输入并提示到列表人工核对。

## Docker 运行

在项目根执行 `docker compose up --build -d --wait`，打开 `http://127.0.0.1:8080`。镜像内使用 `npm ci` 构建，再由 Nginx 提供页面及 API 代理，无需本机 Node。详见 [Docker 运行指南](../docs/Docker运行指南.md)。

## 源码开发运行（两个本地终端）

前置：Node.js（建议 ≥ 20；开发使用 v24 验证）与 Python ≥ 3.12。

```powershell
# 终端 1：后端（默认数据根 D:\emotion\arrive-data）
cd backend
python -m pip install -e ".[dev]"
python -m uvicorn arrive.main:app --reload   # 127.0.0.1:8000
```

```powershell
# 终端 2：前端
cd frontend
npm ci
npm run dev                                 # 127.0.0.1:5173
```

打开 `http://127.0.0.1:5173/`。首次验收建议使用系统临时数据根启动后端，
避免合成测试数据写入个人数据库：

```powershell
$env:ARRIVE_DATA_DIR = (New-Item -ItemType Directory -Force "$env:TEMP\arrive-verify").FullName
python -m uvicorn arrive.main:app
```

## 脚本

| 命令 | 用途 |
| --- | --- |
| `npm run dev` | 开发服务器（代理 `/api`、`/health` 到 8000） |
| `npm run typecheck` | TypeScript 类型检查 |
| `npm test` | Vitest 单元与组件测试（mock fetch，不触网） |
| `npm run build` | 类型检查 + 生产构建到 `dist/`（构建不等于部署） |
| `node scripts/acceptance-shots.mjs` | 端到端合成数据截图（需双服务已启动，输出到 Git 忽略的 `test-results/`） |

## 页面与接口对应

| 页面 | 路由 | 使用的后端接口 |
| --- | --- | --- |
| 记录 | `/` | `POST /api/v1/materials` |
| 素材 | `/materials`、`/materials/:id` | `GET /api/v1/materials`（详情从列表恢复） |
| 来源 | `/sources`、`/sources/:id` | `GET/POST /api/v1/sources`、`GET /api/v1/sources/{id}` |
| 观点 | `/propositions` | `GET/POST /api/v1/personal-propositions` |
| 命题回应 | `/responses?target=...` | `POST /api/v1/responses`、`GET /responses/timeline/{id}`、`GET /responses/snapshot/{id}?as_of=` |

侧边栏连接状态来自 `GET /health`。`POST/GET /api/v1/thought-maps` 本期不对普通界面开放。

## 已知后端缺口（本期不补造）

- 素材无单条 GET / 编辑 / 删除；详情从列表恢复，不显示镜像状态。
- 无镜像版本、确认事件、关键词语义 API；素材仅供回看。
- 来源登记必须有 HTTP(S) 链接；无快照、抓取、定位批注、追加来源命题接口。
- `effective_at` 未传时后端回退为 `recorded_at`，界面默认只展示「录入时间」，
  不把返回值冒充为思想发生时间；模糊时间（只知年月）待后端契约。
- POST 无幂等键；快照按生效时间逐轴计算，未说明不清空旧轴，不按情境合并。
- 后端当前无认证与字段级加密，仅限本地或受控环境，不能公开部署为私人数据服务。

## 数据边界

`frontend/` 已加入 `scripts/check_data_boundary.py` 的软件目录白名单；
`node_modules/`、`dist/`、`test-results/` 等生成物由 `.gitignore` 忽略。
提交前运行 `python scripts/check_data_boundary.py`。截图与测试一律使用合成数据。

## 验收与开发交接

前端 27 项测试、类型检查和构建通过；主要流程已通过系统临时数据库上的真实浏览器联调。
仍有三处未修复的草稿保护问题（FE-001 至 FE-003），不能标为完整验收。

当前问题状态、复现步骤、验证范围与下一步统一记录在
[开发进度与模型交接](../docs/开发进度与模型交接.md)，后续模型接手前先阅读并在结束时更新。
