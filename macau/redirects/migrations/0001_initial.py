from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Redirect",
            fields=[
                (
                    "slug",
                    models.SlugField(
                        primary_key=True, serialize=False, verbose_name="slug"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("destination", models.URLField(verbose_name="destination")),
                ("is_permanent", models.BooleanField(default=False)),
            ],
        ),
    ]
