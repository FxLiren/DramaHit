from django import forms
from django.contrib.auth.forms import SetPasswordForm


class CustomSetPasswordForm(SetPasswordForm):

    def clean(self):
        cleaned_data = super().clean()

        new_password1 = cleaned_data.get('new_password1')

        if new_password1 and self.user.check_password(new_password1):
            raise forms.ValidationError(
                '新密碼不能與舊密碼相同。'
            )

        return cleaned_data