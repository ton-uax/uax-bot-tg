from django.db import models
from django.utils.translation import ugettext_lazy as _


class GetOrNoneManager(models.Manager):

    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None


class BaseModel(models.Model):
    created = models.DateTimeField(_('Created'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated'), auto_now=True, )

    class Meta:
        abstract = True

