from django import forms
from django.core.exceptions import ValidationError
from django.forms import widgets

from blog.models import *


class UserForm(forms.Form):
    user = forms.CharField(max_length=32, label='用户名', widget=widgets.TextInput(attrs={'class': 'form-control'})
                           , error_messages={'required': '该字段不能为空'}
                           )
    pwd = forms.CharField(max_length=32, label='密码', widget=widgets.PasswordInput(attrs={'class': 'form-control'})
                          , error_messages={'required': '该字段不能为空'}
                          )
    re_pwd = forms.CharField(max_length=32, label='确认密码', widget=widgets.PasswordInput(attrs={'class': 'form-control'})
                             , error_messages={'required': '该字段不能为空'}
                             )
    email = forms.EmailField(max_length=32, label='邮箱', widget=widgets.EmailInput(attrs={'class': 'form-control'})
                             , error_messages={'required': '该字段不能为空'}
                             )

    def clean_user(self):
        user = self.cleaned_data.get('user')
        user_sql = UserInfo.objects.filter(username=user).first()
        if user_sql:
            raise ValidationError('该用户也存在')
        else:
            return user

    def clean(self):
        pwd = self.cleaned_data.get('pwd')
        re_pwd = self.cleaned_data.get('re_pwd')
        # 如果一个值为空 那么就直接返回不做密码校验
        if pwd and re_pwd:
            if pwd == re_pwd:
                return self.cleaned_data
            else:
                raise ValidationError('两次密码不一致')
        else:
            # 全局钩子必须返回这个值
            return self.cleaned_data
