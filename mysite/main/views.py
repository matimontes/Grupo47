from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate, get_user_model
from django.contrib import messages
from django.http import HttpResponse
from .models import Residencia, Subasta, Suscripcion, HotSale, SemanaPasada, Notificacion, SemanaReservada
from main.forms import RegistrationForm, MontoPujaForm, BuscarResidenciaForm, InvertirTipoForm, EditarPerfilForm, PaymentForm, OpinarForm
from django.forms import ValidationError
import datetime
from django.contrib.auth.views import update_session_auth_hash

def homepage(request):
    if request.user.is_authenticated: #si hay una sesion iniciada
        return render(request=request,
                      template_name="main/homes/home_logged_in.html",
                      context={"residencias": Residencia.objects.all()[:3],
                               "notificaciones": request.user.notificaciones.all()})
    else: #si no hay una sesion iniciada
        return render(request=request,
                      template_name="main/homes/home.html",
                      context={"residencias": Residencia.objects.all()[:3]})


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
            messages.success(request, 'Cuenta registrada.')
            auth_login(request, user) #iniciamos su sesion automaticamente
            return redirect("main:homepage") #los mandamos a home
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
            messages.error(request, "Mail o contraseña inválidos.")

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
        'profile_form': profile_form,
        "notificaciones": request.user.notificaciones.all()
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
                           "form": form,
                           "notificaciones": request.user.notificaciones.all()})


def ver_hotsales(request):
    hotsales = []
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
                hotsales = HotSale.objects.filter(dia_inicial__gte = fecha_inicio,
                dia_inicial__lte = fecha_fin, residencia__personas = pasa_form,
                residencia__pais = pais_form, residencia__ciudad = ciudad_form)
            #si no se completan los pasajeros
            elif pais_form != "" and ciudad_form != "":
                hotsales = HotSale.objects.filter(dia_inicial__gte = fecha_inicio,
                dia_inicial__lte = fecha_fin, residencia__pais = pais_form,
                residencia__ciudad = ciudad_form)
            #si no se completa el pais
            elif pasa_form != None and ciudad_form != "":
                hotsales = HotSale.objects.filter(dia_inicial__gte = fecha_inicio,
                dia_inicial__lte = fecha_fin, residencia__personas = pasa_form,
                residencia__ciudad = ciudad_form)
            #si no se completa la ciudad
            elif pais_form != "" and pasa_form != None:
                hotsales = HotSale.objects.filter(dia_inicial__gte = fecha_inicio,
                dia_inicial__lte = fecha_fin, residencia__personas = pasa_form,
                residencia__pais = pais_form)
            #solo se completa pasajeros
            elif pasa_form != None:
                hotsales = HotSale.objects.filter(dia_inicial__gte = fecha_inicio,
                dia_inicial__lte = fecha_fin, residencia__personas = pasa_form)
            #solo se completa pais
            elif pais_form != "":
                hotsales = HotSale.objects.filter(dia_inicial__gte = fecha_inicio,
                dia_inicial__lte = fecha_fin, residencia__pais = pais_form)
            #solo se completa ciudad:
            elif ciudad_form != "":
                hotsales = HotSale.objects.filter(dia_inicial__gte = fecha_inicio,
                dia_inicial__lte = fecha_fin, residencia__ciudad = ciudad_form)
            #si no se completa ningún otro campo
            else:
                hotsales = HotSale.objects.filter(dia_inicial__gte = fecha_inicio,
                                                  dia_inicial__lte = fecha_fin)
        residencias = set([Residencia.objects.get(id=h.residencia.id) for h in hotsales])
    else:
        form = BuscarResidenciaForm()
        residencias = Residencia.objects.all()
    paises = set(r.pais for r in Residencia.objects.all())
    ciudades = set(r.ciudad for r in Residencia.objects.all())
    pasajeros = set(r.personas for r in Residencia.objects.all())
    return render(request=request,
                  template_name="main/residencias/buscar_residencias.html",
                  context={"residencias": residencias,
                           "paises": paises,
                           "pasajeros": pasajeros,
                           "ciudades": ciudades,
                           "form": form,
                           "notificaciones": request.user.notificaciones.all()})

