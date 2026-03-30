from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.translation import gettext as _

from datetime import date, timedelta

from django.conf import settings as django_settings
from django.core.mail import send_mail
from django.utils import timezone

from webapptemplate.apps.workspaces.models import Invitation, Membership, Workspace

from .models import Gift, GiftExclusion, GiftRegistration, PendingNickname, UserProfile, WorkspaceInviteLink, WorkspaceNickname, WorkspaceSettings
from .forms import GiftForm

User = get_user_model()


def _visible_gifts_qs(owner, workspace):
    """Gifts owned by `owner` that are visible in `workspace` (not excluded)."""
    excluded_ids = GiftExclusion.objects.filter(
        workspace=workspace
    ).values_list("gift_id", flat=True)
    return Gift.objects.filter(owner=owner).exclude(id__in=excluded_ids)


@login_required
def index(request):
    """List all workspace members and their wishlist counts."""
    workspace = getattr(request, "workspace", None)
    if not workspace:
        messages.info(request, _("Create or join a group to see wishlists."))
        return redirect("dashboard:index")

    memberships = (
        Membership.objects.filter(workspace=workspace)
        .select_related("user")
        .exclude(user=request.user)
    )

    nickname_map = {
        wn.user_id: wn.nickname
        for wn in WorkspaceNickname.objects.filter(workspace=workspace)
    }

    members_data = []
    for m in memberships:
        count = _visible_gifts_qs(m.user, workspace).filter(is_received=False).count()
        members_data.append({
            "user": m.user,
            "gift_count": count,
            "nickname": nickname_map.get(m.user_id),
        })

    return render(request, "gifts/index.html", {"members": members_data})


