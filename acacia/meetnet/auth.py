'''
Created on Nov 17, 2019

@author: theo
'''
from acacia.meetnet.models import Network
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin

def should_login(user):
    network = Network.objects.first()
    return (network and not network.login_required) or user.is_authenticated

def auth_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the user is logged in (if needed for this network), redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: should_login(u),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def staff_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the user is staff member, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_staff,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

class AuthRequiredMixin(LoginRequiredMixin):
    """
    CBV mixin which verifies that the current user is authenticated (if required by network).
    """
    def dispatch(self, request, *args, **kwargs):
        network = Network.objects.first() # assume there is only one network!
        if network and network.login_required:
            return LoginRequiredMixin.dispatch(self, request, *args, **kwargs)
        else:
            return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)

class StaffRequiredMixin(LoginRequiredMixin):
    """
    CBV mixin which verifies that the current user is staff member
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return self.handle_no_permission()
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)

