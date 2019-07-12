from __future__ import unicode_literals

from django.db import models
from datetime import date, timedelta
from django.utils import timezone

from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from creditcards.models import CardNumberField, CardExpiryField, SecurityCodeField
from creditcards import types
from django.core.validators import MaxValueValidator, MinValueValidator

from django.contrib.auth.base_user import BaseUserManager

# Create your models here.
class Tarjeta(models.Model):
	cc_number = CardNumberField(_('card number'), default="4532661247991100")
	cc_expiry = CardExpiryField(_('expiration date'), default="11/19")
	cc_code = SecurityCodeField(_('security code'), default="374")

	def numero_censurado(self):
		return '*'*(len(self.cc_number)-4)+self.cc_number[-4:]

	def __str__(self):
		return self.get_type()+' '+self.numero_censurado()

	def get_type(self):
		tipo = types.get_type(self.cc_number)
		if tipo == types.CC_TYPE_VISA:
			return "VISA"
		elif tipo == types.CC_TYPE_AMEX:
			return "AMEX"
		else:
			return "GENERIC"

class UserManager(BaseUserManager):
	use_in_migrations = True

	def _create_user(self, email, password, **extra_fields):
		"""
		Creates and saves a User with the given email and password.
		"""
		if not email:
			raise ValueError('The given email must be set')
		email = self.normalize_email(email)
		user = self.model(email=email, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_user(self, email=None, password=None, **extra_fields):
		extra_fields.setdefault('is_staff', False)
		extra_fields.setdefault('is_superuser', False)
		return self._create_user(email, password, **extra_fields)

	def create_superuser(self, email, password, **extra_fields):
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)

		if extra_fields.get('is_staff') is not True:
			raise ValueError('Superuser must have is_staff=True.')
		if extra_fields.get('is_superuser') is not True:
			raise ValueError('Superuser must have is_superuser=True.')

		extra_fields['date_of_birth']=date(1950,1,1)

		return self._create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
	email = models.EmailField(_('email address'), unique=True)
	first_name = models.CharField(_('nombre'), max_length=30, blank=True)
	last_name = models.CharField(_('apellido'), max_length=30, blank=True)
	date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
	is_active = models.BooleanField(_('active'), default=True)
	date_of_birth = models.DateField(_('fecha de nacimiento'))
	nacionalidad = models.CharField(max_length=50)
	creditos = models.IntegerField(default=2)
	premium = models.BooleanField(_('premium estatus'), default=False)
	is_staff = models.BooleanField(
		_('staff status'),
		default=False,
		help_text=_('Designates whether the user can log into this admin site.'),
	)
	metodo_de_pago = models.OneToOneField(
		'Tarjeta',
		on_delete=models.CASCADE,
		related_name='user'
		)

	objects = UserManager()

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = []

	class Meta:
		verbose_name = _('cliente')
		verbose_name_plural = _('clientes')

	def get_full_name(self):
		'''
		Returns the first_name plus the last_name, with a space in between.
		'''
		full_name = '%s %s' % (self.first_name, self.last_name)
		return full_name.strip()

	def get_short_name(self):
		'''
		Returns the short name for the user.
		'''
		return self.first_name

	def user_type(self):
		return 'premium' if self.premium else 'basico'

	def email_user(self, subject, message, from_email=None, **kwargs):
		'''
		Sends an email to this User.
		'''
		send_mail(subject, message, from_email, [self.email], **kwargs)

	def notificar_comienzo_subasta(self,subasta):
		Notificacion.objects.create(
		usuario=self,
		info="Comenzó una subasta a la que te habias inscripto!"
		)

	def tiene_creditos(self):
		return self.creditos > 0


	def vencimiento_de_creditos(self):
		if self.date_joined.month > date.today().month:
			return date(year=date.today().year,month=self.date_joined.month,day=self.date_joined.day)
		elif (self.date_joined.month == date.today().month) and (self.date_joined.day > date.today().day):
			return date(year=date.today().year,month=self.date_joined.month,day=self.date_joined.day)
		return date(year=(date.today().year+1),month=self.date_joined.month,day=self.date_joined.day)

	def quitar_credito(self):
		self.creditos -= 1

	def invertir_tipo(self):
		self.premium = not self.premium

	def eliminar_usuario(self):
		#Eliminar pujas
		for subasta in self.inscripciones.all():
			subasta.abandonar_subasta(self)
		#Pasar reservas a pendientes
		for reservas in self.semanas_reservadas.all():
		 	reservas.convertir_en_semana_en_espera()
		#Eliminar usuario de base de datos
		self.delete()

	def reservar_premium(self, semana):
		if self.premium and self.tiene_creditos():
			semana.reservar(self, semana.precio_reserva)
			self.creditos -= 1
			self.save()
			return True
		return False

