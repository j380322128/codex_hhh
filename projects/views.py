import json
import shutil
import zipfile
from json import JSONDecodeError
from pathlib import Path, PurePosixPath

from django.conf import settings
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from django.http import FileResponse, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Department, Project, ProjectCategory


@require_http_methods(["GET"])
def health(request):
    return _success({"service": "project-management-api", "status": "ok"})


def _success(data=None, status=200):
    return JsonResponse({"code": 0, "message": "ok", "data": data}, status=status)


def _error(message, status=400, code=1, errors=None):
    payload = {"code": code, "message": message}
    if errors:
        payload["errors"] = errors
    return JsonResponse(payload, status=status)


def _read_json(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except JSONDecodeError:
        return None


def _template_package_path(template):
    filename = f"{template}.zip"
    return settings.TEMPLATE_PACKAGE_DIR / filename


def _project_files_dir(project_id):
    return settings.PROJECT_FILES_DIR / str(project_id)


def _template_package_payload(request, template):
    filename = f"{template}.zip"
    package_path = _template_package_path(template)
    download_url = reverse("projects:template_package_download", args=[template])
    return {
        "name": filename,
        "template": template,
        "exists": package_path.exists(),
        "download_url": request.build_absolute_uri(download_url),
    }


def _project_payload(project, request=None):
    return {
        "id": str(project.id),
        "host": project.host,
        "url": project.public_url,
        "name": project.name,
        "template": project.template,
        "template_display": project.get_template_display(),
        "description": project.description,
        "prompt": project.prompt,
        "department": {
            "id": str(project.department_id),
            "name": project.department.name,
        },
        "category": {
            "id": str(project.category_id),
            "name": project.category.name,
        },
        "created_at": project.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": project.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        "template_package": _template_package_payload(request, project.template)
        if request
        else None,
    }


def _department_payload(department, include_categories=False):
    payload = {
        "id": str(department.id),
        "name": department.name,
        "sort_order": department.sort_order,
    }
    if include_categories:
        payload["categories"] = [
            _category_payload(category) for category in department.categories.all()
        ]
    return payload


def _category_payload(category):
    return {
        "id": str(category.id),
        "name": category.name,
        "department_id": str(category.department_id),
        "department_name": category.department.name if hasattr(category, "department") else "",
        "sort_order": category.sort_order,
    }


def _validate_department_data(data, partial=False):
    errors = {}
    values = {}
    name = data.get("name")
    if name is None:
        if not partial:
            errors["name"] = "部门名称不能为空"
    else:
        name = name.strip() if isinstance(name, str) else name
        if not name:
            errors["name"] = "部门名称不能为空"
        else:
            values["name"] = name

    if "sort_order" in data:
        try:
            values["sort_order"] = int(data["sort_order"])
        except (TypeError, ValueError):
            errors["sort_order"] = "排序必须是整数"

    return values, errors


def _validate_category_data(data, partial=False):
    errors = {}
    values = {}
    name = data.get("name")
    if name is None:
        if not partial:
            errors["name"] = "分类名称不能为空"
    else:
        name = name.strip() if isinstance(name, str) else name
        if not name:
            errors["name"] = "分类名称不能为空"
        else:
            values["name"] = name

    department_id = data.get("department_id")
    if department_id is None:
        if not partial:
            errors["department_id"] = "所属部门不能为空"
    else:
        department = Department.objects.filter(id=department_id).first()
        if department is None:
            errors["department_id"] = "所属部门不存在"
        else:
            values["department_id"] = department.id

    if "sort_order" in data:
        try:
            values["sort_order"] = int(data["sort_order"])
        except (TypeError, ValueError):
            errors["sort_order"] = "排序必须是整数"

    return values, errors


def _validate_project_data(data, partial=False):
    errors = {}
    values = {}

    fields = {
        "host": "主机名不能为空",
        "name": "项目名称不能为空",
        "template": "模板不能为空",
        "description": "项目描述不能为空",
        "department_id": "所属部门不能为空",
        "category_id": "项目类型不能为空",
    }

    for field, message in fields.items():
        value = data.get(field)
        if value is None:
            if not partial:
                errors[field] = message
            continue
        if isinstance(value, str):
            value = value.strip()
        if value == "":
            errors[field] = message
            continue
        values[field] = value

    if "prompt" in data:
        prompt = data.get("prompt") or ""
        values["prompt"] = prompt.strip() if isinstance(prompt, str) else prompt

    if "template" in values:
        templates = {choice[0] for choice in Project.TEMPLATE_CHOICES}
        if values["template"] not in templates:
            errors["template"] = "模板只能是 pc 或 mobile"

    department = None
    category = None
    if "department_id" in values:
        department = Department.objects.filter(id=values["department_id"]).first()
        if department is None:
            errors["department_id"] = "所属部门不存在"
    if "category_id" in values:
        category = ProjectCategory.objects.filter(id=values["category_id"]).first()
        if category is None:
            errors["category_id"] = "项目类型不存在"
    if department and category and category.department_id != department.id:
        errors["category_id"] = "项目类型必须属于所属部门"

    return values, errors


def _validate_project_relation(values, project=None):
    department_id = values.get("department_id")
    category_id = values.get("category_id")
    if project is not None:
        department_id = department_id or project.department_id
        category_id = category_id or project.category_id

    if not department_id or not category_id:
        return None

    category = ProjectCategory.objects.filter(id=category_id).first()
    if category and category.department_id != department_id:
        return "项目类型必须属于所属部门"
    return None


def _validate_project_host_unique(values, project=None):
    host = values.get("host")
    if not host:
        return None

    queryset = Project.objects.filter(host=host)
    if project is not None:
        queryset = queryset.exclude(id=project.id)
    if queryset.exists():
        return "主机名已存在"
    return None


def _is_safe_zip_member(member_name):
    if "\\" in member_name:
        return False
    member_path = PurePosixPath(member_name)
    if member_path.is_absolute():
        return False
    return ".." not in member_path.parts


def _extract_project_zip(uploaded_file, target_dir):
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(uploaded_file) as archive:
            for member in archive.infolist():
                if not _is_safe_zip_member(member.filename):
                    shutil.rmtree(target_dir)
                    target_dir.mkdir(parents=True, exist_ok=True)
                    return None, "压缩包包含非法路径"
            archive.extractall(target_dir)
    except zipfile.BadZipFile:
        shutil.rmtree(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        return None, "上传文件必须是 zip 压缩包"

    extracted_files = [
        str(path.relative_to(target_dir))
        for path in target_dir.rglob("*")
        if path.is_file()
    ]
    return extracted_files, None


@csrf_exempt
@require_http_methods(["GET", "POST"])
def departments(request):
    if request.method == "GET":
        include_categories = request.GET.get("include_categories") in {"1", "true", "yes"}
        queryset = Department.objects.all()
        if include_categories:
            queryset = queryset.prefetch_related("categories")
        data = [_department_payload(item, include_categories) for item in queryset]
        return _success(data)

    data = _read_json(request)
    if data is None:
        return _error("请求体必须是合法 JSON")

    values, errors = _validate_department_data(data)
    if errors:
        return _error("参数错误", errors=errors)

    try:
        department = Department.objects.create(**values)
    except IntegrityError:
        return _error("部门名称已存在", errors={"name": "部门名称已存在"})
    return _success(_department_payload(department), status=201)


@csrf_exempt
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def department_detail(request, department_id):
    department = Department.objects.filter(id=department_id).first()
    if department is None:
        return _error("部门不存在", status=404, code=404)

    if request.method == "GET":
        return _success(_department_payload(department, include_categories=True))

    if request.method == "DELETE":
        try:
            department.delete()
        except ProtectedError:
            return _error("该部门下已有项目，不能删除")
        return _success(None)

    data = _read_json(request)
    if data is None:
        return _error("请求体必须是合法 JSON")

    values, errors = _validate_department_data(data, partial=request.method == "PATCH")
    if errors:
        return _error("参数错误", errors=errors)

    for field, value in values.items():
        setattr(department, field, value)
    try:
        department.save()
    except IntegrityError:
        return _error("部门名称已存在", errors={"name": "部门名称已存在"})
    return _success(_department_payload(department))


@csrf_exempt
@require_http_methods(["GET", "POST"])
def categories(request):
    if request.method == "GET":
        queryset = ProjectCategory.objects.select_related("department")
        department_id = request.GET.get("department_id")
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        return _success([_category_payload(item) for item in queryset])

    data = _read_json(request)
    if data is None:
        return _error("请求体必须是合法 JSON")

    values, errors = _validate_category_data(data)
    if errors:
        return _error("参数错误", errors=errors)

    try:
        category = ProjectCategory.objects.create(**values)
    except IntegrityError:
        return _error("分类名称已存在", errors={"name": "当前部门下分类名称已存在"})
    category.refresh_from_db()
    return _success(_category_payload(category), status=201)


@csrf_exempt
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def category_detail(request, category_id):
    category = ProjectCategory.objects.select_related("department").filter(id=category_id).first()
    if category is None:
        return _error("项目类型不存在", status=404, code=404)

    if request.method == "GET":
        return _success(_category_payload(category))

    if request.method == "DELETE":
        try:
            category.delete()
        except ProtectedError:
            return _error("该项目类型下已有项目，不能删除")
        return _success(None)

    data = _read_json(request)
    if data is None:
        return _error("请求体必须是合法 JSON")

    values, errors = _validate_category_data(data, partial=request.method == "PATCH")
    if errors:
        return _error("参数错误", errors=errors)

    for field, value in values.items():
        setattr(category, field, value)
    try:
        category.save()
    except IntegrityError:
        return _error("分类名称已存在", errors={"name": "当前部门下分类名称已存在"})
    category.refresh_from_db()
    return _success(_category_payload(category))


@csrf_exempt
@require_http_methods(["GET", "POST"])
def projects(request):
    if request.method == "GET":
        queryset = Project.objects.select_related("department", "category")
        department_id = request.GET.get("department_id")
        category_id = request.GET.get("category_id")
        keyword = request.GET.get("keyword")
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if keyword:
            queryset = queryset.filter(name__icontains=keyword.strip())
        return _success([_project_payload(item, request) for item in queryset])

    data = _read_json(request)
    if data is None:
        return _error("请求体必须是合法 JSON")

    values, errors = _validate_project_data(data)
    relation_error = _validate_project_relation(values)
    if relation_error:
        errors["category_id"] = relation_error
    host_error = _validate_project_host_unique(values)
    if host_error:
        errors["host"] = host_error
    if errors:
        return _error("参数错误", errors=errors)

    try:
        project = Project.objects.create(
            host=values["host"],
            name=values["name"],
            template=values["template"],
            description=values["description"],
            prompt=values.get("prompt", ""),
            department_id=values["department_id"],
            category_id=values["category_id"],
        )
    except IntegrityError:
        return _error("主机名已存在", errors={"host": "主机名已存在"})
    return _success(_project_payload(project, request), status=201)


@csrf_exempt
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def project_detail(request, project_id):
    project = Project.objects.select_related("department", "category").filter(id=project_id).first()
    if project is None:
        return _error("项目不存在", status=404, code=404)

    if request.method == "GET":
        return _success(_project_payload(project, request))

    if request.method == "DELETE":
        project.delete()
        return _success(None)

    data = _read_json(request)
    if data is None:
        return _error("请求体必须是合法 JSON")

    partial = request.method == "PATCH"
    values, errors = _validate_project_data(data, partial=partial)
    relation_error = _validate_project_relation(values, project)
    if relation_error:
        errors["category_id"] = relation_error
    host_error = _validate_project_host_unique(values, project)
    if host_error:
        errors["host"] = host_error
    if errors:
        return _error("参数错误", errors=errors)

    for field in ["host", "name", "template", "description", "prompt"]:
        if field in values:
            setattr(project, field, values[field])
    if "department_id" in values:
        project.department_id = values["department_id"]
    if "category_id" in values:
        project.category_id = values["category_id"]

    try:
        project.save()
    except IntegrityError:
        return _error("主机名已存在", errors={"host": "主机名已存在"})
    project.refresh_from_db()
    return _success(_project_payload(project, request))


@require_http_methods(["GET"])
def template_package_download(request, template):
    templates = {choice[0] for choice in Project.TEMPLATE_CHOICES}
    if template not in templates:
        return _error("模板不存在", status=404, code=404)

    package_path = _template_package_path(template)
    if not package_path.exists():
        return _error("模板压缩包不存在", status=404, code=404)

    return FileResponse(
        package_path.open("rb"),
        as_attachment=True,
        filename=package_path.name,
    )


@csrf_exempt
@require_http_methods(["POST"])
def upload_project_package(request):
    project_id = request.POST.get("project_id")
    uploaded_file = request.FILES.get("file")

    errors = {}
    if not project_id:
        errors["project_id"] = "项目 ID 不能为空"
    if uploaded_file is None:
        errors["file"] = "压缩包文件不能为空"
    if errors:
        return _error("参数错误", errors=errors)

    project = Project.objects.filter(id=project_id).first()
    if project is None:
        return _error("项目不存在", status=404, code=404)

    target_dir = _project_files_dir(project.id)
    extracted_files, error_message = _extract_project_zip(uploaded_file, target_dir)
    if error_message:
        return _error(error_message, errors={"file": error_message})

    return _success(
        {
            "project_id": str(project.id),
            "directory": str(target_dir),
            "file_count": len(extracted_files),
            "files": extracted_files,
        }
    )
