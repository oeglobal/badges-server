from django.core.management.base import BaseCommand, CommandError

from main.models import BadgeInstance, BadgeTemplate
from main.render_utils import BadgeRenderHelper


class Command(BaseCommand):
    help = "CLI utilities to manage Badge renders"

    def add_arguments(self, parser):
        parser.add_argument("-I", dest="instance", help="Individual instance")
        parser.add_argument("-A", dest="all", action="store_true", help="Render all")

    def handle(self, *args, **options):
        if options.get("instance"):
            self._render_instance(
                badge_instance=BadgeInstance.objects.get(pk=options.get("instance"))
            )

        if options.get("all"):
            for instance in BadgeInstance.objects.all():
                self._render_instance(badge_instance=instance)

    def _render_instance(self, badge_instance):
        print(badge_instance)
        render_helper = BadgeRenderHelper(badge_instance=badge_instance)
        render_helper.build_archive()
