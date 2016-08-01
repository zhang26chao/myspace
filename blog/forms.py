# !-*-coding=utf8-*-
'''
Created on 2015-1-20

@author: Administrator
'''
from django import forms
from DjangoCaptcha import Captcha

class ContactForm(forms.Form):
    def __init__(self,data=None,request=None):
        self.django_request = request
        forms.BaseForm.__init__(self,data)
    
    nickname = forms.CharField(widget=forms.TextInput(attrs={'id':'nickname','placeholder': '昵称'}),required = True)
    email = forms.EmailField(widget=forms.TextInput(attrs={'id':'email','placeholder': '电子邮箱'}),required = True)
    content = forms.CharField(widget=forms.Textarea(attrs={'id':'formContent','placeholder': '内容'}),required = True)
    code = forms.CharField(widget=forms.TextInput(attrs={'id':'code','class':'code','placeholder': '验证码'}),required = True)
    
    def clean_code(self):
        code = self.cleaned_data['code']
        ca = Captcha(self.django_request)
        if not ca.check(code):
            raise forms.ValidationError("验证码错误")
        return code