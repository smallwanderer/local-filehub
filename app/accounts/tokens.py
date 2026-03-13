from django.contrib.auth.tokens import PasswordResetTokenGenerator 

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{user.email_verified}{timestamp}"

account_activation_token = AccountActivationTokenGenerator()
