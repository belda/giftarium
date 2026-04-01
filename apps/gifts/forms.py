from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Gift, UserProfile, WorkspaceSettings


class GiftForm(forms.ModelForm):
    class Meta:
        model = Gift
        fields = ["name", "description", "url", "price"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "input",
                "placeholder": _("What do you wish for?"),
            }),
            "description": forms.Textarea(attrs={
                "class": "input",
                "rows": 2,
                "placeholder": _("Optional details — color, size, brand…"),
            }),
            "url": forms.URLInput(attrs={
                "class": "input",
                "placeholder": "https://…",
            }),
            "price": forms.NumberInput(attrs={
                "class": "input",
                "placeholder": "0.00",
                "step": "0.01",
                "min": "0",
            }),
        }
        labels = {
            "name": _("Gift name"),
            "description": _("Details"),
            "url": _("Link"),
            "price": _("Approximate price"),
        }


class WorkspaceSettingsForm(forms.ModelForm):
    class Meta:
        model = WorkspaceSettings
        fields = ["members_can_invite", "currency"]
        widgets = {
            "members_can_invite": forms.CheckboxInput(attrs={"class": "h-4 w-4 rounded border-gray-300 text-indigo-600"}),
            "currency": forms.TextInput(attrs={"class": "input", "placeholder": "CZK"}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["birthday"]
        widgets = {
            "birthday": forms.DateInput(attrs={"type": "date", "class": "input"}),
        }
        labels = {
            "birthday": _("Birthday"),
        }
