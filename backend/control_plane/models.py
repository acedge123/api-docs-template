"""
Models for control plane functionality
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class UserTenantMapping(models.Model):
    """
    Maps Django users to Repo B tenant UUIDs.
    Created during onboarding to link API keys to tenants.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='tenant_mapping',
        primary_key=True,
    )
    tenant_uuid = models.CharField(max_length=36, db_index=True)  # UUID string
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'control_plane_user_tenant_mapping'
        verbose_name = 'User Tenant Mapping'
        verbose_name_plural = 'User Tenant Mappings'

    def __str__(self):
        return f"{self.user.username} -> {self.tenant_uuid}"