class Notificacion(models.Model):
	info = models.CharField(max_length=200)
	usuario = models.ForeignKey('User', on_delete=models.CASCADE,related_name='notificaciones')

	def __str__(self):
		return self.info

from django.conf import settings

class Course(models.Model):
	slug = models.SlugField(max_length=100)
	name = models.CharField(max_length=100)
	tutor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class Residencia(models.Model):
	nombre = models.CharField(max_length=50)
	dirección = models.CharField(max_length=200)
	ciudad = models.CharField(max_length=100)
	pais = models.CharField(max_length=30)
	#fotos = SE IMPLEMENTA EN CLASE IMAGEN
	descripcion = models.TextField()
	habitaciones = models.IntegerField(default=0)
	personas = models.IntegerField(default=0)
	baños = models.IntegerField(default=0)
	#subastas = SE IMPLEMENTA EN SUBASTA
	#hotsales = SE IMPLEMENTA EN HOTSALE

	def __str__(self):
		return self.nombre

	class Meta:
		ordering = ['nombre']

	def primerFoto(self):
		if self.imagenes.exists():
			return self.imagenes.first().imagen.name[12:]
		else:
			return "fotos/68184730.jpg"

class Semana(models.Model):
	dia_inicial = models.DateField()
	precio_reserva = models.DecimalField(max_digits=11,decimal_places=2)

	def __str__(self):
		return self.residencia.nombre + " - De: " + self.dia_inicial.isoformat() + " a: " + self.dia_final().isoformat()

	def dia_final(self):
		return self.dia_inicial + timedelta(days=7)

	def coincide(self,fecha):
		return ((fecha > self.dia_inicial - timedelta(days=7)) and (fecha < self.dia_final()))

	def reservar(self,usuario,precio_reserva):
		SemanaReservada.objects.create(usuario=usuario,
			precio_reserva=precio_reserva,
			residencia=self.residencia,
			dia_inicial=self.dia_inicial)
		Notificacion.objects.create(usuario=usuario,
		info="La reserva se realizó correctamente.")
		self.delete()

	class Meta:
		abstract = True
		ordering = ['dia_inicial', 'residencia']

class Subasta(Semana):
	precio_inicial = models.DecimalField(max_digits=11,decimal_places=2)
	inicio_de_subasta = models.DateField()
	residencia = models.ForeignKey('Residencia',on_delete=models.CASCADE,related_name='subastas')
	usuarios_inscriptos = models.ManyToManyField('User',related_name='inscripciones')
	iniciada = models.BooleanField(default=False)
	#pujas CREADAS DESDE CLASE PUJA

	def fin_de_subasta(self):
		return (self.inicio_de_subasta + timedelta(days=3))

	def cantidad_de_inscriptos(self):
		return self.usuarios_inscriptos.count()

	def puja_actual(self):
		return self.pujas.first()

	def pujar(self,usuario_pujador,dinero_a_pujar):
		Puja.objects.create(usuario=usuario_pujador,dinero_pujado=dinero_a_pujar,subasta=self)

	def cancelar_puja(self,usuario):
		puja = self.puja_actual()
		if puja.usuario == usuario:
			puja.delete()
		else:
			#AGREGAR FUNCIONALIDAD
			pass

	def inscribir_usuario(self,usuario):
		self.usuarios_inscriptos.add(usuario)

	def anular_inscripcion_usuario(self,usuario):
		self.usuarios_inscriptos.remove(usuario)

	def esta_inscripto(self,usuario):
		return self.usuarios_inscriptos.filter(id=usuario.id).exists()

	def usuario_default(self):
		try:
			return User.objects.get(email='puja_default@hsh.com')
		except ObjectDoesNotExist:
			User.objects.create(email='puja_default@hsh.com',password='asdqwezxcfghrtyvbnjkluiom,.',date_of_birth=date(1950,1,1),first_name='Puja',last_name='Default',creditos=1000000)

	def convertir_en_semana_en_espera(self):
		SemanaEnEspera.objects.create(dia_inicial=self.dia_inicial,precio_reserva=self.precio_reserva,residencia=self.residencia)
		self.delete()

	def abandonar_subasta(self,usuario):
		self.anular_inscripcion_usuario(usuario)
		for puja in self.pujas.filter(usuario=usuario):
			puja.delete()
		if self.cantidad_de_inscriptos() == 0:
			self.convertir_en_semana_en_espera()

	def comenzar(self):
		self.iniciada = True
		Puja.objects.create(usuario=self.usuario_default(),dinero_pujado=self.precio_inicial,subasta=self)
		self.notificar_inscriptos()
		self.save(update_fields=['iniciada'])

	def finalizar(self):
		puja = self.puja_actual()
		if puja.usuario == self.usuario_default():
			self.convertir_en_semana_en_espera()
		else:
			puja.usuario.quitar_credito()
			self.reservar(puja.usuario,puja.dinero_pujado)

	def forzar_comienzo(self):
		if self.cantidad_de_inscriptos() == 0:
			self.convertir_en_semana_en_espera()
		else:
			self.inicio_de_subasta = date.today()
			self.save(update_fields=['inicio_de_subasta'])
			self.comenzar()

	def forzar_fin(self):
		if self.iniciada:
			self.finalizar()
			return True
		else:
			return False

	def notificar_inscriptos(self):
		for usuario in self.usuarios_inscriptos.all():
			usuario.notificar_comienzo_subasta(self)

