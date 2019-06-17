from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from main.models import User
from datetime import date, timedelta

class MontoPujaForm(forms.Form):
    monto = forms.DecimalField(label="Monto a pujar")

    def __init__(self, *args, user, subasta, **kwargs):
        self.user = user
        self.subasta = subasta
        super().__init__(*args, **kwargs)

    def clean(self):
        data = self.cleaned_data
        cleaned_monto = data['monto']
        if (self.subasta.puja_actual().usuario != self.user):
            if (cleaned_monto < self.subasta.puja_actual().dinero_pujado + 50):
                self.add_error('monto','El monto a pujar debe superar al actual por al menos $50.')
            if not(self.user.tiene_creditos()):
                self.add_error('monto','No tienes créditos suficientes para realizar una puja.')
        else:
            raise forms.ValidationError('No puedes pujar cuando tu puja ya está ganando.')
        return data

class BuscarResidenciaForm(forms.Form):
    inicio = forms.CharField()
    fin = forms.CharField()
    pasajeros = forms.IntegerField(required=False)
    pais = forms.CharField(required=False)

class InvertirTipoForm(forms.Form):

    def __init__(self, *args, user, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        data = self.cleaned_data
        if (not self.user.premium) and (not self.user.validar_premium()):
            raise forms.ValidationError('Tu tarjeta no es válida para ser premium.')
        return data

class EditarPerfilForm(forms.ModelForm):

	class Meta:
		model = User
		fields = (
			"email",
			"first_name",
			"last_name",
			"date_of_birth",
			"nacionalidad"
			)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		user_permissions = self.fields.get('user_permissions')
		if user_permissions:
			user_permissions.queryset = user_permissions.queryset.select_related('content_type')

	def clean(self):
		data = super().clean()
		cleaned_fecha = data['date_of_birth']
		today = date.today()
		if (cleaned_fecha.year == today.year - 18):
			if (cleaned_fecha.month == today.month):
				if (cleaned_fecha.day > today.day):
					self.add_error('date_of_birth','Debes ser mayor de 18 años')
			elif (cleaned_fecha.month > today.month):
				self.add_error('date_of_birth','Debes ser mayor de 18 años')
		elif (cleaned_fecha.year > today.year - 18):
			self.add_error('date_of_birth','Debes ser mayor de 18 años')
		return data

class RegistrationForm(UserCreationForm):

	class Meta:
		model = User
		fields = (
			"email",
			"first_name",
			"last_name",
			"date_of_birth",
			"nacionalidad",
			"password1",
			"password2"
		)

	def clean(self):
		data = super().clean()
		cleaned_fecha = data['date_of_birth']
		today = date.today()
		if (cleaned_fecha.year == today.year - 18):
			if (cleaned_fecha.month == today.month):
				if (cleaned_fecha.day > today.day):
					self.add_error('date_of_birth','Debes ser mayor de 18 años')
			elif (cleaned_fecha.month > today.month):
				self.add_error('date_of_birth','Debes ser mayor de 18 años')
		elif (cleaned_fecha.year > today.year - 18):
			self.add_error('date_of_birth','Debes ser mayor de 18 años')
		return data
