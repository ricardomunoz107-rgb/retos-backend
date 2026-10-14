from rest_framework import serializers

from .models import Categoria, Envio, Reto


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'


class RetoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.ReadOnlyField(source='categoria.nombre')
    respuesta_correcta = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Reto
        fields = '__all__'


class EnvioSerializer(serializers.ModelSerializer):
    reto_titulo = serializers.ReadOnlyField(source='reto.titulo')

    class Meta:
        model = Envio
        fields = '__all__'
