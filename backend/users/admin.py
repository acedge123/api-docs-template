import os

import requests
from django.contrib import messages, admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.html import mark_safe

from scoringengine.admin import admin_site

from control_plane.models import UserTenantMapping
from users.forms import CloneUserForm, CatalogueForm
from users.models import Catalogue

User = get_user_model()


class CatalogueAdmin(admin.ModelAdmin):
    form = CatalogueForm
    list_display = ("master", "slaves_usernames")
    list_display_links = list_display

    def slaves_usernames(self, obj: Catalogue):
        slaves = obj.slaves.all()
        return ", ".join([s.username for s in slaves]) if slaves else "--"

    slaves_usernames.short_description = "Slaves"


class UserOwnAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("actions_column",)
    readonly_fields = UserAdmin.readonly_fields + ("actions_column",)

    def actions_column(self, obj: User):
        return mark_safe(
            '<a href="{}">Clone</a> | <a href="{}">Provision Tenant</a>'.format(
                reverse("admin:auth_user_clone", kwargs={"object_id": obj.pk}),
                reverse("admin:auth_user_provision_tenant", kwargs={"object_id": obj.pk}),
            )
        )

    def clone(self, request, object_id):
        try:
            obj = User.objects.get(pk=object_id)

            if request.method == "POST":
                form = CloneUserForm(data=request.POST)

                if form.is_valid():
                    form.clone_user(obj)
                    messages.add_message(request, messages.SUCCESS, "User cloned.")
                    return redirect(reverse("admin:auth_user_changelist"))

            else:
                form = CloneUserForm()

            opts = self.model._meta
            app_label = opts.app_label

            return render(
                request,
                "admin/auth/user/clone.html",
                {
                    **self.admin_site.each_context(request),
                    "opts": opts,
                    "app_label": app_label,
                    "has_view_permission": self.has_view_permission(request, obj),
                    "original": "Clone account",
                    "form": form,
                },
            )

        except User.DoesNotExist:
            return redirect(reverse("admin:auth_user_changelist"))

    def provision_tenant(self, request, object_id):
        try:
            user = User.objects.get(pk=object_id)
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect(reverse("admin:auth_user_changelist"))

        # Skip if mapping already exists
        existing = UserTenantMapping.objects.filter(user=user).first()
        if existing:
            messages.info(
                request,
                f"Tenant already provisioned for {user.username}: {existing.tenant_uuid}",
            )
            return redirect(reverse("admin:auth_user_change", kwargs={"object_id": user.pk}))

        governance_url = os.environ.get("ACP_BASE_URL") or os.environ.get("GOVERNANCE_HUB_URL")
        kernel_api_key = os.environ.get("ACP_KERNEL_KEY")

        if not governance_url or not kernel_api_key:
            messages.error(
                request,
                "ACP_BASE_URL and ACP_KERNEL_KEY must be set to provision a tenant.",
            )
            return redirect(reverse("admin:auth_user_change", kwargs={"object_id": user.pk}))

        tenant_create_url = f"{governance_url}/functions/v1/tenants-create"
        idempotency_key = f"admin-user-{user.id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {kernel_api_key}",
            "Idempotency-Key": idempotency_key,
        }
        payload = {
            "agent_id": user.username,
            "email": user.email or f"{user.username}@example.com",
        }

        try:
            response = requests.post(tenant_create_url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            tenant_result = response.json()
            tenant_data = tenant_result.get("data", tenant_result)
            tenant_uuid = tenant_data.get("tenant_uuid") or tenant_data.get("tenant_id")
        except Exception as e:
            messages.error(request, f"Tenant provisioning failed: {e}")
            return redirect(reverse("admin:auth_user_change", kwargs={"object_id": user.pk}))

        if not tenant_uuid:
            messages.error(request, "Tenant provisioning failed: no tenant_uuid returned.")
            return redirect(reverse("admin:auth_user_change", kwargs={"object_id": user.pk}))

        UserTenantMapping.objects.update_or_create(
            user=user,
            defaults={"tenant_uuid": tenant_uuid},
        )
        messages.success(
            request,
            f"Tenant provisioned for {user.username}: {tenant_uuid}",
        )
        return redirect(reverse("admin:auth_user_change", kwargs={"object_id": user.pk}))

    def get_urls(self):
        return [
            path(
                "<int:object_id>/clone/",
                self.clone,
                name="auth_user_clone",
            ),
            path(
                "<int:object_id>/provision-tenant/",
                self.provision_tenant,
                name="auth_user_provision_tenant",
            ),
        ] + super().get_urls()

    actions_column.short_description = "Actions"


admin_site.register(Catalogue, CatalogueAdmin)
admin_site.register(Group, GroupAdmin)
admin_site.register(User, UserOwnAdmin)
