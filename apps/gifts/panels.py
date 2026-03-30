from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _


@login_required
def workspace_settings_panel_view(request):
    from webapptemplate.apps.workspaces.models import Membership
    from .models import WorkspaceSettings
    from .forms import WorkspaceSettingsForm

    workspace = request.workspace
    if not workspace:
        return redirect("workspace_create")

    membership = Membership.objects.filter(user=request.user, workspace=workspace).first()
    if not membership or not membership.is_admin:
        raise PermissionDenied

    ws_settings = WorkspaceSettings.for_workspace(workspace)
    saved = False

    if request.method == "POST":
        form = WorkspaceSettingsForm(request.POST, instance=ws_settings)
        if form.is_valid():
            form.save()
            saved = True
            form = WorkspaceSettingsForm(instance=ws_settings)
            if not request.headers.get("HX-Request"):
                messages.success(request, _("Settings saved."))
                return redirect("workspace_settings")
    else:
        form = WorkspaceSettingsForm(instance=ws_settings)

    return render(request, "gifts/panels/workspace_settings.html", {
        "form": form,
        "saved": saved,
    })


@login_required
def user_profile_panel_view(request):
    from .models import UserProfile
    from .forms import UserProfileForm

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    saved = False

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            saved = True
            form = UserProfileForm(instance=profile)
            if not request.headers.get("HX-Request"):
                messages.success(request, _("Profile saved."))
                return redirect("profile_settings")
    else:
        form = UserProfileForm(instance=profile)

    return render(request, "gifts/panels/user_profile.html", {
        "form": form,
        "saved": saved,
    })
