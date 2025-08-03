from django import forms
from home.models import Temporada, Liga, Equipo, Equipacion


class TemporadaForm(forms.ModelForm):
    class Meta:
        model = Temporada
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 2024-25',
                'maxlength': 20
            })
        }
        labels = {
            'nombre': 'Nombre de la temporada'
        }


class LigaForm(forms.ModelForm):
    class Meta:
        model = Liga
        fields = ['nombre', 'logo', 'temporada']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: LaLiga, Premier League, Serie A...'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'temporada': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'nombre': 'Nombre de la liga',
            'logo': 'Logo de la liga',
            'temporada': 'Temporada'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['temporada'].queryset = Temporada.objects.order_by('-creado_en')
        self.fields['temporada'].empty_label = "Selecciona una temporada"


class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = ['nombre', 'logo', 'liga']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Real Madrid, Barcelona, Manchester United...'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'liga': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'nombre': 'Nombre del equipo',
            'logo': 'Logo del equipo',
            'liga': 'Liga'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['liga'].queryset = Liga.objects.select_related('temporada').order_by('temporada__nombre', 'nombre')
        self.fields['liga'].empty_label = "Selecciona una liga"


class EquipacionForm(forms.ModelForm):
    class Meta:
        model = Equipacion
        fields = ['equipo', 'temporada', 'imagen']
        widgets = {
            'equipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'temporada': forms.Select(attrs={
                'class': 'form-select'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        labels = {
            'equipo': 'Equipo',
            'temporada': 'Temporada',
            'imagen': 'Imagen de la equipación'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['equipo'].queryset = Equipo.objects.select_related('liga', 'liga__temporada').order_by('liga__temporada__nombre', 'liga__nombre', 'nombre')
        self.fields['temporada'].queryset = Temporada.objects.order_by('-creado_en')
        self.fields['equipo'].empty_label = "Selecciona un equipo"
        self.fields['temporada'].empty_label = "Selecciona una temporada"