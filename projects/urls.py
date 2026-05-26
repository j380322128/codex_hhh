from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("health/", views.health, name="health"),
    path("departments/", views.departments, name="departments"),
    path("departments/<int:department_id>/", views.department_detail, name="department_detail"),
    path("categories/", views.categories, name="categories"),
    path("categories/<int:category_id>/", views.category_detail, name="category_detail"),
    path("projects/", views.projects, name="projects"),
    path(
        "projects/upload-package/",
        views.upload_project_package,
        name="upload_project_package",
    ),
    path(
        "projects/<str:project_id>/images/<path:image_path>/",
        views.project_image_asset,
        name="project_image_asset",
    ),
    path("projects/<str:project_id>/", views.project_detail, name="project_detail"),
    path(
        "template-packages/<str:project_id>/download/",
        views.template_package_download,
        name="template_package_download",
    ),
]
