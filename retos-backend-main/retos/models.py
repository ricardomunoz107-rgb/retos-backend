from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Reto(models.Model):
    DIFICULTAD_CHOICES = [
        ('FACIL', 'Fácil'),
        ('MEDIA', 'Media'),
        ('DIFICIL', 'Difícil'),
    ]

    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    dificultad = models.CharField(max_length=10, choices=DIFICULTAD_CHOICES, default='FACIL')
    puntos = models.PositiveIntegerField(default=10)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='retos')
    respuesta_correcta = models.CharField(max_length=255, blank=True, default='')

    def __str__(self):
        return f"{self.titulo} ({self.dificultad})"

    def respuesta_es_correcta(self, respuesta):
        esperada = " ".join(self.respuesta_correcta.casefold().split())
        recibida = " ".join(respuesta.casefold().split())
        return bool(esperada) and recibida == esperada


class RetoResuelto(models.Model):
    usuario = models.CharField(max_length=80)
    reto = models.ForeignKey(Reto, on_delete=models.CASCADE, related_name='resoluciones')
    puntos_obtenidos = models.PositiveIntegerField()
    fecha_resolucion = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['usuario', 'reto'], name='un_reto_resuelto_por_usuario'),
        ]

    def __str__(self):
        return f"{self.usuario} - {self.reto.titulo} ({self.puntos_obtenidos} pts)"


class Envio(models.Model):
    ESTADO_CHOICES = [
        ('ACEPTADO', 'Aceptado'),
        ('RECHAZADO', 'Rechazado'),
        ('PENDIENTE', 'Pendiente'),
    ]

    reto = models.ForeignKey(Reto, on_delete=models.CASCADE, related_name='envios')
    usuario = models.CharField(max_length=80)
    codigo_fuente = models.TextField()
    lenguaje = models.CharField(max_length=30, default='python')
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='PENDIENTE')
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Envío #{self.id} de {self.usuario} - {self.reto.titulo}"
