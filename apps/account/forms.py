from django.contrib.auth.forms import UserCreationForm
from apps.account.utils import generate_user


class QAUserCreationForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fullname'].widget.attrs['class'] = 'signup-input'
        self.fields['fullname'].widget.attrs['placeholder'] = 'Fullname'

        self.fields['email'].widget.attrs['class'] = 'signup-input'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'

        self.fields['password1'].widget.attrs['class'] = 'signup-input'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'

        self.fields['password2'].widget.attrs['class'] = 'signup-input'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = generate_user()
        user.save()
        return user
