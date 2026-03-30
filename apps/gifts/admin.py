from django.contrib import admin
from .models import Gift, GiftExclusion, GiftRegistration, WorkspaceSettings


class GiftExclusionInline(admin.TabularInline):
    model = GiftExclusion
    extra = 0


class GiftRegistrationInline(admin.TabularInline):
    model = GiftRegistration
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(WorkspaceSettings)
class WorkspaceSettingsAdmin(admin.ModelAdmin):
    list_display = ("workspace", "members_can_invite")
    list_editable = ("members_can_invite",)


@admin.register(Gift)
class GiftAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "added_by", "price", "is_received", "created_at")
    list_filter = ("is_received",)
    search_fields = ("name", "owner__email", "added_by__email")
    inlines = [GiftExclusionInline, GiftRegistrationInline]
