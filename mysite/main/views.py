from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate, get_user_model
from django.contrib import messages
from django.http import HttpResponse
from .models import Residencia, Subasta
from main.forms import RegistrationForm, MontoPujaForm, BuscarResidenciaForm, InvertirTipoForm, EditarPerfilForm, PaymentForm
from django.forms import ValidationError
import datetime
from django.contrib.auth.views import update_session_auth_hash

def homepage(request):
    if request.user.is_authenticated: #si hay una sesion iniciada
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
        user_form = RegistrationForm(request.POST)
        cc_form = PaymentForm(request.POST)
        if user_form.is_valid() and cc_form.is_valid(): #si el form fue completado correctamente
            user = user_form.save(commit=False)
            tarjeta = cc_form.save()
            user.metodo_de_pago = tarjeta
            user.save()
            auth_login(request, user) #iniciamos su sesion automaticamente
            return redirect("main:homepage") #los mandamos a home
        else: #si se completo mal el form
            for msg in form.error_messages:
                print(form.error_messages[msg]) #muestro los errores
    #es una request normal
    else:
        user_form = RegistrationForm()
        cc_form = PaymentForm()
    return render(request=request,
                  template_name="main/authentication/register.html",
                  context={"user_form":user_form,"cc_form":cc_form})

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
    else:
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
    residencias = Residencia.objects.all()
    subastas = []
    errores = ""
    if request.method == 'POST':
        form = BuscarResidenciaForm(request.POST)
        if form.is_valid():
            fecha_inicio = form.cleaned_data.get("inicio")
            fecha_fin = form.cleaned_data.get("fin")
            pasa_form = form.cleaned_data.get("pasajeros")
            pais_form = form.cleaned_data.get("pais")
            ciudad_form = form.cleaned_data.get("ciudad")
            #si se completan todos los campos
            if pasa_form != None and pais_form != "" and ciudad_form != "":
                subastas = Subasta.objects.filter(dia_inicial__gte = fecha_inicio,
                dia_inicial__lte = fecha_fin, residencia__personas = pasa_form,
                residencia__pais = pais_form, residencia__ciudad = ciudad_form)
            #si no se completan los pasajeros
            elif pais_form != "" and ciudad_form != "":
                subastas = Subasta.objects.filter(dia_inicial__gte = fecha_inicio,
                dia_inicial__lte = fecha_fin, residencia__pais = pais_form,
                residencia__ciudad = ciudad_form)
            #si no se completa el pais
            elif pasa_form != None and ciudad_form != "":
                subastas = Subasta.objects.filter(dia_inicial__gte = fecha_inicio,
                dia_inicial__lte = fecha_fin, residencia__personas = pasa_form,
                residencia__ciudad = ciudad_form)
            #si no se completa la ciudad
            elif pais_form != "" and pasa_form != None:
                subastas = Subasta.objects.filter(dia_inicial__gte = fecha_inicio,
                dia_inicial__lte = fecha_fin, residencia__personas = pasa_form,
                residencia__pais = pais_form)
            #solo se completa pasajeros
            elif pasa_form != None:
                subastas = Subasta.objects.filter(dia_inicial__gte = fecha_inicio,
                dia_inicial__lte = fecha_fin, residencia__personas = pasa_form)
            #solo se completa pais
            elif pais_form != "":
                subastas = Subasta.objects.filter(dia_inicial__gte = fecha_inicio,
                dia_inicial__lte = fecha_fin, residencia__pais = pais_form)
            #solo se completa ciudad:
            elif ciudad_form != "":
                subastas = Subasta.objects.filter(dia_inicial__gte = fecha_inicio,
                dia_inicial__lte = fecha_fin, residencia__ciudad = ciudad_form)
            #si no se completa ningún otro campo
            else:
                subastas = Subasta.objects.filter(dia_inicial__gte = fecha_inicio,
                                                  dia_inicial__lte = fecha_fin)
        residencias = set([Residencia.objects.get(id=s.residencia.id) for s in subastas])
    else:
        form = BuscarResidenciaForm()
    paises = set(r.pais for r in Residencia.objects.all())
    ciudades = set(r.ciudad for r in Residencia.objects.all())
    pasajeros = set(r.personas for r in Residencia.objects.all())
    return render(request=request,
                  template_name="main/residencias/buscar_residencias.html",
                  context={"residencias": residencias,
                           "paises": paises,
                           "pasajeros": pasajeros,
                           "ciudades": ciudades,
                           "form": form})

def residencia(request, id_residencia):
    import datetime
    res = Residencia.objects.get(id=id_residencia)
    subastas = Subasta.objects.filter(residencia=id_residencia)
    user = request.user
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
    if request.method == "POST":
        form = MontoPujaForm(request.POST,user=request.user,subasta=sub)
        if form.is_valid():
            monto = form.cleaned_data.get("monto")
            sub.pujar(request.user, monto)
            sub.save()
    else:
        form = MontoPujaForm(user=request.user,subasta=sub)
    import datetime
    inscripto = sub.esta_inscripto(request.user)
    return render(request=request,
                  template_name="main/subastas/ver_subasta.html",
                  context={"subasta": sub,
                           "inscripto": inscripto,
                           "form": form})

def inscribirse(request, id_residencia, id_subasta):
    sub = Subasta.objects.get(id=id_subasta)
    sub.inscribir_usuario(request.user)
    #Obtengo el url desde donde se llamo a este link
    referer = request.META.get("HTTP_REFERER")
    return redirect(referer)

def abandonar(request, id_residencia, id_subasta):
    sub = Residencia.objects.get(id=id_residencia).subastas.get(id=id_subasta)
    sub.abandonar_subasta(request.user)
    #Obtengo el url desde donde se llamo a este link
    referer = request.META.get("HTTP_REFERER")
    return redirect(referer)

def perfil(request):
    if request.method == "POST":
        user_type_form = InvertirTipoForm(request.POST,user=request.user)
        if user_type_form.is_valid():
            request.user.invertir_tipo()
            request.user.save()
            messages.success(request, 'Ahora eres un usuario '+request.user.user_type()+'.')
    else:
        user_type_form = InvertirTipoForm(user=request.user)
    return render(request=request,
                  template_name="main/user/profile.html",
                  context={"user_type_form": user_type_form})

def editar_perfil(request):
    if request.method == "POST":
        form = EditarPerfilForm(request.POST,instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Datos cambiados con éxito.')
            update_session_auth_hash(request, form.instance)
            return redirect("main:perfil")
    else:
        form = EditarPerfilForm(instance=request.user)
    return render(request=request,
                  template_name="main/user/editar_perfil.html",
                  context={"form":form})

def cambiar_contraseña(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user,request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contraseña cambiada con éxito.')
            update_session_auth_hash(request, form.user)
            return redirect("main:perfil")
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request=request,
                  template_name="main/user/cambiar_contraseña.html",
                  context={"form":form})

def eliminar_usuario(request):
    request.user.eliminar_usuario()
    messages.success(request, 'Cuenta eliminada con éxito.')
    return redirect("main:eliminar_usuario_exito")

def eliminar_usuario_exito(request):
    return render(request=request,
                  template_name="main/user/eliminar_usuario_exito.html",
                  context={})
