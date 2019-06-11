from django.urls import path
from django.urls import re_path

from django.conf import settings
from django.views.static import serve

from . import views
from .models import BadgeTemplate

app_name = "main"
urlpatterns = [
    re_path(
        r"^preview/(?P<slug>\w+)/(?P<filename>.*)$",
        views.PreviewIndexView.as_view(),
        name="preview-filename",
    ),
    path("preview/<slug:slug>", views.PreviewIndexView.as_view(), name="preview"),
]

if settings.DEBUG:
    for local_template in BadgeTemplate.objects.filter(repository__startswith="/"):
        urlpatterns += [
            re_path(
                r"^templates/{slug}/(?P<path>.*)$".format(slug=local_template.slug),
                serve,
                {"document_root": local_template.repository},
            )
        ]
