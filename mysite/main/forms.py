from django import forms
from django.contrib.auth.forms import UserCreationForm
from main.models import User

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

class RegistrationForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = (
			"email",
			"first_name",
			"last_name",
			"date_of_birth",
			"password1",
			"password2"
		)

	def save(self, commit=True):
		user = super(RegistrationForm, self).save(commit=False)
		user.first_name = self.cleaned_data['first_name']
		user.last_name = self.cleaned_data['last_name']
		user.email = self.cleaned_data['email']

		if commit:
			user.save()

		return user
