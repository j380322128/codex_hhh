# 项目管理平台 API

一个 Django 后端接口项目。项目主键为 8 位短 UUID 字符串；部门、项目类型主键为自增整数。

接口文档见 [API_DOCS.md](API_DOCS.md)。

服务器部署说明见 [DEPLOY.md](DEPLOY.md)。

## 本地运行

```bash
python3 -m pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver
```

接口基础地址为 http://127.0.0.1:8000/api/。

模板压缩包放在项目根目录的 `templates_packages/` 文件夹中：

- `pc_tempate.zip`
- `wap_template.zip`

项目上传压缩包会解压到项目工作目录的 `<host>/` 文件夹中。服务器默认项目工作目录是 `/usr/share/nginx/client`。

## 接口

- `GET /api/departments/?include_categories=1`：一级分类/部门列表
- `POST /api/departments/`：新增一级分类，JSON：`{"name":"产品研发中心","sort_order":10}`
- `GET /api/categories/?department_id=<id>`：二级分类/项目类型列表
- `POST /api/categories/`：新增二级分类，JSON：`{"name":"产品原型","prompt":"二级分类提示词","department_id":1,"sort_order":10}`
- `GET /api/projects/?department_id=<id>&category_id=<id>`：项目列表
- `POST /api/projects/`：新建项目
- `GET|PUT|PATCH|DELETE /api/projects/<project_id>/`：项目详情、更新、删除

新建项目 JSON 示例：

```json
{
  "host": "project_center_admin",
  "name": "数字人需求用例",
  "template": "pc",
  "description": "用于管理部门、项目类型和项目模板配置。",
  "prompt": "",
  "department_id": 1,
  "category_id": 1
}
```
