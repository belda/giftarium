import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gifts", "0003_userprofile_pendingnickname"),
        ("workspaces", "0004_apikey"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="WorkspaceInviteLink",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("token", models.UUIDField(default=uuid.uuid4, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("workspace", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="invite_link", to="workspaces.workspace")),
                ("created_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
