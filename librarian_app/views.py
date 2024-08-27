# core_app/views.py
from django.shortcuts import render, redirect , get_object_or_404
from django.views import View
from core_app.models import User , Librarian , Book_Issue_Record , BookName , Books_Category
from django.middleware.csrf import get_token
from django.contrib.sessions.models import Session
from django.contrib.sessions.models import Session
from django.http import JsonResponse
from django.core.paginator import Paginator
from datetime import datetime, date, time, timedelta



from librarian_app.mixins import LoginRequiredMixin , LogoutRequiredMixin

    
class LibrarianLoginView(LogoutRequiredMixin,View):
    def get(self, request):
        csrf_token = get_token(request) 
        return render(request, 'librarian/login.html', {'csrf_token': csrf_token})
    
    def post(self, request):
        librarian_id = request.POST.get('librarian_id')
        password = request.POST.get('password')

        librarians = Librarian.objects.all()

        for librarian in librarians:
            if librarian.librarian_id == librarian_id:
                if librarian.password == password:
                    request.session['librarian_id'] = librarian.librarian_id  # Store librarian ID in session
                    request.session.save()

                    context = {
                        "message":"Successfully Logged In",
                        "status":200
                    }
                    return render(request, 'librarian/login.html', context)

                else:
                    context = {
                        "message":"Invalid Password",
                        "status":400
                    }
                    return render(request, 'librarian/login.html',context)
            else:
                context = {
                        "message":"Invalid Credentials",
                        "status":400
                    }
                return render(request, 'librarian/login.html', context)



class LibrarianHomeView(LoginRequiredMixin,View):
    def get(self,request):
        return render(request,'librarian/home.html')




class LibrarianLogoutView(LoginRequiredMixin,View):
    def get(self,request):           
        # Clear session key
        request.session.pop('librarian_id', None)
        return render(request,'librarian/login.html')




# Adding Book Categories 

class BookView(LoginRequiredMixin, View):
    def get(self, request):
        # CSRF token for form submissions
        csrf_token = get_token(request)

        # Fetch book categories
        book_categories = Books_Category.objects.all()

        # Fetch and sort books
        sort_by = request.GET.get('sort_by', 'book_name')  # Default sort by 'book_name'
        order = request.GET.get('order', 'asc')
        
        if order == 'desc':
            sort_by = f'-{sort_by}'  # Add '-' prefix for descending order

        books = BookName.objects.all().order_by(sort_by)

        # Pagination
        paginator = Paginator(books, 10)  # Show 10 books per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj,
            'sort_by': sort_by.strip('-'),  # Send sorting information back to the template
            'order': order,
            'book_categories': book_categories,
            'csrf_token': csrf_token,
        }

        return render(request, 'librarian/books.html', context)
    

class Add_Book_Category(LoginRequiredMixin,View):
    def post(self, request):
        book_category = request.POST.get('book_category')
        
        # Check if the book category already exists
        if Books_Category.objects.filter(book_category=book_category).exists():
            return JsonResponse({'message': 'Book Category Already Exists'})
        
        # If not, save the new category
        book_ctg = Books_Category(
            book_category=book_category
        )
        book_ctg.save()
        return JsonResponse({'message': 'Book Category Added Successfully'})

# book_name 
# book_author_name 


# Add Books 

class Add_Book(LoginRequiredMixin,View):
    def post(self, request):
        book_name = request.POST.get('book_name')
        book_author_name = request.POST.get('book_author_name')
        book_category_id = request.POST.get('book_category_id')

        # Retrieve the Books_Category instance
        try:
            book_category = Books_Category.objects.get(book_category_id=book_category_id)
        except Books_Category.DoesNotExist:
            return JsonResponse({'message': 'Invalid book category'})

        # Check if a book with the same name and author already exists
        if BookName.objects.filter(book_name=book_name, book_author_name=book_author_name).exists():
            return JsonResponse({'message': 'Book with the same author already exists'})

        # If the book doesn't exist, add the new book
        new_book = BookName(
            book_name=book_name,
            book_author_name=book_author_name,
            book_category_id = book_category  # Assign the Books_Category instance
        )
        new_book.save()
        return JsonResponse({'message': 'Book Added Successfully'})
    

class BookCountByCategoryView(LoginRequiredMixin,View):
    def post(self, request):
        try:
            # Retrieve the category instance
            category_id = request.POST.get('book_category_id')
            category = Books_Category.objects.get(book_category_id=category_id)
        except Books_Category.DoesNotExist:
            return JsonResponse({'message': 'Category not found'}, status=404)

        # Count the number of books associated with the category
        book_count = BookName.objects.filter(book_category_id=category_id).count()
        print(book_count)
        
        return JsonResponse({'category': category.book_category, 'book_count': book_count})
    


# Delete Book

class DeleteBook(LoginRequiredMixin,View):
    def post(self,request):
        try:
            # Retrieve the book by its ID
            book_id = request.POST.get('book_id')
            book = BookName.objects.get(book_id=book_id)
            # Delete the book
            book.delete()
            return JsonResponse({'message': 'Book deleted successfully'}, status=200)
        except BookName.DoesNotExist:
            return JsonResponse({'message': 'Book not found'}, status=404)
        

# Check Issue Requests 
class IssueRequests(LoginRequiredMixin,View):
    def get(self, request):
        csrf_token = get_token(request)
        book_requests = Book_Issue_Record.objects.all()
        context = {
            'csrf_token': csrf_token,
            'book_issue_request_record': book_requests
        }
        return render(request, 'librarian/issue_request_record.html',context)
    
# Approve Issue 

class ApproveIssueRequest(LoginRequiredMixin,View):
    def post(self,request):
        
        book_issue_id = request.POST.get('book_issue_id')
        issue_record = get_object_or_404(Book_Issue_Record, book_issue_id=book_issue_id)
        issue_record.is_issue_approve = True 
        issue_record.issue_date = date.today().strftime("%Y-%m-%d")

        issue_record.save()

        return JsonResponse({'message':'Issue Request Approved'})

# Approve Return 

class ApproveReturnRequest(LoginRequiredMixin,View):
    def post(self,request):
        book_issue_id = request.POST.get('book_issue_id')
        issue_record = get_object_or_404(Book_Issue_Record,book_issue_id=book_issue_id)

        issue_record.is_return_approve = True
        issue_record.return_date = date.today().strftime("%Y-%m-%d")

        issue_record.save()

        return JsonResponse({'message':'Return Request Approved'})

class DeleteIssueRecord(LoginRequiredMixin,View):
    def post(self,request):
        book_issue_id = request.POST.get('book_issue_id')
        issue_record = get_object_or_404(Book_Issue_Record,book_issue_id = book_issue_id)
        issue_record.delete()
        return JsonResponse({'message':"Issue Record Deleted"})
    
