# Docker 运行指南

普通使用者只需 Docker（包含 Compose v2），无需单独安装 Node、npm、Python 或数据库。Windows/macOS 可使用 Docker Desktop 并启动 Linux 容器引擎；Linux 安装 Docker Engine 与 Compose 插件。首次构建需要访问镜像仓库及 npm/Python 包源，后续启动复用本机镜像。

## 首次启动

```sh
git clone https://github.com/Linzeyu912/Arrive.git
cd Arrive
docker compose up --build -d --wait
```

打开 [http://127.0.0.1:8080](http://127.0.0.1:8080)。也可以下载仓库 ZIP、解压后在包含 `compose.yaml` 的目录执行最后一条命令。首次无须创建 `.env`。

前端构建为静态文件，由 Nginx 提供页面和同源 API 代理；后端通过 Alembic 自动初始化/升级数据库，健康检查成功后前端启动。浏览器刷新素材详情也能返回应用页面。API 错误保留后端响应，不回退成 HTML。

默认仅绑定本机地址，后端 8000 端口不映射到宿主机。当前没有认证和字段加密，容器封装不改变这一限制；不应将端口开放到公网供他人提交私人数据。

## 数据放在哪里

默认将项目内 `arrive-data/` 挂载到后端容器 `/data`，数据库为 `arrive-data/database/arrive.db`。首次会创建目录及标识文件；整个目录由 Git 忽略，不进入镜像构建上下文。前端容器不挂载数据目录。

`docker compose down` 只停止并删除容器和网络，不删除此宿主机数据目录。重新构建镜像仍会使用原有数据。不要同时用本机开发服务和 Docker 操作同一数据根；升级或备份前先停止写入。

旧版 Compose 使用命名卷。新配置不会自动读取或迁移那个卷；如果使用过旧版且其中已有数据，先停止旧服务、备份并把**完整数据根**复制到空的 `arrive-data/`，不要只复制数据库，也不要删除旧卷后再尝试迁移。原有卷不会被本次配置自动删除。

## 常用操作

```sh
docker compose ps
docker compose logs --tail=100
docker compose stop
docker compose start
docker compose down
```

升级前 `docker compose down`，备份完整 `arrive-data/` 到单独位置，再更新代码并执行 `docker compose up --build -d --wait`。数据库迁移可能改变格式，回退代码前应核对迁移兼容性或恢复相配套的完整备份。

需要修改端口或选择外部数据目录时，在项目根创建被忽略的 `.env`，只填需要覆盖的项：

```dotenv
ARRIVE_PORT=8081
# 可选，Windows 使用正斜杠的绝对路径；Linux/macOS 使用对应绝对路径。
# ARRIVE_DOCKER_DATA_DIR=D:/ArriveData
```

修改后重新执行 `docker compose up -d --wait`。容器内部仍固定使用 `/data`，宿主机路径不写入镜像。数据目录不得等于/包含项目根或落入源码，不能使用指回源码的链接。Linux 自定义目录必须允许容器写入；不要将宿主机根目录挂载给应用。

## 版本如何固定

- 前端：`npm ci` 严格使用 `frontend/package-lock.json`，不在构建时刷新依赖版本。
- 后端：`backend/requirements.lock` 固定运行与构建工具的直接/间接依赖，并使用 `pip --require-hashes` 校验；项目安装禁用依赖重解析和构建隔离。
- Node、Python、Nginx 基础镜像固定为多架构镜像摘要，避免同名标签更新导致构建环境漂移。固定不等于永远不升级，维护者应定期更新摘要及锁文件并跑验收。

维护者更新后端锁文件（普通使用者无需安装 uv）：

```sh
uv pip compile backend/pyproject.toml backend/build-requirements.in --python-version 3.12 --python-platform linux --generate-hashes --output-file backend/requirements.lock
```

锁文件针对 Linux Python 3.12 容器；本机 Windows 开发仍按后端 README 安装。镜像拉取、网络连通、Docker/虚拟化条件和目标架构依旧会影响首次运行，不能承诺所有机器零故障。

## 验收与排障

配置检查：`docker compose config --quiet`。

维护者可运行 `python scripts/docker_smoke.py`。脚本创建独立 Compose 项目、随机本机端口和系统临时数据根，验证页面深链接、API、来源命题路径、采用创建个人命题、迁移及容器重建后的持久化；最后关闭验收容器，保留合成临时目录便于排查，不接触个人数据。普通使用者无需 Python，也无需运行此脚本。

GitHub Actions 的 `Docker integration` 工作流执行相同验收。工作流文件存在不等于已运行通过；实际验证范围见 [开发交接](./开发进度与模型交接.md)。

若提示无法连接 Docker daemon，先启动 Docker Desktop/Engine 并确认 `docker info` 能返回 Server 信息。若镜像或依赖下载失败，检查本机网络和 Docker 代理；若端口占用，按上面的 `.env` 修改 `ARRIVE_PORT`。启动 unhealthy 时查看 `docker compose logs --tail=100 api web`，不要通过关闭健康检查掩盖迁移或数据根错误。

设计依据：[Docker 构建与镜像固定](https://docs.docker.com/build/building/best-practices/)、[Compose 健康检查与启动顺序](https://docs.docker.com/compose/how-tos/startup-order/)。
