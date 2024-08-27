from django.urls import path
from . import views

urlpatterns = [
    path('', views.LibrarianLoginView.as_view(), name='LibrarianLoginView'),
    path('logout',views.LibrarianLogoutView.as_view(),name='LibrarianLogoutView'),
    path('books',views.BookView.as_view(),name='BookView'),
    path('add_book_category',views.Add_Book_Category.as_view(),name='AddBookCategory'),
    path('add_book',views.Add_Book.as_view(),name="AddBook"),
    path("book_count",views.BookCountByCategoryView.as_view(), name="BookCount"),
    path("delete_book",views.DeleteBook.as_view(),name="BookDelete"),
    path('issue_request',views.IssueRequests.as_view(),name="BookIssueRequest"),
    path('approve_issue_request',views.ApproveIssueRequest.as_view(),name="BookIssueApprove"),
    path('approve_return_request',views.ApproveReturnRequest.as_view(),name="Approve Return Request"),
    path('delete_issue_record',views.DeleteIssueRecord.as_view(),name = "Delete Record")
    # Add more paths for your app's views
]



#Login
#Logout


# Add Category 
# Add Books 


# List All Categories 
# List All Books with Delete Button 





# List all Book Issue request 
# Approve the book issue request


# List All Book Return request
# Approve the book return request 





