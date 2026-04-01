from django.utils.translation import gettext_lazy as _
from webapptemplate.app_config import WebAppConfig
from webapptemplate.settings_panels import WorkspaceSettingsPanel, UserSettingsPanel

from .panels import workspace_settings_panel_view, user_profile_panel_view


class GiftsConfig(WebAppConfig):
    name = "apps.gifts"
    default_auto_field = "django.db.models.BigAutoField"
    url_prefix = "gifts/"
    nav_items = [
        {"url": "gifts:my_list", "label": _("My Wishes"),      "icon": "list-check", "order": 10},
        {"url": "gifts:index",   "label": _("Others' Wishes"), "icon": "gift",        "order": 20},
        {"url": "gifts:groups",  "label": _("Members"),        "icon": "users",       "order": 30},
    ]

    workspace_settings_panels = [
        WorkspaceSettingsPanel(
            id="gift_settings",
            title=_("Other Settings"),
            description=_("Currency and permissions for this group."),
            template="gifts/panels/workspace_settings.html",
            view_func=workspace_settings_panel_view,
            admin_only=True,
            order=10,
        ),
    ]

    user_settings_panels = [
        UserSettingsPanel(
            id="gift_profile",
            title=_("Gift Profile"),
            description=_("Your birthday lets group members know when to celebrate."),
            template="gifts/panels/user_profile.html",
            view_func=user_profile_panel_view,
            order=10,
        ),
    ]

    def ready(self):
        super().ready()
        from . import signals  # noqa: F401
