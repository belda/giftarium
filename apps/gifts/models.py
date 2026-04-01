import uuid

from django.db import models
from django.conf import settings
from webapptemplate.apps.workspaces.models import Workspace


def _default_currency():
    return getattr(settings, "DEFAULT_CURRENCY", "CZK")


class Gift(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="gifts",
    )
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="added_gifts",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_received = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["is_received", "created_at"]

    @property
    def is_surprise(self):
        return self.added_by_id != self.owner_id

    def __str__(self):
        return f"{self.name} (for {self.owner})"


class GiftExclusion(models.Model):
    """A gift excluded from a specific workspace (hidden from its members)."""

    gift = models.ForeignKey(Gift, on_delete=models.CASCADE, related_name="exclusions")
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="+")

    class Meta:
        unique_together = ("gift", "workspace")


class GiftRegistration(models.Model):
    """Someone has registered (claimed or chipped in) for a gift."""

    gift = models.ForeignKey(Gift, on_delete=models.CASCADE, related_name="registrations")
    registrant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="gift_registrations",
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("gift", "registrant")
        ordering = ["created_at"]


class WorkspaceNickname(models.Model):
    """A user's nickname within a specific workspace (set by themselves)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workspace_nicknames",
    )
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="member_nicknames",
    )
    nickname = models.CharField(max_length=100)

    class Meta:
        unique_together = ("user", "workspace")


class PendingNickname(models.Model):
    """Nickname pre-assigned to an invite email; applied when the user accepts."""

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="+")
    email = models.EmailField()
    nickname = models.CharField(max_length=100)

    class Meta:
        unique_together = ("workspace", "email")


class UserProfile(models.Model):
    """Extra profile info not in the base User model."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="gift_profile",
    )
    birthday = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user}"


class WorkspaceInviteLink(models.Model):
    """A reusable join link for a workspace — not tied to a specific email."""

    workspace = models.OneToOneField(
        Workspace, on_delete=models.CASCADE, related_name="invite_link"
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)


class WorkspaceSettings(models.Model):
    """Per-workspace configuration managed by the workspace owner/admin."""

    workspace = models.OneToOneField(
        Workspace, on_delete=models.CASCADE, related_name="gift_settings"
    )
    members_can_invite = models.BooleanField(
        default=True,
        verbose_name="Members can invite",
        help_text="Allow regular members (not just admins) to invite new people.",
    )
    currency = models.CharField(
        max_length=10,
        default=_default_currency,
        verbose_name="Currency",
        help_text="Currency symbol shown next to prices (e.g. CZK, EUR, USD).",
    )

    class Meta:
        verbose_name = "Workspace settings"
        verbose_name_plural = "Workspace settings"

    def __str__(self):
        return f"Settings for {self.workspace}"

    @classmethod
    def for_workspace(cls, workspace):
        """Return settings for a workspace, creating defaults if needed."""
        obj, _ = cls.objects.get_or_create(workspace=workspace)
        return obj
