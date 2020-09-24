import sys
from django.urls import path
from django.urls import re_path

from django.conf import settings
from django.views.static import serve

from . import views
from .models import BadgeTemplate

app_name = "main"
urlpatterns = [
    re_path(
        r"^instance/(?P<slug>\w+)/(?P<pk>\d+)/(?P<filename>.*)$",
        views.InstanceIndexView.as_view(),
        name="instance-filename",
    ),
    path(
        "instance/<slug:slug>/<int:pk>",
        views.InstanceIndexView.as_view(),
        name="instance",
    ),
    re_path(
        r"^preview/(?P<slug>\w+)/(?P<filename>.*)$",
        views.PreviewIndexView.as_view(),
        name="preview-filename",
    ),
    path("instance/<slug:slug>", views.PreviewIndexView.as_view(), name="preview"),
]

if settings.DEBUG:
    if not ('makemigrations' in sys.argv or 'migrate' in sys.argv):
        for local_template in BadgeTemplate.objects.filter(repository__startswith="/"):
            urlpatterns += [
                re_path(
                    r"^templates/{slug}/(?P<path>.*)$".format(slug=local_template.slug),
                    serve,
                    {"document_root": local_template.repository},
                )
            ]
