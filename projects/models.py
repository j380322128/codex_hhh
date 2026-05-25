import uuid

from django.db import models
from django.utils import timezone


def generate_short_uuid():
    return uuid.uuid4().hex[:8]


class Department(models.Model):
    name = models.CharField("部门名称", max_length=80, unique=True)
    sort_order = models.PositiveIntegerField("排序", default=0)
    created_at = models.DateTimeField("创建时间", default=timezone.now)

    class Meta:
        ordering = ["sort_order", "created_at"]
        verbose_name = "部门"
        verbose_name_plural = "部门"

    def __str__(self):
        return self.name


class ProjectCategory(models.Model):
    name = models.CharField("分类名称", max_length=80)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="categories",
        verbose_name="所属部门",
    )
    sort_order = models.PositiveIntegerField("排序", default=0)
    created_at = models.DateTimeField("创建时间", default=timezone.now)

    class Meta:
        ordering = ["sort_order", "created_at"]
        unique_together = ["name", "department"]
        verbose_name = "项目类型"
        verbose_name_plural = "项目类型"

    def __str__(self):
        return self.name


class Project(models.Model):
    TEMPLATE_PC = "pc"
    TEMPLATE_MOBILE = "mobile"
    TEMPLATE_CHOICES = [
        (TEMPLATE_PC, "PC端"),
        (TEMPLATE_MOBILE, "手机端"),
    ]

    id = models.CharField(
        "项目ID",
        primary_key=True,
        max_length=8,
        default=generate_short_uuid,
        editable=False,
    )
    host = models.SlugField("主机名", max_length=120, unique=True)
    name = models.CharField("项目名称", max_length=120)
    template = models.CharField("模板", max_length=20, choices=TEMPLATE_CHOICES)
    description = models.TextField("项目描述")
    prompt = models.TextField("用户提示词", blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="projects",
        verbose_name="所属部门",
    )
    category = models.ForeignKey(
        ProjectCategory,
        on_delete=models.PROTECT,
        related_name="projects",
        verbose_name="项目类型",
    )
    created_at = models.DateTimeField("创建时间", default=timezone.now)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-created_at"]
        verbose_name = "项目"
        verbose_name_plural = "项目"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self._state.adding:
            if not self.id:
                self.id = generate_short_uuid()
            while Project.objects.filter(id=self.id).exists():
                self.id = generate_short_uuid()
        super().save(*args, **kwargs)

    @property
    def public_url(self):
        return f"https://ai.diyiedu.com/{self.host}"
