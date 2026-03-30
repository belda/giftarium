from django.db.models.signals import post_save
from django.dispatch import receiver
from webapptemplate.apps.workspaces.models import Membership


@receiver(post_save, sender=Membership)
def apply_pending_nickname(sender, instance, created, **kwargs):
    """When a user joins a workspace, apply any pre-assigned nickname."""
    if not created:
        return
    from .models import PendingNickname, WorkspaceNickname

    try:
        pending = PendingNickname.objects.get(
            workspace=instance.workspace,
            email__iexact=instance.user.email,
        )
        WorkspaceNickname.objects.get_or_create(
            user=instance.user,
            workspace=instance.workspace,
            defaults={"nickname": pending.nickname},
        )
        pending.delete()
    except PendingNickname.DoesNotExist:
        pass
