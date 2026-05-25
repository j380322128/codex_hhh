# 项目管理平台接口文档

## 基础信息

基础地址：

```text
http://127.0.0.1:8000/api/
```

请求格式：

```text
Content-Type: application/json
```

统一成功返回：

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

统一失败返回：

```json
{
  "code": 1,
  "message": "参数错误",
  "errors": {
    "name": "部门名称不能为空"
  }
}
```

说明：

- 项目主键为 8 位短 UUID 字符串，例如 `99999999`。
- 一级分类和二级分类主键为自增整数，例如 `1`。
- 时间格式为 `YYYY-MM-DD HH:mm:ss`。
- 项目模板 `template` 可选值为 `pc`、`mobile`。
- 项目根目录下的 `templates_packages/` 文件夹用于存放模板压缩包：`pc_tempate.zip`、`wap_template.zip`。

## 接口总览

| 方法 | 地址 | 说明 |
| --- | --- | --- |
| GET | `/api/health/` | 健康检查 |
| GET | `/api/departments/` | 获取一级分类列表 |
| POST | `/api/departments/` | 新增一级分类 |
| GET | `/api/departments/<department_id>/` | 获取一级分类详情 |
| PUT | `/api/departments/<department_id>/` | 完整更新一级分类 |
| PATCH | `/api/departments/<department_id>/` | 局部更新一级分类 |
| DELETE | `/api/departments/<department_id>/` | 删除一级分类 |
| GET | `/api/categories/` | 获取二级分类列表 |
| POST | `/api/categories/` | 新增二级分类 |
| GET | `/api/categories/<category_id>/` | 获取二级分类详情 |
| PUT | `/api/categories/<category_id>/` | 完整更新二级分类 |
| PATCH | `/api/categories/<category_id>/` | 局部更新二级分类 |
| DELETE | `/api/categories/<category_id>/` | 删除二级分类 |
| GET | `/api/projects/` | 获取项目列表 |
| POST | `/api/projects/` | 新建项目 |
| GET | `/api/projects/<project_id>/` | 获取项目详情 |
| GET | `/api/projects/<project_id>/images/<image_path>/` | 读取项目图片资源 |
| PUT | `/api/projects/<project_id>/` | 完整更新项目 |
| PATCH | `/api/projects/<project_id>/` | 局部更新项目 |
| DELETE | `/api/projects/<project_id>/` | 删除项目 |
| POST | `/api/projects/upload-package/` | 上传并解压项目压缩包 |
| GET | `/api/template-packages/<template>/download/` | 下载模板压缩包 |

## 一级分类 / 部门

### 获取一级分类列表

```http
GET /api/departments/?include_categories=1
```

响应示例：

```json
{
  "code": 0,
  "message": "ok",
  "data": [
    {
      "id": "1",
      "name": "产品研发中心",
      "sort_order": 10,
      "categories": [
        {
          "id": "1",
          "name": "产品原型",
          "department_id": "1",
          "department_name": "产品研发中心",
          "sort_order": 10
        }
      ]
    }
  ]
}
```

### 新增一级分类

```http
POST /api/departments/
```

请求体：

```json
{
  "name": "产品研发中心",
  "sort_order": 10
}
```

### 获取 / 修改 / 删除一级分类

```http
GET /api/departments/<department_id>/
PUT /api/departments/<department_id>/
PATCH /api/departments/<department_id>/
DELETE /api/departments/<department_id>/
```

说明：`department_id` 是自增整数。

## 二级分类 / 项目类型

### 获取二级分类列表

```http
GET /api/categories/?department_id=<department_id>
```

说明：`department_id` 是一级分类自增整数 ID。

### 新增二级分类

```http
POST /api/categories/
```

请求体：

```json
{
  "name": "产品原型",
  "department_id": 1,
  "sort_order": 10
}
```

### 获取 / 修改 / 删除二级分类

```http
GET /api/categories/<category_id>/
PUT /api/categories/<category_id>/
PATCH /api/categories/<category_id>/
DELETE /api/categories/<category_id>/
```

说明：`category_id` 是自增整数。

## 项目

### 获取项目列表

```http
GET /api/projects/?department_id=<department_id>&category_id=<category_id>&keyword=数字人
```

查询参数：

| 参数 | 必填 | 说明 |
| --- | --- | --- |
| department_id | 否 | 按一级分类自增 ID 过滤 |
| category_id | 否 | 按二级分类自增 ID 过滤 |
| keyword | 否 | 按项目名称模糊搜索 |

响应示例：

