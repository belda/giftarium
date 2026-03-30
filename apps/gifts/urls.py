from django.urls import path
from . import views

app_name = "gifts"

urlpatterns = [
    path("", views.index, name="index"),
    path("mine/", views.my_list, name="my_list"),
    path("mine/<int:pk>/edit/", views.edit_gift, name="edit_gift"),
    path("mine/<int:pk>/delete/", views.delete_gift, name="delete_gift"),
    path("mine/<int:pk>/received/", views.mark_received, name="mark_received"),
    path("mine/<int:gift_pk>/exclude/<int:workspace_pk>/", views.toggle_exclusion, name="toggle_exclusion"),
    path("user/<int:user_pk>/", views.user_list, name="user_list"),
    path("user/<int:user_pk>/surprise/", views.add_surprise, name="add_surprise"),
    path("gift/<int:pk>/register/", views.register_gift, name="register_gift"),
    path("gift/<int:pk>/unregister/", views.unregister_gift, name="unregister_gift"),
    path("groups/", views.groups, name="groups"),
    path("join/<uuid:token>/", views.join_via_link, name="join_via_link"),
]
