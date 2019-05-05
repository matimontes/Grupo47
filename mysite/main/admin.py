from django.contrib import admin
from .models import Residencia, Subasta, HotSale, Imagen
# Register your models here.

#class ResidenciaAdmin(admin.ModelAdmin):
#	fields = ["nombre",
#				"tutorial_published",
#				"tutorial_content"]
class ImagenInline(admin.TabularInline):
	model = Imagen
	extra = 0
	verbose_name_plural = 'imágenes'

class SubastaAdmin(admin.ModelAdmin):
	fields = ["residencia","precio_reserva","precio_inicial","dia_inicial","inicio_de_subasta"]

class SubastaInLine(admin.TabularInline):
	model = Subasta
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