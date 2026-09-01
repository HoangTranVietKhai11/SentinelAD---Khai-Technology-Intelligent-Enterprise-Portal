from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(
        label='Tên đăng nhập',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'khai\\username hoặc username@khai.local',
            'autofocus': True,
            'id': 'id_username',
        })
    )
    password = forms.CharField(
        label='Mật khẩu',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '••••••••••••',
            'id': 'id_password',
        })
    )
