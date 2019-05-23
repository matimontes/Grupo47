from datetime import date
from django.contrib import admin

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