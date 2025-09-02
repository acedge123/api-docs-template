from django import forms

from users.helpers import clone_account
from django.contrib.auth import get_user_model
from django.contrib.admin.widgets import FilteredSelectMultiple

from users.models import Catalogue

User = get_user_model()


class CloneUserForm(forms.Form):
    username = forms.CharField(required=True, label="Username")
    password1 = forms.CharField(
        required=True, label="Password", widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        required=True, label="Password repeat", widget=forms.PasswordInput
    )
    copy_quiz_structure = forms.BooleanField(
        label="Copy quiz structure", required=False
    )
    copy_scoring_model = forms.BooleanField(label="Copy scoring model", required=False)
    copy_leads = forms.BooleanField(label="Copy leads and answers", required=False)

    def clean_username(self):
        if User.objects.filter(username=self.cleaned_data["username"]).exists():
            raise forms.ValidationError("User with this username already exists.")

        return self.cleaned_data["username"]

    def clean_password2(self):
        if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
            raise forms.ValidationError("Passwords are not the same.")

        return self.cleaned_data["password2"]

    def clean_copy_scoring_model(self):
        if self.cleaned_data["copy_scoring_model"] and not self.cleaned_data.get(
            "copy_quiz_structure", False
        ):
            raise forms.ValidationError(
                "You cannot copy scoring model without quiz structure"
            )

        return self.cleaned_data["copy_scoring_model"]

    def clean_copy_leads(self):
        if self.cleaned_data["copy_leads"] and (
            not self.cleaned_data.get("copy_scoring_model", False)
            or not self.cleaned_data.get("copy_quiz_structure", False)
        ):
            raise forms.ValidationError(
                "You cannot copy leads and answers without scoring model and quiz structure"
            )

        return self.cleaned_data["copy_leads"]

    def clone_user(self, source_user: User):
        user = User.objects.create(
            username=self.cleaned_data["username"], is_staff=True, is_active=True
        )
        user.set_password(self.cleaned_data["password1"])
        user.save()

        user.user_permissions.set(source_user.user_permissions.all())
        user.groups.set(source_user.groups.all())

        clone_account(
            source_user,
            user,
            self.cleaned_data.get("copy_quiz_structure", False),
            self.cleaned_data.get("copy_scoring_model", False),
            self.cleaned_data.get("copy_leads", False),
        )

        return user


class CatalogueForm(forms.ModelForm):
    master = forms.ModelChoiceField(
        required=True,
        queryset=User.objects.filter(catalogues_as_slave__isnull=True).all(),
    )
    slaves = forms.ModelMultipleChoiceField(
        required=False,
        queryset=User.objects.filter(catalogue_as_master__isnull=True).all(),
        widget=FilteredSelectMultiple("Slaves", is_stacked=False),
    )

    class Meta:
        model = Catalogue
        fields = "__all__"
