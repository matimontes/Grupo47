from datetime import date
from django.contrib import admin
from string import ascii_lowercase

class MesInicioListFilter(admin.SimpleListFilter):
	title = 'Mes de inicio de semana'
	parameter_name = 'mes_inicio'

	def lookups(self, request, model_admin):
		qs = model_admin.get_queryset(request)
		for año in (range(2019, 2100)):
			for mes in (range(1, 13)):
				if (qs.filter(dia_inicial__gte=date(año,mes,1),dia_inicial__lt=date((año if mes < 12 else año + 1),(mes + 1 if mes < 12 else 1),1)).exists()):
					yield ((str(año)+' - '+str(mes)),(str(año)+' - '+str(mes)))

	def queryset(self, request, queryset):
		for año in range(2019,2100):
			for mes in range(1,13):
				if self.value() == (str(año)+' - '+str(mes)):
					return queryset.filter(dia_inicial__gte=date(año,mes,1),dia_inicial__lte=date((año if mes < 12 else año + 1),(mes + 1 if mes < 12 else 1),1))

class InicialDelNombreListFilter(admin.SimpleListFilter):
	# Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Nombre'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'inicial_del_nombre'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        qs = model_admin.get_queryset(request)
        for letra in ascii_lowercase:
        	if (qs.filter(first_name__istartswith=letra).exists()):
        		yield (letra,letra)

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        for letra in ascii_lowercase:
        	if self.value() == letra:
        		return queryset.filter(first_name__istartswith=letra)

class TipoDeUsuarioListFilter(admin.SimpleListFilter):
	title = 'Tipo de usuario'
	parameter_name = 'Tipo de usuario'
	def lookups(self, request, model_admin):
		return (
            ('basico', 'Básico'),
            ('premium', 'Premium'),
            ('admin', 'Administrador'),
        )

	def queryset(self, request, queryset):
		if self.value() == 'basico':
			return queryset.filter(premium__exact=False,is_staff__exact=False)
		if self.value() == 'premium':
			return queryset.filter(premium__exact=True,is_staff__exact=False)
		if self.value() == 'admin':
			return queryset.filter(is_staff__exact=True)