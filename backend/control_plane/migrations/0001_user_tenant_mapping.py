# Generated migration for UserTenantMapping model

from django.conf import settings
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserTenantMapping',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='tenant_mapping', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('tenant_uuid', models.CharField(db_index=True, max_length=36)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'control_plane_user_tenant_mapping',
                'verbose_name': 'User Tenant Mapping',
                'verbose_name_plural': 'User Tenant Mappings',
            },
        ),
    ]
