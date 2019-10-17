#coding=utf-8

# std imports
import uuid, re, os, pathlib
# django imports
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.dispatch import receiver
from django.urls import reverse
#local imports
from .storage import OverwriteStorage

# Funcion que guarda una imagen segun la id del registro
def id_img(instance, filename):
    save_fname = instance.modelName/pathlib.Path(str(instance.pk))
    save_fname = save_fname.with_suffix(pathlib.Path(filename).suffix)
    return str(save_fname)

# User, Base for Organizador and Voluntario
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_voluntario = models.BooleanField(default=False)
    is_organizador = models.BooleanField(default=False)

# MODELS
class Voluntario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    nombre = models.CharField(max_length=256, verbose_name="Nombre Completo")
    telefono = models.CharField(max_length=10, verbose_name="Teléfono Móvil")
    email = models.EmailField(unique=True, verbose_name="E-mail")
    num_cuenta_unam = models.CharField(unique=True, max_length=9, verbose_name="Número de Cuenta UNAM")
    total_horas = models.PositiveIntegerField(default=0, verbose_name="Horas de voluntariado")
    foto = models.ImageField(upload_to=id_img, default=os.path.join('Voluntario', 'default.jpg'),
                             verbose_name="Foto de Perfil", storage=OverwriteStorage())
    modelName = 'Voluntario'

    class Meta:
        db_table = 'voluntario'
        ordering = ["-total_horas", "nombre"]
    
    def __str__(self):
        return self.nombre
    
    def get_absolute_url(self):
        return reverse('volun_details', args=[str(self.user.id)])

class Institucion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    telefono = models.CharField(max_length=10, verbose_name="Teléfono")
    nombre = models.CharField(max_length=256, verbose_name="Nombre de la Institución")
    ciudad = models.CharField(max_length=256, verbose_name="Ciudad")
    tipo_organizacion = models.IntegerField(choices=[(0, 'UNAM'), (1, 'Gobierno'), (2, 'ONG')])
    url_pagina = models.URLField(verbose_name="Sitio Web de la Institución", null=True)
    direccion = models.TextField(verbose_name="Dirección")

    class Meta:
        db_table = 'institucion'
        ordering = ["nombre"]


class Organizador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    nombre = models.CharField(max_length=256, verbose_name="Nombre Completo")
    tel_movil = models.CharField(max_length=10, verbose_name="Teléfono Móvil")
    tel_oficina = models.CharField(max_length=10, blank=True, null=True, verbose_name="Teléfono Oficina")
    email = models.EmailField(unique=True, verbose_name="E-mail")
    institucion = models.ForeignKey(Institucion, models.CASCADE)
    foto = models.ImageField(upload_to=id_img, default=os.path.join('Organizador', 'default.jpg'),
                             verbose_name="Foto de Perfil", storage=OverwriteStorage())
    
    modelName = 'Organizador'

    class Meta:
        db_table = 'organizador'
        ordering = ["nombre"]
    
    def get_absolute_url(self):
        return reverse('org_details', args=[str(self.user.id)])


class Evento(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=256, verbose_name="Nombre del Evento")
    fecha = models.DateField(verbose_name="Fecha del Evento")
    lugar = models.CharField(max_length=256, verbose_name="Lugar del Evento")
    activo = models.NullBooleanField(default=True)
    organizador = models.ForeignKey(Organizador, models.DO_NOTHING)
    descripcion = models.TextField(verbose_name="Descripción del Evento")
    num_equipos = models.PositiveIntegerField(default=1, verbose_name="Número de equipos en el evento")
    url_pagina = models.URLField(max_length=300, blank=True, null=True, verbose_name="Sitio Web del Evento")
    foto = models.ImageField(upload_to=id_img, default=os.path.join('Evento', 'default.jpg'),
                             verbose_name="Foto del evento", storage=OverwriteStorage())
    
    modelName = 'Evento'

    class Meta:
        db_table = 'evento'
        ordering = ['-activo', 'fecha', 'nombre']
    
    def get_absolute_url(self):
        return reverse('event_details', args=[str(self.id)])


@receiver(models.signals.post_delete, sender=Evento)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `Evento' object is deleted.
    """
    #check if exists
    default_foto = Evento._meta.get_field('foto').get_default()
    if instance.foto and os.path.isfile(instance.foto.path):
        if instance.foto.path != os.path.join(settings.MEDIA_ROOT, default_foto):
            os.remove(instance.foto.path)



class Participacion(models.Model):
    voluntario = models.ForeignKey(Voluntario, models.CASCADE)
    evento = models.ForeignKey(Evento, models.CASCADE)
    horas = models.PositiveIntegerField(default=0, verbose_name="Horas Participadas")
    comentario_voluntario = models.TextField(blank=True, null=True)
    comentario_organizador = models.TextField(blank=True, null=True)
    capitan = models.BooleanField(default=False, verbose_name="Verdadero si es Capitan")
    equipo = models.PositiveIntegerField(default=1, verbose_name="Equipo al que pertenece")

    class Meta:
        db_table = 'participacion'
        ordering = ['equipo', '-capitan']


