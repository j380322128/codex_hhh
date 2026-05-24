from django.contrib import admin

from .models import Department, Project, ProjectCategory


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name", "sort_order", "created_at"]
    search_fields = ["name"]


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "department", "sort_order", "created_at"]
    list_filter = ["department"]
    search_fields = ["name"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["name", "host", "template", "department", "category", "updated_at"]
    list_filter = ["department", "category", "template"]
    search_fields = ["name", "host", "description"]
    readonly_fields = ["id", "created_at", "updated_at"]
