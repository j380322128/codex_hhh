# 服务器部署说明

服务器已有 Python 3.6.8 时，可以直接使用项目自带脚本部署。脚本会检测 Python 版本，低于 3.10 时会在项目目录下安装独立 Python 运行时，不会替换系统 Python。

注意：首次部署需要下载项目内 Python 运行时和安装 Python 依赖。脚本默认使用清华镜像：

- Miniforge：`https://mirrors.tuna.tsinghua.edu.cn/github-release/conda-forge/miniforge/LatestRelease`
- Conda：`https://mirrors.tuna.tsinghua.edu.cn/anaconda`
- PyPI：`https://pypi.tuna.tsinghua.edu.cn/simple`

## 一键启动

进入项目根目录：

```bash
cd /path/to/codex_hhh
chmod +x scripts/run_server.sh scripts/stop_server.sh
./scripts/run_server.sh
```

默认启动地址：

```text
http://服务器IP:8000
```

API 基础地址：

```text
http://服务器IP:8000/api/
```

健康检查：

```text
http://服务器IP:8000/api/health/
```

如果 `8000` 端口已经被其他服务占用，换端口启动：

```bash
APP_PORT=8010 ./scripts/run_server.sh
```

然后访问：

```text
http://服务器IP:8010/api/health/
```

## 常用环境变量

```bash
APP_HOST=0.0.0.0
APP_PORT=8000
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=*
DJANGO_SECRET_KEY=请替换成随机字符串
GUNICORN_WORKERS=2
GUNICORN_TIMEOUT=120
PROJECT_WORKSPACE_DIR=/usr/share/nginx/client
MINIFORGE_BASE_URL=https://mirrors.tuna.tsinghua.edu.cn/github-release/conda-forge/miniforge/LatestRelease
CONDA_MIRROR_URL=https://mirrors.tuna.tsinghua.edu.cn/anaconda
PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
```

示例：

```bash
APP_PORT=9000 DJANGO_ALLOWED_HOSTS=example.com,服务器IP ./scripts/run_server.sh
```

## 停止服务

```bash
./scripts/stop_server.sh
```

## 查看日志

```bash
tail -f logs/access.log
tail -f logs/error.log
```

## 跑不起来时排查

先执行诊断脚本：

```bash
chmod +x scripts/diagnose_server.sh
./scripts/diagnose_server.sh
```

最常见原因：

- 直接用服务器 Python 3.6.8 执行 `pip install -r requirements.txt`，会失败。请使用 `./scripts/run_server.sh`。
- 之前已经创建过 Python 3.6 的 `.venv`。新版脚本会自动重建不兼容的 `.venv`。
- 服务器不能访问 GitHub 或 PyPI，导致无法下载项目内 Python 或安装依赖。
- 8000 端口没有开放安全组/防火墙，服务启动了但外部访问不到。
- 8000 端口已经有别的服务在运行。浏览器看到的不是本项目时，请用 `APP_PORT=8010 ./scripts/run_server.sh` 换端口。

## 目录说明

- `.runtime/`：当服务器 Python 版本过低时，脚本安装的项目内 Python。
- `.venv/`：项目虚拟环境。
- `templates_packages/`：放置 `pc_tempate.zip`、`wap_template.zip` 模板压缩包。
- `PROJECT_WORKSPACE_DIR/<host>/`：项目上传压缩包解压后的目录。服务器默认是 `/usr/share/nginx/client/<host>/`。

## 重新部署

更新代码后重新执行：

```bash
./scripts/run_server.sh
```

脚本会安装依赖、执行数据库迁移、收集静态文件，并重启服务。

## 主键规则变更后的处理

如果服务器上已经用旧版本创建过 `db.sqlite3`，旧库里部门和分类还是 UUID 主键。更新到新版本后，建议在没有重要数据时直接重建数据库：

```bash
cd /usr/share/nginx/client/codex_hhh
bash scripts/stop_server.sh
rm -f db.sqlite3
APP_PORT=8010 bash scripts/run_server.sh
```

重建后默认数据 ID：

- 产品研发中心：`department_id=1`
- 产品原型：`category_id=1`
- 企业宣传：`category_id=2`
- 示例项目：`project_id=99999999`
