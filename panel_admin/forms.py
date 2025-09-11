from django import forms
from home.models import Seccion, Subseccion, Subsubseccion, Prenda


class SeccionForm(forms.ModelForm):
    class Meta:
        model = Seccion
        fields = ['nombre', 'descripcion', 'logo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Ropa Callejera, Fútbol, Zapatillas...'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción opcional de la sección...',
                'rows': 3
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        labels = {
            'nombre': 'Nombre de la sección',
            'descripcion': 'Descripción',
            'logo': 'Logo de la sección'
        }


class SubseccionForm(forms.ModelForm):
    class Meta:
        model = Subseccion
        fields = ['nombre', 'logo', 'seccion', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: LaLiga, Camisetas, Running...'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'seccion': forms.Select(attrs={
                'class': 'form-select'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción opcional...',
                'rows': 3
            })
        }
        labels = {
            'nombre': 'Nombre de la subsección',
            'logo': 'Logo de la subsección',
            'seccion': 'Sección',
            'descripcion': 'Descripción'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['seccion'].queryset = Seccion.objects.all().order_by('nombre')
        self.fields['seccion'].empty_label = "Selecciona una sección"


class SubsubseccionForm(forms.ModelForm):
    class Meta:
        model = Subsubseccion
        fields = ['nombre', 'logo', 'subseccion', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Real Madrid, Oversized, Adidas...'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'subseccion': forms.Select(attrs={
                'class': 'form-select'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción opcional...',
                'rows': 3
            })
        }
        labels = {
            'nombre': 'Nombre de la subsubsección',
            'logo': 'Logo de la subsubsección',
            'subseccion': 'Subsección',
            'descripcion': 'Descripción'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subseccion'].queryset = Subseccion.objects.select_related('seccion').all().order_by('seccion__nombre', 'nombre')
        self.fields['subseccion'].empty_label = "Selecciona una subsección"


class PrendaForm(forms.ModelForm):
    class Meta:
        model = Prenda
        fields = ['nombre', 'subsubseccion', 'imagen', 'precio']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Camiseta Local 2024, Ultraboost 22...'
            }),
            'subsubseccion': forms.Select(attrs={
                'class': 'form-select'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '0.01',
                'placeholder': '0.00'
            })
        }
        labels = {
            'nombre': 'Nombre de la prenda',
            'subsubseccion': 'Subsubsección',
            'imagen': 'Imagen de la prenda',
            'precio': 'Precio (€)'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subsubseccion'].queryset = Subsubseccion.objects.select_related('subseccion', 'subseccion__seccion').all().order_by('subseccion__seccion__nombre', 'subseccion__nombre', 'nombre')
        self.fields['subsubseccion'].empty_label = "Selecciona una subsubsección"


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class PrendaMultipleUploadForm(forms.Form):
    imagenes = MultipleFileField(
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'multiple': True
        }),
        label='Seleccionar imágenes',
        help_text='Puedes seleccionar múltiples imágenes a la vez. Formatos permitidos: JPG, PNG, GIF.'
    )
    precio = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 0,
            'step': '0.01',
            'placeholder': '0.00'
        }),
        label='Precio para todas las prendas (€)',
        help_text='Este precio se aplicará a todas las prendas que subas.'
    )
    subsubseccion = forms.ModelChoiceField(
        queryset=Subsubseccion.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Subsubsección',
        empty_label="Selecciona una subsubsección"
    )

    def __init__(self, *args, **kwargs):
        subsubseccion_id = kwargs.pop('subsubseccion_id', None)
        super().__init__(*args, **kwargs)
        
        if subsubseccion_id:
            # Si tenemos una subsubseccion específica, la preseleccionamos con campo oculto
            self.fields['subsubseccion'].queryset = Subsubseccion.objects.filter(id=subsubseccion_id)
            self.fields['subsubseccion'].initial = subsubseccion_id
            self.fields['subsubseccion'].widget = forms.HiddenInput()
        else:
            self.fields['subsubseccion'].queryset = Subsubseccion.objects.select_related(
                'subseccion', 'subseccion__seccion'
            ).all().order_by('subseccion__seccion__nombre', 'subseccion__nombre', 'nombre')