from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _


User = get_user_model()


class Catalogue(models.Model):
    master = models.OneToOneField(User, verbose_name=_("Master user"), related_name="catalogue_as_master", on_delete=models.CASCADE, primary_key=True)
    slaves = models.ManyToManyField(User, verbose_name=_("Slaves user"), related_name="catalogues_as_slave", blank=True)

    class Meta:
        verbose_name = _("Catalogue")
        verbose_name_plural = _("Catalogues")

    def __str__(self):
        return str(self.master.username)
