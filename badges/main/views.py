from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.template import Template, Context

import toml
from pathlib import PurePath

from .models import BadgeTemplate


class PreviewIndexView(View):
    def get_context_data(self, *args, **kwargs):
        context = {
            "TEMPLATE_STATIC": "/templates/{}/".format(self.badge_template.slug),
            "TEMPLATE_SLUG": self.badge_template.slug,
        }

        config = toml.loads(
            open(PurePath(self.badge_template.repository, "config.toml")).read()
        )
        sample_data = config["sample-data"]

        context["data"] = sample_data

        return context

    @property
    def filename(self):
        if self.kwargs.get("filename"):
            return self.kwargs["filename"]

        return "index.html"

    @property
    def badge_template(self):
        return BadgeTemplate.objects.get(slug=self.kwargs["slug"])

    def get(self, request, *args, **kwargs):
        source = open(PurePath(self.badge_template.repository, self.filename)).read()
        t = Template(source)
        c = Context(self.get_context_data())

        return HttpResponse(t.render(c), request)
