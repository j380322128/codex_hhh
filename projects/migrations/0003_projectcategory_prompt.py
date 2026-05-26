from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0002_seed_initial_data"),
    ]

    operations = [
        migrations.AddField(
            model_name="projectcategory",
            name="prompt",
            field=models.TextField(blank=True, default="", verbose_name="分类提示词"),
        ),
    ]
