# coding: utf-8

from django import forms
from django.forms.models import model_to_dict

from apps.users.tasks import send_template_mail
from apps.users.models import User, UsersProfile
from apps.users.constants import APP_SUBJECT_TO_RESTORE_EMAIL


class UsersProfileForm(forms.ModelForm):
    email = forms.EmailField(required=False)
    username = forms.CharField(required=True, max_length=30)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('instance')
        kwargs['instance'] = self.user.profile

        super(UsersProfileForm, self).__init__(*args, **kwargs)
        self.fields['email'].initial = self.user.email

    def save(self, commit=True, send_email=False):
        email = self.cleaned_data['email']
        flag = True if self.user.username != email or self.user.email != email else False

        if flag:
            self.confirm_email = False
            self.activation_key = self.instance.generate_key()

        instance = super(UsersProfileForm, self).save(commit)

        self.user.first_name = self.cleaned_data['username']
        if flag:
            self.user.email = email
            self.user.username = email

        self.user.save()

        if send_email:
            try:
                # Формируем параметры email
                param_email = {
                    'to': [email],
                    'context': {
                        'user': model_to_dict(self.user, fields=[field.name for field in self.user._meta.fields]),
                        'profile': model_to_dict(instance, fields=[field.name for field in instance._meta.fields])
                    },
                    'subject': APP_SUBJECT_TO_RESTORE_EMAIL,
                    'tpl_name': 'email_confirm.html',
                }

                # Отправляем email
                send_template_mail.apply_async(kwargs=param_email)
            except Exception, e:
                pass


    class Meta:
        model = UsersProfile
        exclude = ('userpic_id', 'userpic_type', 'last_visited', 'user')


class CustomRegisterForm(forms.ModelForm):
    password2 = forms.CharField(widget=forms.PasswordInput, required=True)
    password1 = forms.CharField(widget=forms.PasswordInput, required=True)

    error_messages = {
        'passwords_not_equal': u'Пароли не совпадают',
        'email': u'Email-обязательное поле!',
    }

    def __init__(self, **kwargs):
        super(CustomRegisterForm, self).__init__(**kwargs)
        self.fields['username'].required = False
        self.fields['email'].required = True

    def clean(self):
        if 'email' in self.cleaned_data:
            self.cleaned_data['username'] = self.cleaned_data.get('email')
        else:
            raise forms.ValidationError(self.error_messages['email'],
                                        code='email')
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(self.error_messages['passwords_not_equal'],
                                            code='password_not_equal')
            else:
                return super(CustomRegisterForm, self).clean()
        else:
            raise forms.ValidationError('Password is required field')

    def save(self, commit=True, send_email=False):
        instance = super(CustomRegisterForm, self).save(commit)
        instance.first_name = self.cleaned_data['email'].split('@')[0]
        instance.set_password(self.cleaned_data['password1'])
        instance.save()

        if send_email:
            try:
                pass
            except Exception, e:
                pass

        return instance

    class Meta:
        model = User
        fields = ('email', 'username')


class UserUpdateForm(forms.Form):
    name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=False)
