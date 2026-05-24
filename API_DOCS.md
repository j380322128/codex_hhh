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

- 所有数据主键均为 UUID 字符串。
- 时间格式为 `YYYY-MM-DD HH:mm:ss`。
- 项目模板 `template` 可选值为 `pc`、`mobile`。
- 项目根目录下的 `templates_packages/` 文件夹用于存放模板压缩包：`pc.zip`、`mobile.zip`。

## 接口总览

| 方法 | 地址 | 说明 |
| --- | --- | --- |
| GET | `/api/health/` | 健康检查 |
| GET | `/api/departments/` | 获取一级分类列表 |
| POST | `/api/departments/` | 新增一级分类 |
| GET | `/api/departments/<department_uuid>/` | 获取一级分类详情 |
| PUT | `/api/departments/<department_uuid>/` | 完整更新一级分类 |
| PATCH | `/api/departments/<department_uuid>/` | 局部更新一级分类 |
| DELETE | `/api/departments/<department_uuid>/` | 删除一级分类 |
| GET | `/api/categories/` | 获取二级分类列表 |
| POST | `/api/categories/` | 新增二级分类 |
| GET | `/api/categories/<category_uuid>/` | 获取二级分类详情 |
| PUT | `/api/categories/<category_uuid>/` | 完整更新二级分类 |
| PATCH | `/api/categories/<category_uuid>/` | 局部更新二级分类 |
| DELETE | `/api/categories/<category_uuid>/` | 删除二级分类 |
| GET | `/api/projects/` | 获取项目列表 |
| POST | `/api/projects/` | 新建项目 |
| GET | `/api/projects/<project_uuid>/` | 获取项目详情 |
| PUT | `/api/projects/<project_uuid>/` | 完整更新项目 |
| PATCH | `/api/projects/<project_uuid>/` | 局部更新项目 |
| DELETE | `/api/projects/<project_uuid>/` | 删除项目 |
| POST | `/api/projects/upload-package/` | 上传并解压项目压缩包 |
| GET | `/api/template-packages/<template>/download/` | 下载模板压缩包 |

## 一级分类 / 部门

### 获取一级分类列表

```http
GET /api/departments/?include_categories=1
```

查询参数：

| 参数 | 必填 | 说明 |
| --- | --- | --- |
| include_categories | 否 | 传 `1` 时返回部门下的二级分类 |

响应示例：

