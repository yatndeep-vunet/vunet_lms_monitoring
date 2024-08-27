from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserRegisterView.as_view(), name='UserRegisterView'),
    path('login/',views.UserLoginView.as_view(),name="LoginView"),
    path('home/',views.UserHomeView.as_view(),name="UserHomeView"),
    path('logout/',views.UserLogoutView.as_view(),name="UserLogoutView"),
    path('verify_mail/',views.UserVerifyMail.as_view(),name="VerifyMail"),
    path('get_book',views.UserBookIssueView.as_view(),name="UserBookIssue"),
    path('issue_record',views.UserListBookIssueRecord.as_view(),name="UserBookIssueRecord"),
    path('delete_book',views.CancelApproveRequest.as_view(),name="Delete Book Request"),
    path('return_request',views.RequestReturn.as_view(),name="Return Request")
    # Add more paths for your app's views

]

#Registration
#Login
#Logout



#List All Books
#List Books by Author Name 
#Get Book by ID
#Request Return Book 
#List Issued Book


'''
HTML Pages for the user 

1. Register Page
2. Login Page
3. Listing of Books
    Request for Issue Book
4. Issue Records 
    Request for Return Book 

'''