```json
{
  "code": 0,
  "message": "ok",
  "data": [
    {
      "id": "99999999",
      "host": "project_center_admin",
      "url": "https://ai.diyiedu.com/project_center_admin",
      "name": "数字人需求用例",
      "template": "pc",
      "template_display": "PC端",
      "description": "用于管理部门、项目类型和项目模板配置。",
      "prompt": "",
      "department": {
        "id": "1",
        "name": "产品研发中心"
      },
      "category": {
        "id": "1",
        "name": "产品原型"
      },
      "created_at": "2026-05-20 09:30:00",
      "updated_at": "2026-05-20 09:30:00",
      "template_package": {
        "name": "pc_tempate.zip",
        "template": "pc",
        "exists": true,
        "download_url": "http://127.0.0.1:8000/api/template-packages/pc/download/"
      }
    }
  ]
}
```

### 新建项目

```http
POST /api/projects/
```

请求体：

```json
{
  "host": "test",
  "name": "1",
  "template": "pc",
  "description": "1",
  "prompt": "1",
  "department_id": 1,
  "category_id": 1
}
```

字段说明：

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| host | 是 | 主机名，必须唯一，接口会返回完整地址 `https://ai.diyiedu.com/{host}` |
| name | 是 | 项目名称 |
| template | 是 | 项目模板，可选 `pc`、`mobile` |
| description | 是 | 项目描述 |
| prompt | 否 | 用户提示词 |
| department_id | 是 | 所属一级分类自增 ID |
| category_id | 是 | 所属二级分类自增 ID，必须属于当前一级分类 |

说明：新建项目成功后，后端会自动在项目工作目录下创建项目文件夹，并根据 `template` 解压对应模板包到该文件夹中。服务器默认位置为 `/usr/share/nginx/client/<project_id>/`。

模板对应关系：

- `template=pc`：解压 `templates_packages/pc_tempate.zip`
- `template=mobile`：解压 `templates_packages/wap_template.zip`

如果对应模板压缩包不存在或不是合法 zip，新建项目会失败并回滚数据库记录。

### 获取 / 修改 / 删除项目

```http
GET /api/projects/<project_id>/
PUT /api/projects/<project_id>/
PATCH /api/projects/<project_id>/
DELETE /api/projects/<project_id>/
```

说明：`project_id` 是 8 位短 UUID 字符串。

项目详情响应会额外返回 `image_assets`。后端会读取：

```text
/usr/share/nginx/client/<project_id>/assets/images/
```

下的所有图片资源，支持 `.jpg`、`.jpeg`、`.png`、`.gif`、`.webp`、`.svg`、`.bmp`、`.ico`。

响应字段示例：

```json
{
  "image_assets": [
    {
      "name": "logo.png",
      "path": "assets/images/logo.png",
      "relative_path": "logo.png",
      "size": 12345,
      "url": "http://127.0.0.1:8000/api/projects/99999999/images/logo.png/"
    }
  ]
}
```

### 读取项目图片资源

```http
GET /api/projects/<project_id>/images/<image_path>/
```

说明：

- `image_path` 是相对于 `assets/images/` 的路径。
- 例如图片文件为 `/usr/share/nginx/client/99999999/assets/images/logo.png`，访问地址为 `/api/projects/99999999/images/logo.png/`。
- 例如图片文件为 `/usr/share/nginx/client/99999999/assets/images/banner/home.png`，访问地址为 `/api/projects/99999999/images/banner/home.png/`。
- 删除项目时，后端会同步删除 `/usr/share/nginx/client/<project_id>/` 文件夹。

### 上传并解压项目压缩包

```http
POST /api/projects/upload-package/
```

请求格式：

```text
multipart/form-data
```

表单字段：

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| project_id | 是 | 8 位项目 ID |
| file | 是 | zip 压缩包文件 |

成功响应示例：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "project_id": "99999999",
    "directory": "/usr/share/nginx/client/99999999",
    "file_count": 2,
    "files": [
      "index.html",
      "assets/app.js"
    ]
  }
}
```

## 模板压缩包

### 下载模板压缩包

```http
GET /api/template-packages/<template>/download/
```

说明：

- 下载 `pc` 模板：`GET /api/template-packages/pc/download/`，对应 `pc_tempate.zip`
- 下载移动端模板：`GET /api/template-packages/mobile/download/`，对应 `wap_template.zip`
- 文件需要放在项目根目录的 `templates_packages/` 文件夹中。

## 常见错误

### ID 类型错误

```json
{
  "code": 1,
  "message": "参数错误",
  "errors": {
    "department_id": "ID 必须是整数",
    "category_id": "ID 必须是整数"
  }
}
```

### 主机名重复

```json
{
  "code": 1,
  "message": "参数错误",
  "errors": {
    "host": "主机名已存在"
  }
}
```
