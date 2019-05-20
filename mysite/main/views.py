from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib import messages
from django.http import HttpResponse
from .models import Residencia, Subasta
from main.forms import RegistrationForm


def homepage(request):
    if request.user.is_authenticated: #si hay una sesion iniciada
        user = request.user
        return render(request=request,
                      template_name="main/homes/home_logged_in.html",
                      context={"residencias": Residencia.objects.all()[:3]})
    else: #si no hay una sesion iniciada
        return render(request=request,
                      template_name="main/homes/home.html")


def register(request):
    #si la request es tipo POST es porque el usuario nos mando info
    #click en "registrarse"
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid(): #si el form fue completado correctamente
            user = form.save() #registramos el usuario
            auth_login(request, user) #iniciamos su sesion automaticamente
            return redirect("main:homepage") #los mandamos a home
        else: #si se completo mal el form
            for msg in form.error_messages:
                print(form.error_messages[msg]) #muestro los errores
    #es una request normal
    form = RegistrationForm
    return render(request=request,
                  template_name="main/authentication/register.html",
                  context={"form":form})

def login(request):
    #si la request es info enviada por el usuario
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid(): #si la form esta bien completada
            username = form.cleaned_data["username"] #obtengo el username de la form
            password = form.cleaned_data["password"] #obtengo la pass de la form
            user = authenticate(username=username, password=password) #valido el usuario
            if user is not None: #si es valido
                auth_login(request, user) #inicio la sesion
                return redirect("main:homepage") #lo mando a homepage
            else: #datos invalidos
                pass#messages.error(request, "Nombre de usuario o contraseña inválidos.")
        else: #se lleno mal la form
            pass
            #messages.error(request, "Datos inválidos.")
    #la request es normal
    form = AuthenticationForm
    return render(request=request,
                  template_name="main/authentication/login.html",
                  context={"form":form})

def logout(request):
    auth_logout(request)
    #messages.info(request, "Sesion cerrada")
    return redirect("main:homepage")

def buscar_residencias(request):
    paises = set(r.pais for r in Residencia.objects.all())
    pasajeros = set(r.personas for r in Residencia.objects.all())
    return render(request=request,
                  template_name="main/residencias/buscar_residencias.html",
                  context={"residencias": Residencia.objects.all,
                           "paises": paises,
                           "pasajeros": pasajeros})

def residencia(request, id_residencia):
    res = Residencia.objects.get(id=id_residencia)
    subastas = Subasta.objects.filter(residencia=id_residencia)
    user = request.user
    return render(request=request,
                  template_name="main/residencias/ver_residencia.html",
                  context={"residencia": res,
                           "subastas": subastas,
                           "usuario": user})
