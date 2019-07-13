"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("buscar_residencias/", views.buscar_residencias, name="buscar_residencias"),
    path("ver_residencia/<id_residencia>/", views.residencia, name="residencia"),
    path("subasta/<id_subasta>/", views.subasta, name="subasta"),
    path("inscribirse/<id_residencia>/<id_subasta>/", views.inscribirse, name="inscribirse"),
    path("abandonar/<id_residencia>/<id_subasta>/", views.abandonar, name="abandonar"),
    path("perfil/", views.perfil, name="perfil"),
    path("editar_perfil/", views.editar_perfil, name="editar_perfil"),
    path("cambiar_contraseña/", views.cambiar_contraseña, name="cambiar_contraseña"),
    path("eliminar_usuario/", views.eliminar_usuario, name="eliminar_usuario"),
    path("eliminar_exito/", views.eliminar_usuario_exito, name="eliminar_usuario_exito"),
    path("reserva/<id_subasta>/", views.reserva, name="reserva"),
    path("hotsales/", views.ver_hotsales, name="ver_hotsales"),
    path("ver_residencia/<id_residencia>/hotsales/", views.residencia_hotsales, name="residencia_hotsales"),
    path("reserva_hotsale/<id_hotsale>/", views.reserva_hotsale, name="reserva_hotsale"),
    path("perfil/mis_semanas/", views.mis_semanas, name="mis_semanas"),
    path("opinar/<id_semana>/", views.opinar, name="opinar"),
    path("leer_notificaciones", views.leer_notificaciones, name="leer_notificaciones"),
    path("cancelar_reserva/<id_reserva>/", views.cancelar_reserva, name="cancelar_reserva"),
]
