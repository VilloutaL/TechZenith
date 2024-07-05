# forms.py

from django import forms
from .models import Anuncio

class AnuncioForm(forms.ModelForm):
    class Meta:
        model = Anuncio
        fields = ['titulo', 'contenido', 'asignatura']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del anuncio'}),
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Contenido del anuncio'}),
            'asignatura': forms.Select(attrs={'class': 'form-control'}),
        }
