#coding=utf-8
#django imports
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.forms import modelformset_factory
from django.http import Http404, HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import CreateView, UpdateView

from .forms import *
from .models import *


def refresh_session_expire(func):
    def wrapper(request, *args, **kwargs):
        request.session.set_expiry(request.session.get_expiry_age())
        return func(request, *args, **kwargs)
    return wrapper

# Auth views
class SignupView(CreateView):
    model = User
    form_class = None
    user_type = ""
    template_name = "Registro/signup.html"

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = self.user_type
        kwargs['pTitle'] = self.user_type.capitalize()
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        auth.login(self.request, user)
        return redirect('home')

signup_volun = SignupView.as_view(form_class=SignupFormV, user_type="voluntario")
signup_org = SignupView.as_view(form_class=SignupFormO, user_type="organizador")

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth.login(request, form.get_user())
            return redirect('home')
    else:
        form = AuthenticationForm(request)

    return render(request, 'Registro/login.html', {'form': form})

def logout_view(request):
    auth.logout(request)
    return redirect('index')

@refresh_session_expire
def index_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'index.html', {})

# Active Events TEST OK
@login_required(login_url='login')
@refresh_session_expire
def active_events(request):
    queryset = Evento.objects.filter(activo__exact=True)
    context = {'event_list': queryset, 'pTitle': "Eventos Activos"}
    return render(request, 'Registro/list_event.html', context)

# Old Events TEST OK
@login_required(login_url='login')
@refresh_session_expire
def old_events(request):
    queryset = Evento.objects.filter(activo__exact=False)
    context = {'event_list': queryset, 'pTitle': "Eventos Archivados"}
    return render(request, 'Registro/list_event.html', context)

# Event Details TEST OK
def _event_process_volun(event, volun, postdata):
    try:
        part = Participacion.objects.get(voluntario=volun, evento=event)
    except Participacion.DoesNotExist:
        part = None
    if postdata:
        if postdata.get('ConfirmIns') == "Confirmado" and not part:
            part = Participacion.objects.create(voluntario=volun, evento=event)
            part.save()
        elif postdata.get('ConfirmDel') == "Confirmado" and part:
            part.delete()
            part = None
    return {'evento': event, 'participacion': part,}

@login_required(login_url='login')
@refresh_session_expire
def event_details(request, pk):
    event = get_object_or_404(Evento, id=pk)
    pdata = request.POST if request.method == "POST" else dict()

    if request.user.is_voluntario:
        context = _event_process_volun(event, request.user.voluntario, pdata)

    elif request.user.is_organizador:
        if pdata and request.user.organizador == event.organizador:
            if pdata.get('ConfirmDelete') == "Confirmado":
                event.delete()
                return redirect('home')
            if pdata.get('ConfirmClose') == "Confirmado":
                event.activo = False
                event.save()
        context = {'evento': event, 'participacion': None,}

    return render(request, 'Registro/event_details.html', context=context)

# Organizador details TEST OK
@login_required(login_url='login')
@refresh_session_expire
def org_details(request, pk):
    organizador = get_object_or_404(Organizador, user=pk)
    eventos = Evento.objects.filter(organizador__exact=pk)

    context = context={'organizador': organizador, 'eventos': eventos}

    return render(request, 'Registro/org_details.html', context)

# Voluntario details TEST OK
@login_required(login_url='login')
@refresh_session_expire
def volun_details(request, pk):
    voluntario = get_object_or_404(Voluntario, user=pk)
    return render(request, 'Registro/volun_details.html', {'voluntario': voluntario})

# Edit your profile TEST OK
@login_required(login_url='login')
@refresh_session_expire
def edit_profile(request):
    pk = request.user.pk
    if request.user.is_voluntario:
        FormClass = VoluntarioForm
        redirect_to = reverse('volun_details', args=[str(pk)])
        Model = Voluntario
    elif request.user.is_organizador:
        FormClass = OrganizadorForm
        redirect_to = reverse('org_details', args=[str(pk)])
        Model = Organizador

    # Request user is not owner
    if request.user.id != pk:
        return redirect('home')

    profile = get_object_or_404(Model, user=pk)

    if request.method == "POST":
        form = FormClass(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect(redirect_to)
    else:
        form = FormClass(instance=profile)

    context = {'form': form, 'pTitle': 'Perfil'}
    return render(request, 'Registro/edit_form.html', context)

## ORGANIZADOR EXCLUSIVE ###
org_required = user_passes_test(lambda u: u.is_authenticated and u.is_organizador,
                                login_url='login', redirect_field_name='')
class OrgRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.is_organizador

# My events TEST OK
@org_required
@refresh_session_expire
def my_events(request):
    queryset = Evento.objects.filter(organizador__exact=request.user.organizador)
    context = {'event_list': queryset, 'pTitle': "Mis Eventos"}
    return render(request, 'Registro/list_event.html', context)

# Signed up for event TEST OK
@org_required
@refresh_session_expire
def event_participations(request, pk):
    event = get_object_or_404(Evento, id=pk)

    if event.activo or (request.user.id != event.organizador.pk):
        return redirect(reverse('devent_details', args=[str(pk)]))

    inscritos = Participacion.objects.filter(evento__exact=event)
    context = {'evento': event, 'inscritos': inscritos}

    return render(request, 'Registro/event_participations.html', context)

# Edit Participacion Signed up for event TEST OK
@org_required
@refresh_session_expire
def edit_participations(request, pk):
    event = get_object_or_404(Evento, id=pk)

    if event.activo or (request.user.id != event.organizador.pk):
        return redirect(reverse('devent_details', args=[str(pk)]))

    inscritos = Participacion.objects.filter(evento=event)

    PartiFormSet = modelformset_factory(Participacion, form=ParticipacionForm, extra=0)

    if request.method == "POST":
        formset = PartiFormSet(request.POST, queryset=inscritos)
        if formset.is_valid():
            formset.save()
            return redirect(reverse('event_participations', args=[str(event.id)]))
    else:
        formset = PartiFormSet(queryset=inscritos)

    context = {'evento': event, 'inscritos': inscritos, 'formset': formset}

    return render(request, 'Registro/edit_participations.html', context=context)

# Create an event TEST OK
class EventCreateView(OrgRequiredMixin, CreateView):
    template_name = 'Registro/create_form.html'
    form_class = EventForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pTitle'] = "Evento"
        return context
    
    @transaction.atomic
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.organizador = self.request.user.organizador
        self.object.save()
        return redirect(self.get_success_url())

# Edit Event view TEST OK
class EventEditView(OrgRequiredMixin, UpdateView):
    template_name = 'Registro/edit_form.html'
    form_class = EventForm
    model = Evento

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pTitle'] = "Evento"
        return context
    
    def get(self, request, *args, **kwargs):
        if self.get_object().organizador != self.request.user.organizador:
            return redirect(self.get_success_url())
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.get_object().organizador != self.request.user.organizador:
            return redirect(self.get_success_url())
        return super().post(request, *args, **kwargs)
