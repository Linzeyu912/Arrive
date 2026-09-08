# Arrive Backend

“抵达 / Arrive”的首个可运行后端，用于把项目的协作规范变成可验证的数据和 API 行为。

## 当前能力

- 采集带隐私等级和时间信息的原始思绪；
- 登记外部来源及其稳定编号；
- 为来源建立带归属的命题；
- 追加观点回应事件，分别记录共鸣、认同和采用；
- 按指定时间点还原观点快照；
- 建立带节点、关系和矛盾的思考地图；
- 通过 OpenAPI 提供交互式接口文档。

## 核心不变量

1. 回应事件只能新增，没有更新和删除接口；
2. 所有事件时间必须包含时区；
3. 共鸣、认同和采用分别演进，不能相互推断；
4. 当前立场是截至某一时间的计算结果，不是覆盖历史的字段；
5. 外部来源命题和个人命题使用不同编号；
6. 只有明确的 `adopt` 或 `adapt` 操作才能同时建立个人命题；
7. 数据默认位于项目内被 Git 忽略的 `arrive-data/`，不得进入 Git；
8. 应用 SQLite 文件必须位于数据根的 `database/` 中，来源原文只使用数据根相对键。

## Docker 运行

普通使用者在项目根执行 `docker compose up --build -d --wait`，即可同时启动前后端；无需执行下方 pip 安装。详细步骤与验收限制见 [Docker 运行指南](../docs/Docker运行指南.md)。

## 本地运行

```powershell
cd backend
python -m pip install -e ".[dev]"
python -m uvicorn arrive.main:app --reload
```

默认数据根是项目目录内的 `arrive-data/`，默认数据库位于其中的 `database/arrive.db`。本仓库当前会解析为 `D:\emotion\arrive-data\database\arrive.db`。也可以显式指定数据根：

```powershell
$env:ARRIVE_DATA_DIR = "D:\emotion\arrive-data"
python -m uvicorn arrive.main:app --reload
```

如需设置 `ARRIVE_DATABASE_URL`，SQLite 路径仍必须位于 `ARRIVE_DATA_DIR/database/` 内；不支持 SQLite URI 文件名。数据根等于或包含项目根、落入源码目录，或项目内的 `arrive-data/` 未被 Git 忽略或已被跟踪时，后端会拒绝启动。示例变量见 [`.env.example`](./.env.example)。环境变量示例不是自动加载的配置文件；复制为 `.env` 后需显式使用 `--env-file .env`，或直接设置 shell 环境变量。

### 本地个人部署的数据归属

克隆软件不会下载其他人的数据，也不需要单独部署数据库服务器：默认使用本机 SQLite。数据库保存当前已实现的素材、命题、观点回应与思考地图，包含加工后的结构化数据，原始输入与加工结果都归属同一数据根。

第一次启动会在数据根创建标识、忽略全部内容的 `.gitignore`，以及 `database/`、`raw/`、`drafts/`、`outputs/`、`exports/`、`model-runs/` 等分类目录。已有合法数据根只补齐缺少的目录和忽略文件，不覆盖已有内容；非空且没有标识的目录会被拒绝。目录存在不代表对应功能已实现：附件实际落盘、镜像与完整输出流程仍待开发，未来文件访问必须复用 `arrive.config.data_path()` 校验，不能直接拼接到仓库路径。

可在 `backend/` 中查看当前解析的数据目录（不创建数据库）：

```powershell
python -c "from arrive.config import Settings; print(Settings().data_dir)"
```

每个克隆默认使用自身的 `arrive-data/`，相互独立；也可通过 `ARRIVE_DATA_DIR` 指定外部数据根。更改环境变量不会迁移旧数据；迁移前停止服务，备份并复制整个数据根（不是只复制一个数据库文件），再切换配置。

Docker Compose 默认将项目内 `arrive-data/` 挂载到容器 `/data`，停止或重建容器不会删除这个宿主机目录。旧版命名卷不会自动迁移，升级前请按 [Docker 运行指南](../docs/Docker运行指南.md) 备份和迁移完整数据根。

默认仅监听本机；当前没有用户认证和数据加密。目录分开与 Git 忽略是存储和版本管理边界，不等于加密或备份，也不会阻止操作系统云同步、人工复制或未来远程 LLM 调用。使用远程数据库或模型服务须另行确认数据流向。

启动后访问：

- API 文档：`http://127.0.0.1:8000/docs`
- 健康检查：`http://127.0.0.1:8000/health`

## 测试

```powershell
cd backend
python -m pytest
```

## API 概览

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| `POST` | `/api/v1/materials` | 采集一条原始思绪 |
| `GET` | `/api/v1/materials` | 浏览素材 |
| `POST` | `/api/v1/sources` | 创建来源及其命题 |
| `GET` | `/api/v1/sources/{source_id}` | 查看来源 |
| `POST` | `/api/v1/personal-propositions` | 创建个人命题 |
| `POST` | `/api/v1/responses` | 追加观点回应事件 |
| `GET` | `/api/v1/responses/timeline/{target_id}` | 查看完整时间线 |
| `GET` | `/api/v1/responses/snapshot/{target_id}` | 还原指定时间点立场 |
| `POST` | `/api/v1/thought-maps` | 创建思考地图 |
| `GET` | `/api/v1/thought-maps/{map_id}` | 查看思考地图 |

架构和后续边界见 [`docs/后端架构.md`](../docs/后端架构.md)。

软件与数据的完整隔离规则见 [软件与数据隔离规范](../docs/软件与数据隔离规范.md)。

## 开发交接

已完成能力、待修复问题、迁移验证范围和下一步统一记录在 [开发进度与模型交接](../docs/开发进度与模型交接.md)。接手开发时先核对该文档与当前代码，结束时更新后端栏目。
