from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate, get_user_model
from django.contrib import messages
from django.http import HttpResponse
from .models import Residencia, Subasta, Usuario
from main.forms import RegistrationForm, MontoPujaForm
from django.forms import ValidationError

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
    form = RegistrationForm()
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
            messages.error(request, "Nombre de usuario o contraseña inválidos.")

    #la request es normal
    form = AuthenticationForm
    return render(request=request,
                  template_name="main/authentication/login.html",
                  context={"form":form})

def logout(request):
    auth_logout(request)
    #messages.info(request, "Sesion cerrada")
    return redirect("main:homepage")

# @login_required
# @transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, _('Your profile was successfully updated!'))
            return redirect('settings:profile')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'main/authentication/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def buscar_residencias(request):
    paises = set(r.pais for r in Residencia.objects.all())
    pasajeros = set(r.personas for r in Residencia.objects.all())
    return render(request=request,
                  template_name="main/residencias/buscar_residencias.html",
                  context={"residencias": Residencia.objects.all,
                           "paises": paises,
                           "pasajeros": pasajeros})

def residencia(request, id_residencia):
    import datetime
    res = Residencia.objects.get(id=id_residencia)
    subastas = Subasta.objects.filter(residencia=id_residencia)
    user = request.user.usuario
    hoy = datetime.datetime.now().date()
    inscripto = {}
    for s in subastas:
        inscripto[s] = s.esta_inscripto(user)
    return render(request=request,
                  template_name="main/residencias/ver_residencia.html",
                  context={"residencia": res,
                           "inscripto": inscripto,
                           "usuario": user,
                           "hoy": hoy})

def subasta(request, id_subasta):
    sub = Subasta.objects.get(id=id_subasta)
    error = ''
    if request.method == "POST":
        form = MontoPujaForm(request.POST)
        if form.is_valid():
            monto = form.cleaned_data.get("monto")
            if (monto < sub.puja_actual().dinero_pujado + 50):
                # form.add_error('monto','El monto a pujar debe superar al actual por al menos $50.')
                # form.add_error('monto',ValidationError('El monto a pujar debe superar al actual por al menos $50.', code='no supera'))
                # print(monto,'$50',form.has_error('monto'))
                # error = 'El monto a pujar debe superar al actual por al menos $50.'
                pass
            elif not(usuario_pujador.tiene_creditos()):
                # form.add_error('monto','No tienes créditos suficientes para realizar una puja.')
                # print(monto,'sin credito')
                # error = 'No tienes créditos suficientes para realizar una puja.'
                pass
            else:
                # error = ''
                # print(monto)
                sub.pujar(request.user.usuario, monto)
    form = MontoPujaForm()
    import datetime
    inscripto = sub.esta_inscripto(request.user.usuario)
    return render(request=request,
                  template_name="main/subastas/ver_subasta.html",
                  context={"subasta": sub,
                           "inscripto": inscripto,
                           "form": form,
                           "error": error})

def inscribirse(request, id_residencia, id_subasta):
    sub = Subasta.objects.get(id=id_subasta)
    sub.inscribir_usuario(request.user.usuario)
    #Obtengo el url desde donde se llamo a este link
    referer = request.META.get("HTTP_REFERER")
    return redirect(referer)
