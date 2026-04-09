from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .forms import UserRegistrationForm, EmailAuthenticationForm, ResendVerificationEmailForm
from .models import User
from .services import send_account_activation_email
from .tokens import account_activation_token


def signup_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.is_active = False
            user.email_verified = False
            user.save()

            # request.session["pending_verification_user_id"] = user.pk
            # request.session.set_expiry(60 * 60)

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            send_account_activation_email(request, user, uid, token)

            return render(request, "accounts/signup_done.html")

    else:
        form = UserRegistrationForm()

    return render(request, "accounts/signup.html", {"form": form})


def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and account_activation_token.check_token(user, token):
        user.email_verified = True
        user.is_active = True
        user.save()

        # request.session.pop("pending_verification_user_id", None)
        return render(request, "accounts/verify_success.html")

    return render(request, "accounts/verify_fail.html")


def resend_verification_email(request):
    if request.method == "POST":
        form = ResendVerificationEmailForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = User.objects.get(email=email)
                if not user:
                    messages.error(request, "사용자를 찾을 수 없습니다.")
                    return redirect("accounts:signup")

                if user.email_verified:
                    messages.info(request, "이미 인증이 완료된 계정입니다.")
                    return redirect("accounts:login")

                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = account_activation_token.make_token(user)
                send_account_activation_email(request, user, uid, token)

                messages.success(request, "인증 메일을 다시 보냈습니다.")
                return render(request, "accounts/signup_done.html")

            except User.DoesNotExist:
                messages.error(request, "사용자를 찾을 수 없습니다.")
                return redirect("accounts:signup")

    else:
        form = ResendVerificationEmailForm()

    return render(request, "accounts/resend_verification.html", {"form": form})


def verification_required_view(request):
    if not request.user.is_authenticated:
        return redirect("accounts:login")

    if request.user.email_verified:
        return redirect("files:index")

    return render(request, "accounts/verification_required.html")


class SigninView(LoginView):
    template_name = "accounts/signin.html"
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True


class SignoutView(LogoutView):
    template_name = "accounts/signout.html"