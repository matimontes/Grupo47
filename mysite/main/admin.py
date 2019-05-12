from django.contrib import admin
from .models import Residencia, Subasta, HotSale, Imagen
from django import forms
from datetime import timedelta
# Register your models here.

#class ResidenciaAdmin(admin.ModelAdmin):
#	fields = ["nombre",
#				"tutorial_published",
#				"tutorial_content"]
class ImagenInline(admin.TabularInline):
	model = Imagen
	extra = 0
	verbose_name_plural = 'imágenes'

class SubastaAdminForm(forms.ModelForm):
	"""
	Esta clase Form contiene la verificación de la creación de Subastas
	"""

	def clean(self):
		cleaned_data = super().clean()
		dia_inicial_cleaned = cleaned_data["dia_inicial"]
		residencia_cleaned = cleaned_data["residencia"]
		inicio_de_subasta_cleaned = self.cleaned_data["inicio_de_subasta"]
		#Verifica que no coincida con ninguna semana de Subastas
		for semana in residencia_cleaned.subastas.all():
			if semana.coincide(dia_inicial_cleaned):
				if not (semana == cleaned_data["id"]):
					self.add_error('dia_inicial',"La semana solicitada coincide con la Subasta de: "+ semana.dia_inicial.isoformat()+ " a "+ semana.dia_final().isoformat())
		#Verifica que no coincida con ninguna semana de HotSale
		for semana in residencia_cleaned.hotsales.all():
			if semana.coincide(dia_inicial_cleaned):
				if not (semana == cleaned_data["id"]):
					self.add_error('dia_inicial',"La semana solicitada coincide con el HotSale de: "+ semana.dia_inicial.isoformat()+ " a "+ semana.dia_final().isoformat())
		#Verifica que la subasta comience al menos 4 días antes del día inicial dela semana
		if (inicio_de_subasta_cleaned >= (dia_inicial_cleaned - timedelta(days=3))):
			self.add_error('inicio_de_subasta',"La subasta debe comenzar al menos 4 días antes que el día inicial de la semana.")

class SubastaAdmin(admin.ModelAdmin):
	form = SubastaAdminForm
	fields = ["residencia","precio_reserva","precio_inicial","dia_inicial","inicio_de_subasta"]

class SubastaInLine(admin.TabularInline):
	model = Subasta
	form = SubastaAdminForm
	extra = 0
	fields = ["precio_reserva","precio_inicial","dia_inicial","inicio_de_subasta"]

class HotSaleInLine(admin.TabularInline):
	model = HotSale
	extra = 0
	fields = ["precio_reserva","dia_inicial"]

class ResidenciaAdmin(admin.ModelAdmin):
	inlines = [
		ImagenInline, SubastaInLine, HotSaleInLine,
	]


admin.site.register(Residencia,ResidenciaAdmin)
admin.site.register(Subasta,SubastaAdmin)
admin.site.register(HotSale)