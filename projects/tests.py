import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

from django.test import override_settings
from django.test import TestCase
from django.urls import reverse

from .models import Department, Project, ProjectCategory


class ProjectCategoryPromptTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="测试部门", sort_order=99)

    def test_create_category_can_store_prompt(self):
        response = self.client.post(
            reverse("projects:categories"),
            data=json.dumps(
                {
                    "name": "测试分类",
                    "prompt": "这是二级分类提示词",
                    "department_id": self.department.id,
                    "sort_order": 10,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        payload = response.json()["data"]
        self.assertEqual(payload["prompt"], "这是二级分类提示词")

        category = ProjectCategory.objects.get(id=payload["id"])
        self.assertEqual(category.prompt, "这是二级分类提示词")

    def test_patch_category_can_update_prompt(self):
        category = ProjectCategory.objects.create(
            name="测试分类",
            prompt="旧提示词",
            department=self.department,
            sort_order=10,
        )

        response = self.client.patch(
            reverse("projects:category_detail", args=[category.id]),
            data=json.dumps({"prompt": "新提示词"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["prompt"], "新提示词")

        category.refresh_from_db()
        self.assertEqual(category.prompt, "新提示词")


class ProjectWorkspaceTests(TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.override = override_settings(PROJECT_WORKSPACE_DIR=Path(self.tempdir.name))
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.department = Department.objects.create(name="测试部门", sort_order=99)
        self.category = ProjectCategory.objects.create(
            name="测试分类",
            prompt="分类提示词",
            department=self.department,
            sort_order=10,
        )

    def test_create_project_uses_host_directory_and_writes_prompt_file(self):
        with patch("projects.views._extract_template_package_to_project") as mock_extract:
            mock_extract.return_value = ([], None)
            response = self.client.post(
                reverse("projects:projects"),
                data=json.dumps(
                    {
                        "host": "demo_host",
                        "name": "测试项目",
                        "template": "pc",
                        "description": "说明",
                        "department_id": self.department.id,
                        "category_id": self.category.id,
                    }
                ),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 201)
        project = Project.objects.get(host="demo_host")
        prompt_path = Path(self.tempdir.name) / "demo_host" / "category_prompt.md"
        self.assertEqual(prompt_path.read_text(encoding="utf-8"), "分类提示词")
        self.assertTrue(prompt_path.exists())
        self.assertEqual(project.host, "demo_host")

    def test_delete_project_removes_host_directory(self):
        project = Project.objects.create(
            host="delete_me",
            name="测试项目",
            template="pc",
            description="说明",
            prompt="",
            department=self.department,
            category=self.category,
        )
        project_dir = Path(self.tempdir.name) / "delete_me"
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "category_prompt.md").write_text("分类提示词", encoding="utf-8")

        response = self.client.delete(
            reverse("projects:project_detail", args=[project.id]),
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(project_dir.exists())

    def test_upload_package_preserves_category_prompt_file(self):
        project = Project.objects.create(
            host="upload_me",
            name="测试项目",
            template="pc",
            description="说明",
            prompt="",
            department=self.department,
            category=self.category,
        )
        project_dir = Path(self.tempdir.name) / "upload_me"
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "category_prompt.md").write_text("分类提示词", encoding="utf-8")

        zip_path = Path(self.tempdir.name) / "sample.zip"
        with tempfile.TemporaryDirectory() as tmp:
            sample_dir = Path(tmp) / "pkg"
            sample_dir.mkdir(parents=True, exist_ok=True)
            (sample_dir / "index.html").write_text("hello", encoding="utf-8")
            shutil.make_archive(str(zip_path.with_suffix("")), "zip", sample_dir)

        with zip_path.open("rb") as fh:
            response = self.client.post(
                reverse("projects:upload_project_package"),
                data={"project_id": project.id, "file": fh},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            (project_dir / "category_prompt.md").read_text(encoding="utf-8"),
            "分类提示词",
        )

    def test_template_download_returns_project_archive(self):
        project = Project.objects.create(
            host="download_me",
            name="测试项目",
            template="pc",
            description="说明",
            prompt="",
            department=self.department,
            category=self.category,
        )
        project_dir = Path(self.tempdir.name) / "download_me"
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "category_prompt.md").write_text("分类提示词", encoding="utf-8")
        (project_dir / "index.html").write_text("hello", encoding="utf-8")

        response = self.client.get(
            reverse("projects:template_package_download", args=[project.id]),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")
        self.assertEqual(response["Content-Disposition"].split("filename=")[-1].strip('"'), "download_me.zip")
