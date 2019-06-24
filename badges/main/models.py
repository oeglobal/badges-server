from django.db import models
from django.urls import reverse
from django.contrib.postgres.fields import JSONField

from django_extensions.db.models import TitleSlugDescriptionModel, TimeStampedModel
from django_extensions.db.fields import ShortUUIDField


class BadgeTemplate(TitleSlugDescriptionModel, TimeStampedModel):
    repository = models.TextField(
        help_text="Git Repository in https:// or /Users/.. format"
    )

    def get_absolute_url(self):
        return reverse("main:preview", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title


class BadgeInstance(TimeStampedModel):
    template = models.ForeignKey(BadgeTemplate, on_delete=models.CASCADE)
    data = JSONField(blank=True)
    key = ShortUUIDField()
    external = models.TextField(unique=True)

    def __str__(self):
        return self.external

    def save(self, *args, **kwargs):
        # TODO: check for _loaded_values
        # https://docs.djangoproject.com/en/2.2/ref/models/instances/#customizing-model-loading
        super().save(*args, **kwargs)

    def build_archive(self):
        pass


MEDIA_TYPE_CHOICES = (("archive", "Archive"), ("media", "Individual file"))


class Media(TimeStampedModel):
    instance = models.ForeignKey(BadgeInstance, on_delete=models.CASCADE)
    file = models.FileField(upload_to="media/rendered")
    kind = models.CharField(choices=MEDIA_TYPE_CHOICES, max_length=64)

    def __str__(self):
        return self.file.name
