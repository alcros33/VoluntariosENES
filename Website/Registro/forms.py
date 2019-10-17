#coding=utf-8
# django imports
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from django.db import transaction
from django.contrib.admin.widgets import AdminDateWidget
from django.utils.translation import ugettext, ugettext_lazy as _
# file imports
from .models import *

# Validator string that only contains digits
def str_digits(value):
    if not str.isdigit(value):
        raise forms.ValidationError(_("Sólo puede contener números"), code='invalid')

### VOLUNTARIO FORMS ###
class SignupFormV(UserCreationForm):
    nombre = forms.CharField(max_length=256, label=_("Nombre Completo"), required=True)
    telefono = forms.CharField(max_length=10, min_length=10,
                               label=_("Teléfono Móvil"), required=True, validators=[str_digits])
    email = forms.EmailField(required=True)
    num_cuenta_unam = forms.CharField(max_length=9, min_length=9, label=_("Número de Cuenta UNAM"),
                                      required=True, validators=[str_digits])

    #Check unique
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Ese email ya existe"), code='taken')
        return email

    #Check unique
    def clean_num_cuenta_unam(self):
        value = self.cleaned_data['num_cuenta_unam']
        if Voluntario.objects.filter(num_cuenta_unam=value).exists():
            raise forms.ValidationError(_("Ese número de cuenta ya existe"), code='taken')
        return value

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_voluntario = True
        user.email = self.cleaned_data.get('email')
        user.save()
        voluntario = Voluntario.objects.create(user=user)

        voluntario.nombre = self.cleaned_data.get('nombre')
        voluntario.telefono = self.cleaned_data.get('telefono')
        voluntario.email = self.cleaned_data.get('email')
        voluntario.num_cuenta_unam = self.cleaned_data.get('num_cuenta_unam')
        voluntario.save()
        return user

class VoluntarioForm(forms.ModelForm):
    telefono = forms.CharField(max_length=10, min_length=10, label=_("Teléfono"), required=True,
                               validators=[str_digits],
                               widget=forms.widgets.TextInput(attrs={'style': 'width:100%'}))

    class Meta:
        model = Voluntario
        fields = ['nombre', 'telefono', 'foto']
        widgets = {
            'foto': forms.widgets.FileInput(attrs={'style': 'color:white'}),
            'nombre': forms.widgets.TextInput(attrs={'style': 'width:100%'}),
        }

### ORGANIZADOR FORMS ###
# Signup for Org
class SignupFormO(UserCreationForm):
    nombre = forms.CharField(max_length=256, label=_("Nombre Completo"), required=True)
    tele_m = forms.CharField(max_length=10, min_length=10,
                             label=_("Teléfono Móvil"), required=True, validators=[str_digits])
    tele_o = forms.CharField(max_length=10, min_length=10,
                             label=_("Teléfono Oficina"), required=False, validators=[str_digits])
    email = forms.EmailField(required=True)
    id_ins = forms.UUIDField(required=True, label=_("ID Institución"),
                             help_text=_("Identificador que debe proveerte tu institución"))

    #Revisar si ya existe
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Ese email ya existe"), code='taken')
        return email

    #Revisar si existe
    def clean_id_ins(self):
        value = self.cleaned_data['id_ins']
        if not Institucion.objects.filter(id=value).exists():
            raise forms.ValidationError(_("Institución no registrada"), code='taken')
        return value

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_organizador = True
        user.email = self.cleaned_data.get('email')
        user.save()
        inst = Institucion.objects.get(id=self.cleaned_data['id_ins'])
        organi = Organizador.objects.create(user=user, institucion=inst)

        organi.nombre = self.cleaned_data.get('nombre')
        organi.tel_movil = self.cleaned_data.get('tele_m')
        organi.tel_oficina = self.cleaned_data.get('tele_o')
        organi.email = self.cleaned_data.get('email')
        organi.save()
        return user

class EventForm(forms.ModelForm):

    class Meta:
        model = Evento
        fields = ['nombre', 'fecha', 'lugar', 'num_equipos',
                  'url_pagina', 'foto', 'descripcion']
        widgets = {
            'foto': forms.widgets.FileInput(attrs={'style': 'color:white'}),
            'nombre': forms.widgets.TextInput(attrs={'style': 'width:100%'}),
            'lugar': forms.widgets.TextInput(attrs={'style': 'width:100%'}),
            'num_equipos': forms.widgets.Select(choices=[(i, i) for i in range(1, 11)]),
            'url_pagina': forms.widgets.URLInput(attrs={'style': 'width:100%'}),
            'fecha': forms.widgets.DateInput(attrs={'style': 'width:100%'}),
        }

class OrganizadorForm(forms.ModelForm):
    tel_movil = forms.CharField(max_length=10, min_length=10, label=_("Teléfono Móvil"), required=True,
                                validators=[str_digits],
                                widget=forms.widgets.TextInput(attrs={'style': 'width:100%'}))
    tel_oficina = forms.CharField(max_length=10, min_length=10, label=_("Teléfono Oficina"), required=False,
                                  validators=[str_digits],
                                  widget=forms.widgets.TextInput(attrs={'style': 'width:100%'}))

    class Meta:
        model = Organizador
        fields = ['nombre', 'tel_movil', 'tel_oficina', 'foto']
        widgets = {
            'foto': forms.widgets.FileInput(attrs={'style': 'color:white'}),
            'nombre': forms.widgets.TextInput(attrs={'style': 'width:100%'}),
        }

# Change teams and captains in event
class ParticipacionForm(forms.ModelForm):
    class Meta:
        model = Participacion
        fields = ['equipo', 'capitan']
        widgets = {
            'equipo': forms.widgets.Select(choices=[(i, i) for i in range(10)]),
            'capitan': forms.widgets.CheckboxInput()
        }
