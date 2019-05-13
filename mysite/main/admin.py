from django.contrib import admin
from .models import Residencia, Subasta, HotSale, Imagen
from django import forms
from django.db.models.query import EmptyQuerySet
from datetime import timedelta
# Register your models here.

class SemanasAdminInlineFormSet(forms.BaseInlineFormSet):
	
	def coincide(self, dia_inicial_1, dia_inicial_2):
		return ((dia_inicial_1 > (dia_inicial_2 - timedelta(days=7))) and (dia_inicial_1 < (dia_inicial_2 + timedelta(days=7)) ) )

	def clean(self):
		super().clean()
		for form in self.forms:
			dia_inicial_1 = form.cleaned_data["dia_inicial"]
			for formCheck in self.forms:
				dia_inicial_2 = formCheck.cleaned_data["dia_inicial"]
				if form != formCheck:
					if self.coincide(dia_inicial_1,dia_inicial_2):
						form.add_error('dia_inicial',"La semana solicitada coincide con la HotSale ingresada a iniciar: "+ dia_inicial_2.isoformat())
						formCheck.cleaned_data["dia_inicial"] = dia_inicial_2
						break
				formCheck.cleaned_data["dia_inicial"] = dia_inicial_2
			form.cleaned_data["dia_inicial"] = dia_inicial_1

	def get_queryset(self):
		query = super().get_queryset()
		return self.model.objects.none()

class SemanaAdminForm(forms.ModelForm):

	def clean(self):
		cleaned_data = super().clean()
		dia_inicial_cleaned = cleaned_data["dia_inicial"]
		residencia_cleaned = cleaned_data["residencia"]
		disponible = True
		#Verifica que no coincida con ninguna semana de Subastas
		for semana in residencia_cleaned.subastas.all():
			if semana.coincide(dia_inicial_cleaned):
				self.add_error("dia_inicial","La semana solicitada coincide con la Subasta de: "+ semana.dia_inicial.isoformat()+ " a "+ semana.dia_final().isoformat())
				disponible = False
				break
		#Verifica que no coincida con ninguna semana de HotSale
		if disponible:
			for semana in residencia_cleaned.hotsales.all():
				if semana.coincide(dia_inicial_cleaned):
					self.add_error('dia_inicial',"La semana solicitada coincide con la HotSale de: "+ semana.dia_inicial.isoformat()+ " a "+ semana.dia_final().isoformat())
					break
		cleaned_data["dia_inicial"] = dia_inicial_cleaned
		cleaned_data["residencia"] = residencia_cleaned
		return cleaned_data

class ImagenInline(admin.TabularInline):
	model = Imagen
	extra = 0
	verbose_name_plural = 'imágenes'

class SubastaAdminForm(SemanaAdminForm):
	"""
	Esta clase Form contiene la verificación de la creación de Subastas
	"""

	def clean(self):
		cleaned_data = super().clean()
		inicio_de_subasta_cleaned = cleaned_data["inicio_de_subasta"]
		dia_inicial_cleaned = cleaned_data["dia_inicial"]
		#Verifica que la subasta comience al menos 4 días antes del día inicial dela semana
		if (inicio_de_subasta_cleaned >= (dia_inicial_cleaned - timedelta(days=3))):
			self.add_error('inicio_de_subasta',"La subasta debe comenzar al menos 4 días antes que el día inicial de la semana.")

class SubastaAdmin(admin.ModelAdmin):
	form = SubastaAdminForm
	fields = ["residencia","precio_reserva","precio_inicial","dia_inicial","inicio_de_subasta"]

class SubastaInLine(admin.TabularInline):
	model = Subasta
	form = SubastaAdminForm
	formset = SemanasAdminInlineFormSet
	extra = 0
	fields = ["precio_reserva","precio_inicial","dia_inicial","inicio_de_subasta"]

class HotSaleAdminForm(SemanaAdminForm):
	"""
	Esta clase Form contiene la verificación de la creación de HotSales
	"""

	def clean(self):
		cleaned_data = super().clean()

class HotSaleAdmin(admin.ModelAdmin):
	fields = ["residencia","precio_reserva","dia_inicial"]

class HotSaleInLine(admin.TabularInline):
	model = HotSale
	form = HotSaleAdminForm
	formset = SemanasAdminInlineFormSet
	extra = 0
	fields = ["precio_reserva","dia_inicial"]

class SubastaAdminView(admin.TabularInline):
	model = Subasta
	readonly_fields = ['dia_inicial','precio_reserva','precio_inicial','inicio_de_subasta']
	verbose_name_plural = "Subastas cargadas"
	max_num = 0

class HotSaleAdminView(admin.TabularInline):
	model = HotSale
	readonly_fields = ['dia_inicial','precio_reserva']
	verbose_name_plural = "HotSales cargados"
	max_num = 0

class ResidenciaAdmin(admin.ModelAdmin):
	inlines = [
		SubastaAdminView, HotSaleAdminView, ImagenInline, SubastaInLine, HotSaleInLine,
	]


admin.site.register(Residencia,ResidenciaAdmin)
admin.site.register(Subasta,SubastaAdmin)
admin.site.register(HotSale,HotSaleAdmin)