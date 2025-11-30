from django import forms
from allauth.account.forms import SignupForm
from django.utils.translation import gettext_lazy as _

class CustomSignupForm(SignupForm):
    confirm_age = forms.BooleanField(label=_("I confirm I am 18+ years old"), required=True)

    def save(self, request):
        user = super().save(request)
        return user
