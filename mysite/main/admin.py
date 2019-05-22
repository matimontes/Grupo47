from django.contrib import admin
from .models import Residencia, Subasta, HotSale, Imagen
from django import forms
from django.db.models.query import EmptyQuerySet
from datetime import timedelta
from .filters import MesInicioListFilter
# Register your models here.

def iniciar_subasta(modeladmin, request, queryset):
    for subasta in queryset:
    	subasta.forzar_comienzo()
iniciar_subasta.short_description = "Iniciar Subastas Seleccionada/s"

class SemanasAdminInlineFormSet(forms.BaseInlineFormSet):
	
	def coincide(self, dia_inicial_1, dia_inicial_2):
		"""
			Devuelve True si las semanas se superponen.
		"""
		return ((dia_inicial_1 > (dia_inicial_2 - timedelta(days=7))) and (dia_inicial_1 < (dia_inicial_2 + timedelta(days=7)) ) )

	def clean(self):
		"""
			Validación del FormSet de Semanas.
			Compara cada Form en el FormSet entre sí para detectar errores.
		"""
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
		"""
			Devuelve un QuerySet vacío del Model
		"""
		return self.model.objects.none()

class SemanaAdminForm(forms.ModelForm):

	def clean(self):
		"""
			Validación de Form Semana.
		"""
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
	"""
		Clase Inline de Imagenes
	"""
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
	"""
		Clase ModelAdmin de Subasta.
		Utiliza SubastaAdminForm como form.
		Tiene filtros por residencia y por fecha (MesInicioListFilter).
		La búsqueda se realiza por residencia.
	"""
	form = SubastaAdminForm
	fields = ["residencia","precio_reserva","precio_inicial","dia_inicial","inicio_de_subasta"]
	list_filter = ('residencia', MesInicioListFilter,)
	search_fields = ('residencia',)
	list_display = ('residencia','dia_inicial','dia_final','inicio_de_subasta','iniciada','precio_reserva','precio_inicial')
	list_editable = ('precio_reserva','precio_inicial')
	list_per_page = 30
	actions = [iniciar_subasta]

class SubastaInLine(admin.TabularInline):
	"""
		Clase Inline de Subastas.
		Utiliza la clase SubastaAdminForm como form y SemanasAdminInlineFormSet como formset.
	"""
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
	"""
		Clase ModelAdmin de HotSale.
		Utiliza HotSaleAdminForm como form.
		Tiene filtros por residencia y por fecha (MesInicioListFilter).
		La búsqueda se realiza por residencia.
	"""
	form = HotSaleAdminForm
	fields = ["residencia","precio_reserva","dia_inicial"]
	list_filter = ('residencia', MesInicioListFilter,)
	search_fields = ('residencia',)
	list_display = ('residencia','dia_inicial','dia_final','precio_reserva')
	list_editable = ('precio_reserva',)
	list_per_page = 30

class HotSaleInLine(admin.TabularInline):
	"""
		Clase Inline de HotSales.
		Utiliza la clase HotSaleAdminForm como form y SemanasAdminInlineFormSet como formset.
	"""
	model = HotSale
	form = HotSaleAdminForm
	formset = SemanasAdminInlineFormSet
	extra = 0
	fields = ["precio_reserva","dia_inicial"]

class SubastaAdminView(admin.TabularInline):
	"""
		Clase Inline de subastas ya creadas.
	"""
	model = Subasta
	readonly_fields = ['dia_inicial','precio_reserva','precio_inicial','inicio_de_subasta']
	exclude = ['usuarios_inscriptos']
	verbose_name_plural = "Subastas cargadas"
	max_num = 0
	show_change_link = True

class HotSaleAdminView(admin.TabularInline):
	"""
		Clase Inline de HotSales ya creados.
	"""
	model = HotSale
	readonly_fields = ['dia_inicial','precio_reserva']
	verbose_name_plural = "HotSales cargados"
	max_num = 0
	show_change_link = True

class ResidenciaAdmin(admin.ModelAdmin):
	"""
		Clase ModelAdmin de Residencia.
		Usa form default.
		Contiene inlines: 
			SubastaAdminView
			HotSaleAdminView
			SubastaInLine
			HotSaleInLine
			ImagenInline
		Están ordenadas por (en orden de prioridad):
			nombre
			dirección
			ciudad
			pais
		Tiene filtros  por:
			ciudad
			pais
			personas
			baños
		La búsqueda serealiza por nombre o dirección.
	"""
	list_filter = ('ciudad','pais','personas','baños',)
	search_fields = ('nombre', 'dirección',)
	ordering = ('nombre','dirección','ciudad','pais',)
	inlines = [
		SubastaAdminView, HotSaleAdminView, SubastaInLine, HotSaleInLine, ImagenInline,
	]
	list_display = ('nombre','ciudad','pais','dirección','personas')
	list_per_page = 30

admin.site.index_template = 'admin/mysite/index.html'
admin.site.site_header = 'Administración de HSH'
admin.site.register(Residencia,ResidenciaAdmin)
admin.site.register(Subasta,SubastaAdmin)
admin.site.register(HotSale,HotSaleAdmin)