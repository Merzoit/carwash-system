from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
	"""
	Форма авторизации
	"""
	model = None  # Используем встроенную модель User
	fields = ("username", "password")

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["username"].widget.attrs["class"] = "form-control"
		self.fields["password"].widget.attrs["class"] = "form-control"
