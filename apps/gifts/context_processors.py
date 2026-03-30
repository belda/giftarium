from .models import WorkspaceSettings


def ws_settings(request):
    workspace = getattr(request, "workspace", None)
    if not workspace:
        return {}
    return {"ws_settings": WorkspaceSettings.for_workspace(workspace)}
