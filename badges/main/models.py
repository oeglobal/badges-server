from django.db import models
from django.contrib.postgres.fields import JSONField

from django_extensions.db.models import TitleSlugDescriptionModel, TimeStampedModel
from django_extensions.db.fields import ShortUUIDField


class BadgeTemplate(TitleSlugDescriptionModel, TimeStampedModel):
    repository = models.TextField(help_text="Git Repository in https:// .. format")

    def __str__(self):
        return self.title


class BadgeInstance(TimeStampedModel):
    template = models.ForeignKey(BadgeTemplate)
    data = JSONField(blank=True)
    key = ShortUUIDField()
    external = models.TextField(unique=True)

    def __str__(self):
        return self.external
