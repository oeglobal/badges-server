from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
import tablib

from main.models import BadgeInstance, BadgeTemplate


class Command(BaseCommand):
    help = "Imports instances of badges from Excel file"

    def add_arguments(self, parser):
        parser.add_argument("--template", help="BadgeTemplate ID")
        parser.add_argument(
            "files",
            metavar="FILE",
            type=str,
            nargs="+",
            help="Input files for importer",
        )

    def handle(self, *args, **options):
        badge_template = BadgeTemplate.objects.get(pk=options["template"])

        if options["files"]:
            for file in options["files"]:
                self._process_file(file, badge_template)

    def _process_file(self, filename, badge_template):
        dataset = tablib.Dataset().load(open(filename, "rb").read(), "xlsx")

        headers = [slugify(col) for col in dataset.headers]
        for row in dataset:
            if row[0]:
                data = dict(zip(headers, row))
                print(data)

                obj, created = BadgeInstance.objects.update_or_create(
                    template=badge_template,
                    external="{}_{}".format(badge_template.slug, data["id"]),
                    defaults={"data": data},
                )
                self.stdout.write("Imported {}".format(obj))
