import re
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from accounts.models import UserProfile

User = get_user_model()


class SignupForm(UserCreationForm):
    email = forms.EmailField()

    def clean_password2(self):
        password2 = super(SignupForm, self).clean_password2()
        if password2:
            if len(password2) < 6:
                raise forms.ValidationError('6자 이상 입력!')
            elif re.match(r'^\d+$', password2):
                raise forms.ValidationError('숫자로만 입력하지 마세요!!!')
        return password2

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        if email:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError('이미 등록된 이메일입니다.')
        return email

    def save(self, commit=True):
        user = super(SignupForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


#   class Meta:
#       model = User
#       fields = ('username', 'email')


class QuizLoginForm(AuthenticationForm):
    answer = forms.CharField(help_text='3+3=?')

    def clean_answer(self):
        answer = self.cleaned_data.get('answer', '').strip()
        if answer:
            if answer != '6':
                raise forms.ValidationError('땡~!!!')
        return answer


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('biography',)