```json
{
  "code": 0,
  "message": "ok",
  "data": [
    {
      "id": "11111111-1111-4111-8111-111111111111",
      "name": "产品研发中心",
      "sort_order": 10,
      "categories": [
        {
          "id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
          "name": "产品原型",
          "department_id": "11111111-1111-4111-8111-111111111111",
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

### 获取一级分类详情

```http
GET /api/departments/<department_uuid>/
```

### 修改一级分类

```http
PATCH /api/departments/<department_uuid>/
```

完整覆盖更新也可使用：

```http
PUT /api/departments/<department_uuid>/
```

请求体：

```json
{
  "name": "教研中心",
  "sort_order": 20
}
```

### 删除一级分类

```http
DELETE /api/departments/<department_uuid>/
```

说明：该一级分类下已有项目时不能删除。

## 二级分类 / 项目类型

### 获取二级分类列表

```http
GET /api/categories/?department_id=<department_uuid>
```

查询参数：

| 参数 | 必填 | 说明 |
| --- | --- | --- |
| department_id | 否 | 按一级分类 UUID 过滤 |

响应示例：

```json
{
  "code": 0,
  "message": "ok",
  "data": [
    {
      "id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
      "name": "产品原型",
      "department_id": "11111111-1111-4111-8111-111111111111",
      "department_name": "产品研发中心",
      "sort_order": 10
    }
  ]
}
```

### 新增二级分类

```http
POST /api/categories/
```

请求体：

```json
{
  "name": "产品原型",
  "department_id": "11111111-1111-4111-8111-111111111111",
  "sort_order": 10
}
```

### 获取二级分类详情

```http
GET /api/categories/<category_uuid>/
```

### 修改二级分类

```http
PATCH /api/categories/<category_uuid>/
```

完整覆盖更新也可使用：

```http
PUT /api/categories/<category_uuid>/
```

请求体：

```json
{
  "name": "企业宣传",
  "department_id": "11111111-1111-4111-8111-111111111111",
  "sort_order": 20
}
```

### 删除二级分类

```http
DELETE /api/categories/<category_uuid>/
```

说明：该二级分类下已有项目时不能删除。

## 项目

### 获取项目列表

```http
GET /api/projects/?department_id=<department_uuid>&category_id=<category_uuid>&keyword=数字人
```

查询参数：

| 参数 | 必填 | 说明 |
| --- | --- | --- |
| department_id | 否 | 按一级分类 UUID 过滤 |
| category_id | 否 | 按二级分类 UUID 过滤 |
| keyword | 否 | 按项目名称模糊搜索 |

响应示例：

```json
{
  "code": 0,
  "message": "ok",
  "data": [
    {
      "id": "99999999-9999-4999-8999-999999999999",
      "host": "project_center_admin",
      "url": "https://ai.diyiedu.com/project_center_admin",
      "name": "数字人需求用例",
      "template": "pc",
      "template_display": "PC端",
      "description": "用于管理部门、项目类型和项目模板配置。",
      "prompt": "",
      "department": {
        "id": "11111111-1111-4111-8111-111111111111",
        "name": "产品研发中心"
      },
      "category": {
        "id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        "name": "产品原型"
      },
      "created_at": "2026-05-20 09:30:00",
      "updated_at": "2026-05-20 09:30:00",
      "template_package": {
        "name": "pc.zip",
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
  "host": "project_center_admin",
  "name": "数字人需求用例",
  "template": "pc",
  "description": "用于管理部门、项目类型和项目模板配置。",
  "prompt": "请输入给用户的提示词",
  "department_id": "11111111-1111-4111-8111-111111111111",
  "category_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
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
| department_id | 是 | 所属一级分类 UUID |
| category_id | 是 | 所属二级分类 UUID，必须属于当前一级分类 |

### 获取项目详情

```http
GET /api/projects/<project_uuid>/
```

响应中的 `template_package` 会根据项目的 `template` 自动返回对应模板压缩包：

```json
{
  "name": "pc.zip",
  "template": "pc",
  "exists": true,
  "download_url": "http://127.0.0.1:8000/api/template-packages/pc/download/"
}
```

说明：

- `template=pc` 时对应项目根目录 `templates_packages/pc.zip`。
- `template=mobile` 时对应项目根目录 `templates_packages/mobile.zip`。
- `exists=false` 表示压缩包文件还没有放到指定目录，下载接口会返回 404。

### 修改项目

```http
PATCH /api/projects/<project_uuid>/
```

说明：支持局部更新。

请求体示例：

```json
{
  "name": "新的项目名称",
  "description": "新的项目描述"
}
```

完整覆盖更新也可使用：

```http
PUT /api/projects/<project_uuid>/
```

### 删除项目

```http
DELETE /api/projects/<project_uuid>/
```

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
| project_id | 是 | 项目 UUID |
| file | 是 | zip 压缩包文件 |

处理逻辑：

- 在项目根目录的 `project_files/` 下寻找项目 ID 对应的文件夹。
- 如果文件夹不存在，则自动创建。
- 解压前会清空该项目 ID 对应的文件夹。
- 校验 zip 内部路径，禁止 `../`、绝对路径等非法路径。
- 解压成功后，压缩包内容会放入 `project_files/<project_id>/`。

成功响应示例：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "project_id": "99999999-9999-4999-8999-999999999999",
    "directory": "/Users/jihao/Desktop/hhh/codex_hhh/project_files/99999999-9999-4999-8999-999999999999",
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

路径参数：

| 参数 | 必填 | 说明 |
| --- | --- | --- |
| template | 是 | 可选 `pc`、`mobile` |

说明：

- 下载 `pc` 模板：`GET /api/template-packages/pc/download/`
- 下载移动端模板：`GET /api/template-packages/mobile/download/`
- 文件需要放在项目根目录的 `templates_packages/` 文件夹中。

## 常见错误

### 参数错误

```json
{
  "code": 1,
  "message": "参数错误",
  "errors": {
    "category_id": "项目类型必须属于所属部门"
  }
}
```

### 数据不存在

```json
{
  "code": 404,
  "message": "项目不存在"
}
```

### 主机名重复

```json
{
  "code": 1,
  "message": "主机名已存在",
  "errors": {
    "host": "主机名已存在"
  }
}
```