class HotSale(Semana):
	residencia = models.ForeignKey('Residencia',on_delete=models.CASCADE,related_name='hotsales')

class SemanaReservada(Semana):
	usuario = models.ForeignKey('User',on_delete=models.CASCADE,related_name='semanas_reservadas')
	residencia = models.ForeignKey('Residencia',on_delete=models.CASCADE,related_name='semanas_reservadas')
	credito = models.BooleanField(default=True)

	def convertir_en_semana_en_espera(self):
		SemanaEnEspera.objects.create(dia_inicial=self.dia_inicial,precio_reserva=self.precio_reserva,residencia=self.residencia)
		self.delete()

	def terminar_semana(self):
		SemanaPasada.objects.create(dia_inicial=self.dia_inicial,precio_reserva=self.precio_reserva,residencia=self.residencia,usuario=self.usuario)
		self.usuario.quitar_credito()
		self.delete()

	def quitar_credito(self):
		self.credito = False

class SemanaPasada(Semana):
	usuario = models.ForeignKey('User',on_delete=models.CASCADE,related_name='semanas_pasadas')
	residencia = models.ForeignKey('Residencia',on_delete=models.CASCADE,related_name='semanas_pasadas')

	def convertir_en_semana_en_espera(self):
		SemanaEnEspera.objects.create(dia_inicial=self.dia_inicial,precio_reserva=self.precio_reserva,residencia=self.residencia)
		self.delete()

	def opino(self):
		if self.opinion.exists():
			True
		False

class SemanaEnEspera(Semana):
	residencia = models.ForeignKey('Residencia',on_delete=models.CASCADE,related_name='semanas_en_espera')

	def convertir_en_hotsale(self):
		HotSale.objects.create(dia_inicial=self.dia_inicial,precio_reserva=self.precio_reserva,residencia=self.residencia)
		self.delete()

class Puja(models.Model):
	usuario = models.ForeignKey('User',on_delete=models.CASCADE,related_name='pujas')
	dinero_pujado = models.DecimalField(max_digits=11,decimal_places=2)
	subasta = models.ForeignKey('Subasta',on_delete=models.CASCADE,related_name='pujas')

	class Meta:
		ordering = ['subasta','-dinero_pujado']

class Imagen(models.Model):
	residencia = models.ForeignKey(Residencia,on_delete=models.CASCADE,related_name='imagenes')
	imagen = models.ImageField(upload_to=('staticfiles/fotos'))

class Suscripcion(models.Model):
	premium = models.DecimalField(max_digits=11, decimal_places=2, unique=True, default=100)
	basico = models.DecimalField(max_digits=11, decimal_places=2, unique=True, default=50)

	def __str__(self):
		return "Suscripciones"

	class Meta:
		verbose_name_plural = "Precios de Suscripciones"

class Opinion(models.Model):
	semana = models.OneToOneField(
		'SemanaPasada',
		on_delete=models.CASCADE,
		related_name='opinion'
		)
	puntaje = models.IntegerField(default=10,validators=[MaxValueValidator(10), MinValueValidator(1)])
	descripcion = models.TextField(default="",max_length=1000)
