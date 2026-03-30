from django.urls import path
from django.views.generic import RedirectView
from django.shortcuts import render, redirect
from webapptemplate.urls import urlpatterns as wt_urlpatterns


def home(request):
    if request.user.is_authenticated:
        return redirect("gifts:my_list")
    return render(request, "landing.html")


urlpatterns = [
    path("", home, name="home"),
    path("dashboard/", RedirectView.as_view(pattern_name="gifts:my_list", permanent=False)),
] + wt_urlpatterns
