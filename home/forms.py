from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile


class RegistroForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu-email@ejemplo.com'
        })
    )

    instagram_account = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu_cuenta_instagram'
        }),
        help_text="Cuenta de Instagram sin el símbolo @"
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
    )

    class Meta:
        model = User
        fields = ('email', 'instagram_account', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe un usuario con este email.")
        return email

    def clean_instagram_account(self):
        instagram = self.cleaned_data.get('instagram_account')
        # Remover @ si el usuario lo incluye
        instagram = instagram.lstrip('@')

        if UserProfile.objects.filter(instagram_account=instagram).exists():
            raise forms.ValidationError("Ya existe un usuario con esta cuenta de Instagram.")
        return instagram

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']  # Usar email como username

        if commit:
            user.save()
            # Crear el perfil de usuario
            UserProfile.objects.create(
                user=user,
                instagram_account=self.cleaned_data['instagram_account']
            )
        return user