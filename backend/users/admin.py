from django.contrib import messages, admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.html import mark_safe

from scoringengine.admin import admin_site

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
            '<a href="{}">Clone</a>'.format(
                reverse("admin:auth_user_clone", kwargs={"object_id": obj.pk})
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

    def get_urls(self):
        return [
            path(
                "<int:object_id>/clone/",
                self.clone,
                name="auth_user_clone",
            ),
        ] + super().get_urls()

    actions_column.short_description = "Actions"


admin_site.register(Catalogue, CatalogueAdmin)
admin_site.register(Group, GroupAdmin)
admin_site.register(User, UserOwnAdmin)
