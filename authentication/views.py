from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse


class Login(LoginView):
	"""
	Вход на сайт
	"""
	template_name = "login.html"
	#form_class = LoginForm
	success_url = 'menu'

	def get_success_url(self):
		return self.success_url

	def dispatch(self, request, *args, **kwargs):
		"""
		Перенаправляем авторизованного пользователя на главную страницу
		"""
		if request.user.is_authenticated:
			return redirect(reverse('menu'))
		return super().dispatch(request, *args, **kwargs)