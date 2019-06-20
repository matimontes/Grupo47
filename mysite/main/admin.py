from django.contrib import admin
from .models import Residencia, Subasta, HotSale, Imagen, SemanaReservada, Puja, Suscripcion, SemanaEnEspera
from django import forms
from django.db.models.query import EmptyQuerySet
from datetime import timedelta
from .filters import MesInicioListFilter, InicialDelNombreListFilter, TipoDeUsuarioListFilter
# Register your models here.

def iniciar_subasta(modeladmin, request, queryset):
	for subasta in queryset:
		if subasta.cantidad_de_inscriptos() == 0:
			modeladmin.message_user(request, "La Subasta: %s no tenía inscriptos, por lo que fue convertida en Semana en espera." % subasta.__str__())
		else:
			modeladmin.message_user(request, "La Subasta: %s inició con éxito." % subasta.__str__())
		subasta.forzar_comienzo()
iniciar_subasta.short_description = "Iniciar Subastas Seleccionada/s"

def finalizar_subasta(modeladmin, request, queryset):
	for subasta in queryset:
		if subasta.forzar_fin():
			modeladmin.message_user(request, "La Subasta: %s finalizó con éxito." % subasta.__str__())
		else:
			modeladmin.message_user(request,  "La Subasta: %s no finalizó, ya que no está inicializada." % subasta.__str__(),'error')
finalizar_subasta.short_description = "Finalizar Subastas Seleccionada/s"

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
		#Verifica que no coincida con ninguna semana Reservada
		for semana in residencia_cleaned.semanas_reservadas.all():
			if semana.coincide(dia_inicial_cleaned):
				self.add_error("dia_inicial","La semana solicitada coincide con la Semana Reservada de: "+ semana.dia_inicial.isoformat()+ " a "+ semana.dia_final().isoformat())
				disponible = False
				break
		#Verifica que no coincida con ninguna semana de Subastas
		if disponible:
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
					disponible = False
					break
		#Verifica que no coincida con ninguna semana de Semana en Espera
		if disponible:
			for semana in residencia_cleaned.semanas_en_espera.all():
				if semana.coincide(dia_inicial_cleaned):
					self.add_error('dia_inicial',"La semana solicitada coincide con la Semana en Espera de: "+ semana.dia_inicial.isoformat()+ " a "+ semana.dia_final().isoformat())
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
	actions = [iniciar_subasta,finalizar_subasta]

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

class SemanaReservadaView(admin.TabularInline):
	"""
		Clase Inline de SemanaReservada.
	"""

	model = SemanaReservada
	readonly_fields = ['usuario','dia_inicial','precio_reserva']
	verbose_name_plural = "Semanas reservadas"
	max_num = 0
	can_delete = False
	show_change_link = True

class SemanaReservadaAdmin(admin.ModelAdmin):
	list_filter = ('residencia', MesInicioListFilter,)
	search_fields = ('residencia',)
	list_display = ('residencia','dia_inicial','dia_final','precio_reserva','usuario')
	list_per_page = 30

	def has_add_permission(self, request):
		return False

	def has_change_permission(self, request, obj=None):
		return False

class SemanaEnEperaAdmin(admin.ModelAdmin):
	list_filter = ('residencia', MesInicioListFilter,)
	search_fields = ('residencia',)
	list_display = ('residencia','dia_inicial','dia_final','precio_reserva')
	list_per_page = 30

	def has_add_permission(self, request):
		return False

	def has_change_permission(self, request, obj=None):
		return False

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
	list_filter = ('ciudad','pais','personas',)
	search_fields = ('nombre', 'dirección',)
	ordering = ('nombre','dirección','ciudad','pais',)
	inlines = [
		SemanaReservadaView, SubastaAdminView, HotSaleAdminView, SubastaInLine, HotSaleInLine, ImagenInline,
	]
	list_display = ('nombre','ciudad','pais','dirección','personas')
	list_per_page = 30

class SuscripcionAdmin(admin.ModelAdmin):
	def has_delete_permission(self, *args):
		return False

	def has_add_permission(self, request): #Deniega la posibilidad de añadir rows si ya hay una
		return self.model.objects.count() < 1

from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import User

class UserCreationForm(forms.ModelForm):
	"""A form for creating new users. Includes all the required
	fields, plus a repeated password."""
	password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
	password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

	class Meta:
		model = User
		fields = ('email', 'date_of_birth')

	def clean_password2(self):
		# Check that the two password entries match
		password1 = self.cleaned_data.get("password1")
		password2 = self.cleaned_data.get("password2")
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("Passwords don't match")
		return password2

	def save(self, commit=True):
		# Save the provided password in hashed format
		user = super().save(commit=False)
		user.set_password(self.cleaned_data["password1"])
		if commit:
			user.save()
		return user

class UserChangeForm(forms.ModelForm):
	"""A form for updating users. Includes all the fields on
	the user, but replaces the password field with admin's
	password hash display field.
	"""
	password = ReadOnlyPasswordHashField()

	class Meta:
		model = User
		fields = ('email', 'password', 'date_of_birth', 'is_active', 'is_staff')

	def clean_password(self):
		# Regardless of what the user provides, return the initial value.
		# This is done here, rather than on the field, because the
		# field does not have access to the initial value
		return self.initial["password"]


class UserAdmin(BaseUserAdmin):
	# The forms to add and change user instances
	form = UserChangeForm
	add_form = UserCreationForm

	# The fields to be used in displaying the User model.
	# These override the definitions on the base UserAdmin
	# that reference specific fields on auth.User.
	list_display = ('first_name','last_name','email','date_joined')
	list_display_links = ('email',)
	list_filter = (TipoDeUsuarioListFilter,InicialDelNombreListFilter,'date_of_birth')
	fieldsets = (
		(None, {'fields': ('email', 'password','user_type','creditos')}),
		('Información personal', {'fields': ('first_name','last_name','date_of_birth','nacionalidad')}),
		('Método de pago',{'fields':('metodo_de_pago',)})
	)
	readonly_fields = ('premium',)
	# add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
	# overrides get_fieldsets to use this attribute when creating a user.
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('email', 'date_of_birth', 'password1', 'password2')}
		),
	)
	search_fields = ('email',)
	ordering = ('-date_joined',)
	filter_horizontal = ()

	def has_change_permission(self, request, obj=None):
		return False

# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)

admin.site.index_template = 'admin/mysite/index.html'
admin.site.site_header = 'Administración de HSH'
admin.site.site_title = 'Administración de HSH'
admin.site.register(SemanaReservada,SemanaReservadaAdmin)
admin.site.register(Residencia,ResidenciaAdmin)
admin.site.register(Subasta,SubastaAdmin)
admin.site.register(HotSale,HotSaleAdmin)
admin.site.register(Puja)
admin.site.register(SemanaEnEspera,SemanaEnEperaAdmin)
admin.site.register(Suscripcion, SuscripcionAdmin)
