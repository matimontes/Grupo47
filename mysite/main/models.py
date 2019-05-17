from django.db import models
from datetime import date, timedelta

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
	precio_reserva = models.FloatField()

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
	precio_inicial = models.FloatField()
	inicio_de_subasta = models.DateField()
	residencia = models.ForeignKey('Residencia',on_delete=models.CASCADE,related_name='subastas')

class HotSale(Semana):
	residencia = models.ForeignKey('Residencia',on_delete=models.CASCADE,related_name='hotsales')

class Imagen(models.Model):
	residencia = models.ForeignKey(Residencia,on_delete=models.CASCADE,related_name='imagenes')
	imagen = models.ImageField(upload_to=('fotos/'))

class Usuario(models.Model):
	codigo = models.IntegerField()
	nombre = models.CharField(max_length=50)
	apellido = models.CharField(max_length=50)
	nacionalidad = models.CharField(max_length=50)
	email = models.CharField(max_length=50)
	creditos = models.IntegerField(default=2)

	def NombreCompleto(self):
		cadena = "{1} {2}"
		return cadena.format(self.nombre, self.apellido)

	def __str__(self):
		return self.NombreCompleto()

class Tarjeta(models.Model): #Falta completar
	__numero = models.IntegerField(max_length = 16)
	__codigo = models.IntegerField(max_length = 3)

	def GetNumero(self):
		return self __numero

	def GetCodigo(self):
		return self __codigo

	#def Pagar(self):
	#def Validar(self):
	#	return True