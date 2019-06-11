from django.contrib import admin

from .models import BadgeTemplate, BadgeInstance


@admin.register(BadgeInstance)
class BadgeInstanceAdmin(admin.ModelAdmin):
    pass


@admin.register(BadgeTemplate)
class BadgeTemplateAdmin(admin.ModelAdmin):
    pass
