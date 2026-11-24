from django import forms

from .models import Categoria, Envio, Reto, RetoResuelto


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre", "descripcion"]
        widgets = {
            "nombre": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ej. Algoritmos"}
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Describe esta categoría",
                    "rows": 4,
                }
            ),
        }


class RetoForm(forms.ModelForm):
    class Meta:
        model = Reto
        fields = [
            "titulo",
            "descripcion",
            "dificultad",
            "puntos",
            "activo",
            "categoria",
            "respuesta_correcta",
        ]
        widgets = {
            "titulo": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre del reto"}
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Explica el problema que debe resolver el participante",
                    "rows": 5,
                }
            ),
            "dificultad": forms.Select(attrs={"class": "form-control"}),
            "puntos": forms.NumberInput(
                attrs={"class": "form-control", "min": 0, "placeholder": "10"}
            ),
            "activo": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
            "categoria": forms.Select(attrs={"class": "form-control"}),
            "respuesta_correcta": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Salida esperada del programa",
                }
            ),
        }


class RetoResueltoForm(forms.ModelForm):
    class Meta:
        model = RetoResuelto
        fields = ["usuario", "reto", "puntos_obtenidos"]
        widgets = {
            "usuario": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre del participante"}
            ),
            "reto": forms.Select(attrs={"class": "form-control"}),
            "puntos_obtenidos": forms.NumberInput(
                attrs={"class": "form-control", "min": 0, "placeholder": "10"}
            ),
        }


class EnvioForm(forms.ModelForm):
    class Meta:
        model = Envio
        fields = ["reto", "usuario", "codigo_fuente", "lenguaje", "estado"]
        widgets = {
            "reto": forms.Select(attrs={"class": "form-control"}),
            "usuario": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre del participante"}
            ),
            "codigo_fuente": forms.Textarea(
                attrs={
                    "class": "form-control code-input",
                    "placeholder": "Escribe el código enviado",
                    "rows": 8,
                }
            ),
            "lenguaje": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "python"}
            ),
            "estado": forms.Select(attrs={"class": "form-control"}),
        }
