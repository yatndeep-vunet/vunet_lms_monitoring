# user_app/mixins.py

from django.shortcuts import redirect

class LoginRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.session.get('user_id') is None:
            return redirect('/users/login/')
        return super().dispatch(request, *args, **kwargs)

class LogoutRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.session.get('user_id') is not None:
            return redirect('/users/home/')
        return super().dispatch(request, *args, **kwargs)