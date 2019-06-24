from django.contrib import admin

from .models import BadgeTemplate, BadgeInstance, Media


@admin.register(BadgeInstance)
class BadgeInstanceAdmin(admin.ModelAdmin):
    readonly_fields = ("key",)


@admin.register(BadgeTemplate)
class BadgeTemplateAdmin(admin.ModelAdmin):
    pass


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    pass
