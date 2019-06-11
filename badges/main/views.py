from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.template import Template, Context

import toml
from pathlib import PurePath
import sarge
import magic

from .models import BadgeTemplate


class PreviewIndexView(View):
    def get_context_data(self, *args, **kwargs):
        context = {
            "TEMPLATE_STATIC": "/templates/{}/".format(self.badge_template.slug),
            "TEMPLATE_SLUG": self.badge_template.slug,
        }

        sample_data = self.config["sample-data"]
        context["data"] = sample_data

        return context

    @property
    def config(self):
        return toml.load(PurePath(self.badge_template.repository, "config.toml"))

    @property
    def filename(self):
        if self.kwargs.get("filename"):
            return self.kwargs["filename"]

        return "index.html"

    @property
    def badge_template(self):
        return BadgeTemplate.objects.get(slug=self.kwargs["slug"])

    @property
    def render_config(self):
        for template_file in self.config["files"]:
            if self.filename == template_file["filename"]:
                return template_file

    def get_render(self):
        cmd = (
            "capture-website {url} --width={width} --height={height} "
            "--type={type} --element={element} --no-default-background".format(
                width=self.render_config.get("screen_width", 1000),
                height=self.render_config.get("screen_height", 1000),
                type=self.render_config.get("format", "png"),
                element=sarge.shell_quote(
                    self.render_config.get("element", ".screenshot")
                ),
                url="http://localhost:8000/preview/oeawards/single-badge.html",
            )
        )
        p = sarge.run(cmd, stdout=sarge.Capture())

        image = p.stdout.bytes
        mime = magic.from_buffer(image, mime=True)
        return HttpResponse(image, content_type=mime)

    def get(self, request, *args, **kwargs):
        if request.GET.get("render", False):
            return self.get_render()
        else:
            source = open(
                PurePath(self.badge_template.repository, self.filename)
            ).read()
            t = Template(source)
            c = Context(self.get_context_data())

            return HttpResponse(t.render(c), request)
