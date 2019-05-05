from django.db import models
from datetime import date

# Create your models here.
class Residencia(models.Model):
	nombre = models.CharField(max_length=50)
	dirección = models.CharField(max_length=200)
	#fotos = SE IMPLEMENTA EN CLASE IMAGEN
	descripcion = models.TextField()
	habitaciones = models.IntegerField(default=0)
	personas = models.IntegerField(default=0)
	baños = models.IntegerField(default=0)
	#subastas = SE IMPLEMENTA EN SUBASTA
	#hotsales = SE IMPLEMENTA EN HOTSALE
	
	def __str__(self):
		return self.nombre

class Semana(models.Model):
	dia_inicial = models.DateField()
	dia_final = models.DateField()
	precio_reserva = models.FloatField()

	class Meta:
		abstract = True

class Subasta(Semana):
	precio_inicial = models.FloatField()
	residencia = models.ForeignKey('Residencia',on_delete=models.CASCADE,related_name='subastas')

class HotSale(Semana):
	residencia = models.ForeignKey('Residencia',on_delete=models.CASCADE,related_name='hotsales')