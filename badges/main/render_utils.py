from django.conf import settings
from django.urls import reverse
from django.core.files.base import ContentFile
from django.core.files import File

import tempfile
import os
import zipfile

import sarge
import toml
import magic
from pathlib import PurePath

from .models import Media


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

        file_format = render_config.get("format", "png")
        if file_format == "pdf":
            f = tempfile.NamedTemporaryFile(delete=False)
            tmppdf = f.name
            f.close()

            cmd = (
                "node {chrome_pdf_bin} "
                "--paper-width 8.27 --paper-height 11.69"
                "--no-margins --landscape --include-background --url {url} --pdf {tmppdf}".format(
                    chrome_pdf_bin=settings.CHROME_PDF_BIN,
                    tmppdf=tmppdf,
                    url="{}{}".format(settings.RENDER_PREFIX_URL, url),
                )
            )
            sarge.run(cmd, stdout=sarge.Capture())

            f = open(tmppdf, "rb")
            image = f.read()
            f.close()
            os.unlink(f.name)

        else:
            cmd = (
                "capture-website {url} --width={width} --height={height} "
                "--type={type} --element={element} --no-default-background".format(
                    width=render_config.get("screen_width", 1000),
                    height=render_config.get("screen_height", 1000),
                    type=file_format,
                    element=sarge.shell_quote(
                        render_config.get("element", ".screenshot")
                    ),
                    url="{}{}".format(settings.RENDER_PREFIX_URL, url),
                )
            )
            p = sarge.run(cmd, stdout=sarge.Capture())

            image = p.stdout.bytes

        mime = magic.from_buffer(image, mime=True)
        return image, mime

    def get_rendered_file(self, *, template_filename=None, materialize=False):
        if materialize:
            render_config = self.render_config(template_filename)
            file_format = render_config.get("format", "png")

            file_stem = PurePath(template_filename).stem
            media_filename = "{}.{}".format(file_stem, file_format)

            image, mime = self._render(template_filename=template_filename)
            media = Media(
                instance=self.badge_instance,
                kind="media",
                original_filename=media_filename.replace("single-", ""),
            )

            media.file.save(media_filename, content=ContentFile(image))
            media.save()
            return media

        else:
            return self._render(template_filename=template_filename)

    def build_archive(self):
        Media.objects.filter(instance=self.badge_instance).delete()

        rendered_files = []
        for tf in self.config["files"]:
            media = self.get_rendered_file(
                template_filename=tf["filename"], materialize=True
            )
            rendered_files.append(media)

        f = tempfile.NamedTemporaryFile(delete=False)
        zipf_name = f.name
        f.close()

        archive_name = self.badge_instance.external

        zipf = zipfile.ZipFile(zipf_name, "w", zipfile.ZIP_DEFLATED)
        for tf in rendered_files:
            arcname = tf.original_filename
            zipf.write(tf.file.path, arcname="{}/{}".format(archive_name, arcname))
        zipf.close()

        archive = Media(instance=self.badge_instance, kind="archive")
        archive.file.save(
            name=self.badge_instance.external + ".zip",
            content=File(open(zipf_name, "rb")),
            save=True,
        )
        archive.save()
