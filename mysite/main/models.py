from django.db import models
from datetime import date, timedelta
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
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

class Semana(models.Model):
	dia_inicial = models.DateField()
	precio_reserva = models.DecimalField(max_digits=11,decimal_places=2)

	def __str__(self):
		return self.residencia.nombre + " - De: " + self.dia_inicial.isoformat() + " a: " + self.dia_final().isoformat()

	def dia_final(self):
		return self.dia_inicial + timedelta(days=7)

	def coincide(self,fecha):
		return ((fecha > self.dia_inicial - timedelta(days=7)) and (fecha < self.dia_final()))

	class Meta:
		abstract = True
		ordering = ['dia_inicial', 'residencia']

class Subasta(Semana):
	precio_inicial = models.DecimalField(max_digits=11,decimal_places=2)
	inicio_de_subasta = models.DateField()
	residencia = models.ForeignKey('Residencia',on_delete=models.CASCADE,related_name='subastas')
	usuarios_inscriptos = models.ManyToManyField('Usuario',related_name='inscripciones')
	iniciada = False
	#pujas CREADAS DESDE CLASE PUJA

	def fin_de_subasta(self):
		return (self.inicio_de_subasta + timedelta(days=3))

	def puja_actual(self):
		return self.pujas.first()

	def pujar(self,usuario_pujador,dinero_a_pujar):
		if dinero_pujado > self.puja_actual().dinero_pujado + 100:
			Puja.objects.create(usuario=usuario_pujador,dinero_pujado=dinero_a_pujar,subasta=self)
		else:
			#AGREGAR FUNCIONALIDAD
			pass

	def cancelar_puja(self,usuario):
		puja = self.puja_actual()
		if puja.usuario == usuario:
			puja.delete()
		else:
			#AGREGAR FUNCIONALIDAD
			pass

	def abandonar_subasta(self,usuario):
		pass

	def agregar_usuario(self,usuario):
		pass

	def esta_inscripto(self,usuario):
		return usuario in self.usuarios_inscriptos

	def comenzar(self):
		self.iniciada = True
		Puja.objects.create(usuario=None,dinero_pujado=self.precio_inicial,subasta=self)
		self.notificar_inscriptos()

	def finalizar(self):
		puja = self.puja_actual()
		SemanaReservada.objects.create(usuario=puja.usuario,
			precio_reserva=self.puja.dinero_pujado,
			residencia=self.residencia,
			dia_inicial=self.dia_inicial)
	#FALTA BORRARSE A SÍ MISMO AFUERA DEL FINALIZAR

	def forzar_comienzo(self):
		self.comenzar
		self.inicio_de_subasta = datetime.today()

	def forzar_fin(self):
		self.finalizar

	def notificar_inscriptos(self):
		for usuario in self.usuarios_inscriptos:
			usuario.notificar_comienzo_subasta(self)

class HotSale(Semana):
	residencia = models.ForeignKey('Residencia',on_delete=models.CASCADE,related_name='hotsales')

class SemanaReservada(Semana):
	usuario = models.ForeignKey('Usuario',on_delete=models.CASCADE,related_name='semanas_reservadas')
	residencia = models.ForeignKey('Residencia',on_delete=models.CASCADE,related_name='semanas_reservadas')

class Puja(models.Model):
	usuario = models.ForeignKey('Usuario',on_delete=models.CASCADE,related_name='pujas')
	dinero_pujado = models.DecimalField(max_digits=11,decimal_places=2)
	subasta = models.ForeignKey('Subasta',on_delete=models.CASCADE,related_name='pujas')

	class Meta:
		ordering = ['subasta','-dinero_pujado']

class Imagen(models.Model):
	residencia = models.ForeignKey(Residencia,on_delete=models.CASCADE,related_name='imagenes')
	imagen = models.ImageField(upload_to=('fotos/'))

class Usuario(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	codigo = models.IntegerField(default=0)
	nacionalidad = models.CharField(max_length=50)
	creditos = models.IntegerField(default=2)
	#premium = False 

	def __str__(self):
		return self.user.username

	def notificar_comienzo_subasta(self,subasta):
		#AGREGAR FUNCIONALIDAD PARA NOTIFICAR POR MAIL QUE COMENZÓ LA SUBASTA
		pass

#	def invertir_premium(self):
#		if self.premium:
#			self.premium = False
#		else:
#			self.premium = True

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Usuario.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.usuario.save()

# def create_profile(sender, **kwargs):
#     if kwargs['created']:
#         user_profile = Usuario.objects.create(user=kwargs['instance'])

# post_save.connect(create_profile, sender=User)


class Tarjeta(models.Model): #Falta completar
	numero = models.IntegerField()
	codigo = models.IntegerField()

	#def Pagar(self):
	#def Validar(self):
	#	return True
