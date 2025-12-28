from django.contrib.auth.views import LoginView


class Login(LoginView):
	"""
	Вход на сайт
	"""
	template_name = "login.html"
	#form_class = LoginForm
	succes_url = 'menu'

	def get_succes_url(self):
		return self.succes_url