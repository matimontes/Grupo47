from django.contrib import admin
from .models import Residencia, Subasta, HotSale
# Register your models here.

#class ResidenciaAdmin(admin.ModelAdmin):
#	fields = ["nombre",
#				"tutorial_published",
#				"tutorial_content"]



admin.site.register(Residencia)
admin.site.register(Subasta)
admin.site.register(HotSale)