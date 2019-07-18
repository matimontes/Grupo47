from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from main.models import User, Tarjeta, Opinion
from datetime import date, timedelta
from creditcards.forms import CardNumberField, CardExpiryField, SecurityCodeField
from django.core.validators import MaxValueValidator, MinValueValidator

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
                self.add_error('monto','El monto a pujar debe superar al actual por al menos $1.')
            if not(self.user.tiene_creditos()):
                self.add_error('monto','No tienes créditos suficientes para realizar una puja.')
        else:
            raise forms.ValidationError('No puedes pujar cuando tu puja ya está ganando.')
        return data

class BuscarResidenciaForm(forms.Form):
    inicio = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'class': 'datepicker'}),
        input_formats=('%d/%m/%Y', )
        )
    fin = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'class': 'datepicker'}),
        input_formats=('%d/%m/%Y', )
        )
    pasajeros = forms.IntegerField(required=False)
    ciudad = forms.CharField(required=False)
    pais = forms.CharField(required=False)

    def clean(self):
        import datetime
        data = self.cleaned_data
        fecha_inicio = data['inicio']
        fecha_fin = data['fin']
        if fecha_fin < fecha_inicio:
            self.add_error('inicio', 'La fecha final debe ser mayor a la fecha inicial')
        else:
            if (fecha_fin - fecha_inicio).days < 8:
                self.add_error('inicio', 'Debe haber al menos 8 días de diferencia entre las fechas.')
            elif (fecha_fin - fecha_inicio).days > 60:
                self.add_error('inicio', 'El rango entre las fechas debe ser menor a 2 meses.')
        return data

class InvertirTipoForm(forms.Form):

    def __init__(self, *args, user, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

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
			"password2",
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

class PaymentForm(forms.ModelForm):
	class Meta:
		model = Tarjeta
		fields = ("cc_number","cc_expiry","cc_code")

class OpinarForm(forms.ModelForm):
	puntaje = forms.IntegerField()

	class Meta:
		model = Opinion
		fields = ("descripcion",)