@login_required
def my_list(request):
    """Manage own wishlist."""
    workspace = getattr(request, "workspace", None)

    membership = (
        Membership.objects.filter(user=request.user, workspace=workspace).first()
        if workspace else None
    )
    ws_settings = WorkspaceSettings.for_workspace(workspace) if workspace else None
    members_can_invite = ws_settings.members_can_invite if ws_settings else False
    can_invite = membership is not None and (membership.is_admin or members_can_invite)

    if request.method == "POST" and request.POST.get("action") == "invite":
        if can_invite and workspace:
            email = request.POST.get("email", "").strip().lower()
            nickname = request.POST.get("invite_nickname", "").strip()
            if not email:
                messages.error(request, _("Please enter an email address."))
                return redirect("gifts:my_list")
            if Membership.objects.filter(workspace=workspace, user__email=email).exists():
                messages.warning(request, _("%(email)s is already a member of this group.") % {"email": email})
                return redirect("gifts:my_list")

            invitation, created = Invitation.objects.get_or_create(
                workspace=workspace,
                email=email,
                defaults={"invited_by": request.user},
            )
            if not created:
                invitation.invited_by = request.user
                invitation.accepted_at = None
                invitation.expires_at = timezone.now() + timedelta(days=7)
                invitation.save()

            if nickname:
                PendingNickname.objects.update_or_create(
                    workspace=workspace,
                    email=email,
                    defaults={"nickname": nickname},
                )
            else:
                PendingNickname.objects.filter(workspace=workspace, email=email).delete()

            invite_url = request.build_absolute_uri(
                f"/workspaces/accept-invite/{invitation.token}/"
            )
            app_name = getattr(django_settings, "APP_NAME", "Giftarium")
            send_mail(
                subject=_("You've been invited to %(workspace)s on %(app)s") % {"workspace": workspace.name, "app": app_name},
                message=_("%(user)s has invited you to join \"%(workspace)s\" on %(app)s.\n\nAccept here: %(url)s") % {
                    "user": request.user.display_name,
                    "workspace": workspace.name,
                    "app": app_name,
                    "url": invite_url,
                },
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
            request.session["my_list_invite_url"] = invite_url
            request.session["my_list_invite_email"] = email
            messages.success(request, _("Invitation sent to %(email)s!") % {"email": email})
        return redirect("gifts:my_list")

    # Gifts I added myself (own, non-surprise)
    own_gifts = list(
        Gift.objects.filter(owner=request.user, added_by=request.user)
        .prefetch_related("registrations__registrant", "exclusions")
    )

    surprise_count = Gift.objects.filter(
        owner=request.user
    ).exclude(added_by=request.user).count()

    my_workspaces = list(
        Workspace.objects.filter(memberships__user=request.user).order_by("name")
    )

    # Build exclusion map: {gift_id: set of excluded workspace_ids}
    exclusion_map = {}
    for excl in GiftExclusion.objects.filter(
        gift__owner=request.user, gift__added_by=request.user
    ):
        exclusion_map.setdefault(excl.gift_id, set()).add(excl.workspace_id)

    # Annotate gifts so templates can check `gift.excluded_ws_ids`
    for gift in own_gifts:
        gift.excluded_ws_ids = exclusion_map.get(gift.pk, set())

    invite_url = request.session.pop("my_list_invite_url", None)
    invite_email = request.session.pop("my_list_invite_email", None)

    invite_link_url = None
    if workspace and can_invite:
        invite_link_obj, _created = WorkspaceInviteLink.objects.get_or_create(
            workspace=workspace,
            defaults={"created_by": request.user},
        )
        invite_link_url = request.build_absolute_uri(
            reverse("gifts:join_via_link", args=[invite_link_obj.token])
        )

    form = GiftForm()
    if request.method == "POST":
        form = GiftForm(request.POST)
        if form.is_valid():
            gift = form.save(commit=False)
            gift.owner = request.user
            gift.added_by = request.user
            gift.save()
            messages.success(request, _("Gift added to your wishlist!"))
            return redirect("gifts:my_list")

    return render(request, "gifts/my_list.html", {
        "own_gifts": own_gifts,
        "surprise_count": surprise_count,
        "my_workspaces": my_workspaces,
        "form": form,
        "can_invite": can_invite,
        "workspace": workspace,
        "invite_url": invite_url,
        "invite_email": invite_email,
        "invite_link_url": invite_link_url,
    })


@login_required
def edit_gift(request, pk):
    """Edit a gift — only the person who added it can edit."""
    gift = get_object_or_404(Gift, pk=pk, added_by=request.user)
    form = GiftForm(request.POST or None, instance=gift)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Gift updated!"))
        if gift.owner == request.user:
            return redirect("gifts:my_list")
        return redirect("gifts:user_list", user_pk=gift.owner.pk)
    return render(request, "gifts/edit_gift.html", {"form": form, "gift": gift})


@login_required
def delete_gift(request, pk):
    """Delete a gift — only the person who added it can delete."""
    gift = get_object_or_404(Gift, pk=pk, added_by=request.user)
    if request.method == "POST":
        owner_pk = gift.owner.pk
        is_own = gift.owner == request.user
        gift.delete()
        messages.success(request, _("Gift removed."))
        return redirect("gifts:my_list") if is_own else redirect("gifts:user_list", user_pk=owner_pk)
    return redirect("gifts:my_list")


@login_required
def mark_received(request, pk):
    """Toggle the is_received flag on a gift (owner only)."""
    if request.method == "POST":
        gift = get_object_or_404(Gift, pk=pk, owner=request.user)
        gift.is_received = not gift.is_received
        gift.save()
    return redirect("gifts:my_list")


@login_required
def toggle_exclusion(request, gift_pk, workspace_pk):
    """Exclude or include a gift for a specific workspace."""
    gift = get_object_or_404(Gift, pk=gift_pk, owner=request.user, added_by=request.user)
    workspace = get_object_or_404(Workspace, pk=workspace_pk)
    if not Membership.objects.filter(user=request.user, workspace=workspace).exists():
        return HttpResponse(status=403)
    excl, created = GiftExclusion.objects.get_or_create(gift=gift, workspace=workspace)
    if not created:
        excl.delete()
    return redirect("gifts:my_list")


@login_required
def user_list(request, user_pk):
    """View another member's wishlist within the current workspace."""
    workspace = getattr(request, "workspace", None)
    if not workspace:
        return redirect("dashboard:index")

    target_user = get_object_or_404(User, pk=user_pk)
    if target_user == request.user:
        return redirect("gifts:my_list")

    if not Membership.objects.filter(user=target_user, workspace=workspace).exists():
        messages.error(request, _("This user is not in your current group."))
        return redirect("gifts:index")

    gifts = list(
        _visible_gifts_qs(target_user, workspace)
        .prefetch_related("registrations__registrant")
        .select_related("added_by")
    )

    my_registration_ids = set(
        GiftRegistration.objects.filter(
            registrant=request.user,
            gift__owner=target_user,
        ).values_list("gift_id", flat=True)
    )

    # Annotate each gift with whether the current user is registered
    for gift in gifts:
        gift.i_am_registered = gift.pk in my_registration_ids

    surprise_form = GiftForm()

    target_display = (
        WorkspaceNickname.objects.filter(user=target_user, workspace=workspace)
        .values_list("nickname", flat=True)
        .first()
    ) or target_user.display_name

    return render(request, "gifts/user_list.html", {
        "target_user": target_user,
        "target_display": target_display,
        "gifts": gifts,
        "surprise_form": surprise_form,
    })


@login_required
def add_surprise(request, user_pk):
    """Add a surprise gift to another user's wishlist."""
    workspace = getattr(request, "workspace", None)
    if not workspace:
        return redirect("dashboard:index")

    target_user = get_object_or_404(User, pk=user_pk)
    if target_user == request.user:
        return redirect("gifts:my_list")

    if not Membership.objects.filter(user=target_user, workspace=workspace).exists():
        return redirect("gifts:index")

    if request.method == "POST":
        form = GiftForm(request.POST)
        if form.is_valid():
            gift = form.save(commit=False)
            gift.owner = target_user
            gift.added_by = request.user
            gift.save()
            messages.success(
                request,
                _("Surprise gift added to %(name)s's wishlist!") % {"name": target_user.display_name},
            )
        else:
            messages.error(request, _("Gift name is required."))

    return redirect("gifts:user_list", user_pk=user_pk)


@login_required
def register_gift(request, pk):
    """Register for (or chip in on) a gift."""
    if request.method != "POST":
        return redirect("gifts:index")

    gift = get_object_or_404(Gift, pk=pk)
    workspace = getattr(request, "workspace", None)

    if gift.owner == request.user:
        return HttpResponse(status=400)

    # Ensure the current user shares at least one workspace with the gift owner.
    shares_workspace = Membership.objects.filter(
        workspace__memberships__user=gift.owner,
        user=request.user,
    ).exists()
    if not shares_workspace:
        return HttpResponse(status=403)

    if workspace and GiftExclusion.objects.filter(gift=gift, workspace=workspace).exists():
        return HttpResponse(status=403)

    GiftRegistration.objects.get_or_create(gift=gift, registrant=request.user)

    registrations = list(gift.registrations.select_related("registrant").all())
    if request.headers.get("HX-Request"):
        return render(request, "gifts/partials/registration_section.html", {
            "gift": gift,
            "registrations": registrations,
            "i_am_registered": True,
        })

    return redirect("gifts:user_list", user_pk=gift.owner.pk)  # register_gift end


@login_required
def groups(request):
    """Manage group members, nicknames, birthday, and invitations."""
    workspace = getattr(request, "workspace", None)
    if not workspace:
        messages.info(request, _("Create or join a group first."))
        return redirect("dashboard:index")

    membership = get_object_or_404(Membership, user=request.user, workspace=workspace)
    ws_settings = WorkspaceSettings.for_workspace(workspace)
    members_can_invite = ws_settings.members_can_invite
    can_invite = membership.is_admin or members_can_invite

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "set_profile":
            nickname = request.POST.get("nickname", "").strip()
            birthday_str = request.POST.get("birthday", "").strip()

            if nickname:
                WorkspaceNickname.objects.update_or_create(
                    user=request.user,
                    workspace=workspace,
                    defaults={"nickname": nickname},
                )
            else:
                WorkspaceNickname.objects.filter(
                    user=request.user, workspace=workspace
                ).delete()

            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            if birthday_str:
                try:
                    profile.birthday = date.fromisoformat(birthday_str)
                    profile.save()
                except ValueError:
                    messages.error(request, _("Invalid date format."))
                    return redirect("gifts:groups")
            else:
                profile.birthday = None
                profile.save()

            messages.success(request, _("Profile updated!"))
            return redirect("gifts:groups")

        if action == "invite" and can_invite:
            email = request.POST.get("email", "").strip().lower()
            nickname = request.POST.get("invite_nickname", "").strip()
            if not email:
                messages.error(request, _("Please enter an email address."))
                return redirect("gifts:groups")
            if Membership.objects.filter(workspace=workspace, user__email=email).exists():
                messages.warning(request, _("%(email)s is already a member of this group.") % {"email": email})
                return redirect("gifts:groups")

            invitation, created = Invitation.objects.get_or_create(
                workspace=workspace,
                email=email,
                defaults={"invited_by": request.user},
            )
            if not created:
                invitation.invited_by = request.user
                invitation.accepted_at = None
                invitation.expires_at = timezone.now() + timedelta(days=7)
                invitation.save()

            # Store the pre-set nickname so the signal applies it on join
            if nickname:
                PendingNickname.objects.update_or_create(
                    workspace=workspace,
                    email=email,
                    defaults={"nickname": nickname},
                )
            else:
                PendingNickname.objects.filter(workspace=workspace, email=email).delete()

            invite_url = request.build_absolute_uri(
                f"/workspaces/accept-invite/{invitation.token}/"
            )
            app_name = getattr(django_settings, "APP_NAME", "Giftarium")
            send_mail(
                subject=_("You've been invited to %(workspace)s on %(app)s") % {"workspace": workspace.name, "app": app_name},
                message=_("%(user)s has invited you to join \"%(workspace)s\" on %(app)s.\n\nAccept here: %(url)s") % {
                    "user": request.user.display_name,
                    "workspace": workspace.name,
                    "app": app_name,
                    "url": invite_url,
                },
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
            messages.success(request, _("Invitation sent to %(email)s!") % {"email": email})
            return redirect("gifts:groups")

        if action == "cancel_invite" and can_invite:
            inv_id = request.POST.get("invitation_id")
            inv = Invitation.objects.filter(pk=inv_id, workspace=workspace).first()
            if inv:
                PendingNickname.objects.filter(
                    workspace=workspace, email=inv.email
                ).delete()
                inv.delete()
            messages.success(request, _("Invitation cancelled."))
            return redirect("gifts:groups")

        return redirect("gifts:groups")

    # Build nickname map for this workspace
    nickname_map = {
        n.user_id: n.nickname
        for n in WorkspaceNickname.objects.filter(workspace=workspace)
    }

    # Build birthday map
    user_ids = [m.user_id for m in Membership.objects.filter(workspace=workspace)]
    birthday_map = {
        p.user_id: p.birthday
        for p in UserProfile.objects.filter(user_id__in=user_ids, birthday__isnull=False)
    }

    memberships = list(
        Membership.objects.filter(workspace=workspace)
        .select_related("user")
        .order_by("joined_at")
    )
    for m in memberships:
        m.user.workspace_nickname = nickname_map.get(m.user_id, "")
        m.user.birthday = birthday_map.get(m.user_id)

    my_nickname = nickname_map.get(request.user.pk, "")
    my_profile = UserProfile.objects.filter(user=request.user).first()
    my_birthday = my_profile.birthday if my_profile else None

    pending_invitations = list(
        Invitation.objects.filter(workspace=workspace, accepted_at__isnull=True)
        .order_by("-created_at")
    )
    pending_nickname_map = {
        p.email: p.nickname
        for p in PendingNickname.objects.filter(workspace=workspace)
    }
    for inv in pending_invitations:
        inv.preset_nickname = pending_nickname_map.get(inv.email, "")

    return render(request, "gifts/groups.html", {
        "memberships": memberships,
        "my_nickname": my_nickname,
        "my_birthday": my_birthday,
        "pending_invitations": pending_invitations,
        "can_invite": can_invite,
        "membership": membership,
        "ws_settings": ws_settings,
    })


@login_required
def unregister_gift(request, pk):
    """Unregister from a gift."""
    if request.method != "POST":
        return redirect("gifts:index")

    # Only allow unregistering from gifts the user actually registered for
    gift = get_object_or_404(Gift, pk=pk)
    GiftRegistration.objects.filter(gift=gift, registrant=request.user).delete()

    registrations = list(gift.registrations.select_related("registrant").all())
    if request.headers.get("HX-Request"):
        return render(request, "gifts/partials/registration_section.html", {
            "gift": gift,
            "registrations": registrations,
            "i_am_registered": False,
        })

    return redirect("gifts:user_list", user_pk=gift.owner.pk)


@login_required
def join_via_link(request, token):
    """Join a workspace via a reusable invite link."""
    invite_link = get_object_or_404(WorkspaceInviteLink, token=token)
    workspace = invite_link.workspace

    if Membership.objects.filter(user=request.user, workspace=workspace).exists():
        messages.info(request, _("You're already a member of %(name)s.") % {"name": workspace.name})
        return redirect("gifts:index")

    Membership.objects.create(user=request.user, workspace=workspace, role="member")
    request.user.current_workspace = workspace
    request.user.save(update_fields=["current_workspace"])
    messages.success(request, _("Welcome to %(name)s! You can now see everyone's wishlists.") % {"name": workspace.name})
    return redirect("gifts:index")
