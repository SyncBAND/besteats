from django.db import models
from django.utils import timezone


NULLABLE = dict(null=True, blank=True)


class CreatedModifiedMixin(models.Model):

    created = models.DateTimeField(editable=False, default=timezone.now)
    modified = models.DateTimeField(editable=False, default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()

        self.modified = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
