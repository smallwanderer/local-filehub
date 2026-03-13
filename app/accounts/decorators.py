from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def email_verification_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")

        if request.user.email_verified:
            return function(request, *args, **kwargs)

        messages.warning(request, "이메일 인증이 필요한 서비스입니다.")
        return redirect("accounts:verification_required")

    return wrap