def residencia(request, id_residencia):
    import datetime
    res = Residencia.objects.get(id=id_residencia)
    subastas = Subasta.objects.filter(residencia=id_residencia)
    user = request.user
    inscripto = {}
    for s in subastas:
        inscripto[s] = s.esta_inscripto(user)
    opinar = []
    for o in user.opiniones_disponibles(res):
        print(o)
        opinar.append(o)
    opiniones = []
    promedio = 0
    for s in SemanaPasada.objects.filter(residencia=id_residencia):
        if s.opinion != None:
            opiniones.append(s.opinion)
            promedio += s.opinion.puntaje
    promedio /= len(opiniones) if len(opiniones)!= 0 else 1
    return render(request=request,
                  template_name="main/residencias/ver_residencia.html",
                  context={"residencia": res,
                           "inscripto": inscripto,
                           "usuario": user,
                           "notificaciones": request.user.notificaciones.all(),
                           "opinar":opinar,
                           "opiniones": opiniones,
                           "promedio": "%.1f" % promedio})

def residencia_hotsales(request, id_residencia):
    res = Residencia.objects.get(id=id_residencia)
    hotsales = HotSale.objects.filter(residencia=id_residencia)
    user = request.user
    return render(request=request,
                  template_name="main/residencias/ver_residencia_hotsales.html",
                  context={"residencia": res,
                           "hotsales": hotsales,
                           "usuario": user,
                           "notificaciones": request.user.notificaciones.all()})

def subasta(request, id_subasta):
    try:
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
                               "form": form,
                               "notificaciones": request.user.notificaciones.all()})
    except:
        return render(request=request,
                      template_name="main/subastas/no_existe.html",
                      context={"notificaciones": request.user.notificaciones.all()})

def inscribirse(request, id_residencia, id_subasta):
    if not request.user.is_staff:
        sub = Subasta.objects.get(id=id_subasta)
        sub.inscribir_usuario(request.user)
    #Obtengo el url desde donde se llamo a este link
    referer = request.META.get("HTTP_REFERER")
    return redirect(referer)

def abandonar(request, id_residencia, id_subasta):
    sub = Residencia.objects.get(id=id_residencia).subastas.get(id=id_subasta)
    sub.abandonar_subasta(request.user)
    messages.success(request, 'Has abandonado la subasta con éxito.')
    #Obtengo el url desde donde se llamo a este link
    referer = request.META.get("HTTP_REFERER")
    return redirect(referer)

def perfil(request):
    suscripciones = Suscripcion.objects.all()
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
                  context={"user_type_form": user_type_form,
                           "suscripciones": suscripciones[0],
                           "notificaciones": request.user.notificaciones.all()})

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
                  context={"form":form,
                  "notificaciones": request.user.notificaciones.all()})

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
                  context={"form":form,
                  "notificaciones": request.user.notificaciones.all()})

def eliminar_usuario(request):
    request.user.eliminar_usuario()
    messages.success(request, 'Cuenta eliminada con éxito.')
    return redirect("main:eliminar_usuario_exito")

def eliminar_usuario_exito(request):
    return render(request=request,
                  template_name="main/user/eliminar_usuario_exito.html",
                  context={})

def mis_semanas(request):
    return render(request=request,
                  template_name="main/user/mis_semanas.html",
                  context={"notificaciones": request.user.notificaciones.all()})

def reserva(request, id_subasta):
    semana=Subasta.objects.get(id=id_subasta)
    for inscripto in semana.usuarios_inscriptos.all():
        Notificacion.objects.create(usuario=inscripto,
        info="Alguien reservó una semana para la que estabas inscripto!")
    request.user.reservar_premium(semana)
    #vuelve a la residencia porque la subasta fue borrada
    return redirect(f"/ver_residencia/{semana.residencia.id}/")

def reserva_hotsale(request, id_hotsale):
    semana=HotSale.objects.get(id=id_hotsale)
    semana.reservar(request.user, semana.precio_reserva, False)
    return redirect(f"/ver_residencia/{semana.residencia.id}/hotsales/")

def opinar(request, id_semana):
    semana = SemanaPasada.objects.get(id=id_semana)
    if request.method == "POST":
        form = OpinarForm(request.POST)
        if form.is_valid():
            form.save()
            semana.opinion = form.instance
            semana.save()
            messages.success(request, 'opinión realizada con éxito.')
            return redirect("main:mis_semanas")
    else:
        form = OpinarForm()
    return render(request=request,
                  template_name="main/user/opinar.html",
                  context={"form":form,
                  "semana":semana,
                  "notificaciones": request.user.notificaciones.all()})

def leer_notificaciones(request):
    notificaciones = Notificacion.objects.filter(usuario=request.user)
    for n in notificaciones.all():
        n.delete()
    referer = request.META.get("HTTP_REFERER")
    return redirect(referer)

def cancelar_reserva(request,id_reserva):
    semana=SemanaReservada.objects.get(id=id_reserva)
    semana.cancelar_semana()
    return redirect("main:mis_semanas")
