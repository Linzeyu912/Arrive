# ARRIVE Backend

“抵达 / ARRIVE”的首个可运行后端，用于把项目的协作规范变成可验证的数据和 API 行为。

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
6. 只有明确的 `adopt` 或 `adapt` 操作才能同时建立个人命题。

## 本地运行

```powershell
cd backend
python -m pip install -e ".[dev]"
python -m uvicorn arrive.main:app --reload
```

默认数据库位于 `backend/data/arrive.db`。可以通过环境变量切换：

```powershell
$env:ARRIVE_DATABASE_URL = "sqlite:///D:/path/to/arrive.db"
```

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
