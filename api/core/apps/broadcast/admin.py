from django.contrib import admin

from core.apps.broadcast import models as broadcast_models


@admin.register(broadcast_models.BroadcastQuery)
class BroadcastAdmin(admin.ModelAdmin):
    list_display = ("text", "action", "keyboard", "status",)


