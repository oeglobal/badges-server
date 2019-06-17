from django.conf import settings
from django.urls import reverse

import sarge
import toml
import magic
from pathlib import PurePath


class BadgeRenderHelper:
    def __init__(self, badge_instance=None, badge_template=None, data=None):
        self.badge_instance = badge_instance

        if self.badge_instance:
            self.badge_template = badge_instance.template
        else:
            self.badge_template = badge_template

        if badge_instance:
            self.data = badge_instance.data
        else:
            self.data = data

    @property
    def config(self):
        return toml.load(PurePath(self.badge_template.repository, "config.toml"))

    def render_config(self, template_filename):
        for tf in self.config["files"]:
            if template_filename == tf["filename"]:
                return tf

    def _render(self, template_filename):
        render_config = self.render_config(template_filename)
        if self.badge_instance:
            url = reverse(
                "main:instance-filename",
                kwargs={
                    "slug": self.badge_template.slug,
                    "pk": self.badge_instance.pk,
                    "filename": template_filename,
                },
            )
        else:
            url = reverse(
                "main:preview-filename",
                kwargs={
                    "slug": self.badge_template.slug,
                    "filename": template_filename,
                },
            )
        cmd = (
            "capture-website {url} --width={width} --height={height} "
            "--type={type} --element={element} --no-default-background".format(
                width=render_config.get("screen_width", 1000),
                height=render_config.get("screen_height", 1000),
                type=render_config.get("format", "png"),
                element=sarge.shell_quote(render_config.get("element", ".screenshot")),
                url="{}{}".format(settings.RENDER_PREFIX_URL, url),
            )
        )
        print(cmd)
        p = sarge.run(cmd, stdout=sarge.Capture())

        image = p.stdout.bytes
        mime = magic.from_buffer(image, mime=True)
        return image, mime

    def get_rendered_file(self, template_filename, materialize=False):
        if materialize:
            raise NotImplementedError
        else:
            return self._render(template_filename=template_filename)
