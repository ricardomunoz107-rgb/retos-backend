from django.shortcuts import render
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

def home(request):
    retos_list = [
        {"id": 1, "titulo": "Suma de Arreglos", "dificultad": "Fácil", "puntos": 10},
        {"id": 2, "titulo": "Palíndromo Checker", "dificultad": "Media", "puntos": 20},
        {"id": 3, "titulo": "Arbol Binario", "dificultad": "Difícil", "puntos": 50},
    ]
    carpetas = sorted(
        carpeta.name
        for carpeta in BASE_DIR.iterdir()
        if carpeta.is_dir() and not carpeta.name.startswith("__")
    )
    total_retos = len(retos_list)
    suma_puntos = sum(reto["puntos"] for reto in retos_list)

    contexto = {
        "nombre_plataforma": "Plataforma de Retos de Programación",
        "total_retos": total_retos,
        "suma_puntos": suma_puntos,
        "promedio_puntos": suma_puntos / total_retos if total_retos else 0,
        "activa": True,
        "retos": retos_list,
        "carpetas": carpetas,
    }
    return render(request, "retos/index.html", contexto)

def pagina_error_404(request, exception):
    return render(request, "404.html", status=404)