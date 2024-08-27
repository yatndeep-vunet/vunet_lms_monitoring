from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet , UserViewSet , LibrarianViewSet , Book_Category_Viewset , UserGetBookView

router = DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'users', UserViewSet, basename='user')
router.register(r'librarian',LibrarianViewSet,basename='Librarian')
router.register(r'books_category',Book_Category_Viewset, basename='books_category')
router.register(r'book_issue',UserGetBookView,basename='book_issue')

urlpatterns = [
    path('', include(router.urls)),
]


