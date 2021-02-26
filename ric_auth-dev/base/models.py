from django.conf import settings
from django.db import models


class SoftDeleteMixin(models.Model):
    class Meta:
        abstract = True

    is_deleted = models.BooleanField(default=False)

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()


class CreatedUpdatedSoftDeleteMixin(SoftDeleteMixin):
    class Meta:
        abstract = True

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)

    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)
