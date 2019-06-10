from django import forms
from django.contrib.auth.forms import UserCreationForm
from main.models import User

class MontoPujaForm(forms.Form):
    monto = forms.DecimalField(label="Monto a pujar")

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
