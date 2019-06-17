from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.template import Template, Context

import toml
from pathlib import PurePath
import sarge


from .models import BadgeTemplate, BadgeInstance
from .render_utils import BadgeRenderHelper


class AbstractRenderView(View):
    data = None
    render_helper = None

    def get_context_data(self, *args, **kwargs):
        context = {
            "TEMPLATE_STATIC": "/templates/{}/".format(self.badge_template.slug),
            "TEMPLATE_SLUG": self.badge_template.slug,
            "data": self.data,
        }
        print(context["data"])

        return context

    @property
    def badge_template(self):
        return BadgeTemplate.objects.get(slug=self.kwargs["slug"])

    @property
    def filename(self):
        if self.kwargs.get("filename"):
            return self.kwargs["filename"]

        return "index.html"

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

    @property
    def config(self):
        return toml.load(PurePath(self.badge_template.repository, "config.toml"))

    def get_render(self):
        image, mime = self.render_helper.get_rendered_file(
            template_filename=self.filename, materialize=False
        )
        return HttpResponse(image, content_type=mime)


class PreviewIndexView(AbstractRenderView):
    def dispatch(self, request, *args, **kwargs):
        self.data = self.config["sample-data"]
        self.render_helper = BadgeRenderHelper(
            badge_template=self.badge_template, data=self.data
        )

        return super().dispatch(request, *args, **kwargs)


class InstanceIndexView(AbstractRenderView):
    @property
    def badge_instance(self):
        return BadgeInstance.objects.get(pk=self.kwargs["pk"])

    def dispatch(self, request, *args, **kwargs):
        self.data = self.badge_instance.data
        self.render_helper = BadgeRenderHelper(badge_instance=self.badge_instance)

        return super().dispatch(request, *args, **kwargs)
