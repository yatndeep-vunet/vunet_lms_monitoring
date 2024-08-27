# user_app/mixins.py

from django.shortcuts import redirect

class LoginRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.session.get('librarian_id') is None:
            return redirect('/librarian/')
        return super().dispatch(request, *args, **kwargs)

class LogoutRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.session.get('librarian_id') is not None:
            return redirect('/librarian/books')
        return super().dispatch(request, *args, **kwargs)