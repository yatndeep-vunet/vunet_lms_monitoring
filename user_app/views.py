# core_app/views.py
from django.shortcuts import render, redirect , get_object_or_404 
from django.views import View
from core_app.models import User, BookName , Book_Issue_Record , Books_Category
from django.middleware.csrf import get_token
from django.contrib.sessions.models import Session
from django.contrib.sessions.models import Session
from django.core.paginator import Paginator
from django.http import JsonResponse , HttpResponse
import random
from django.core.mail import send_mail
from urllib.parse import urljoin


from user_app.mixins import LoginRequiredMixin , LogoutRequiredMixin


class UserRegisterView(View):
    def get(self, request):
        # Render the registration form template
        csrf_token = get_token(request)  # Get CSRF token
        return render(request, 'user/register.html',{'csrf_token':csrf_token})

    def post(self, request):
        # Handle form submission
        user_name = request.POST.get('user_name')
        password = request.POST.get('password')
        user_mail = request.POST.get('user_mail')
        email_token = random.randint(1000, 9999)

        # Checking that if user already exist 
        users = User.objects.all()
        for user in users :
            if user.user_mail == user_mail:
                context = {
                           "status" : 400,
                           "message" : "User Already Exist"
                        }
                return render(request,'user/register.html',context)
        # Create a new User object
        user = User(
            user_name=user_name,
            password= password,
            user_mail=user_mail,
            email_token = email_token
        )

        user.save()

        host = request.get_host()

        # Get the protocol (http or https)
        protocol = 'https' if request.is_secure() else 'http'

        # Generate a full URL using the host and protocol
        verify_url = f'{protocol}://{host}/users/verify_mail/?id={user.user_id}&email_token={email_token}'

     
        send_mail(
            subject= 'Vu-LMS Verification Mail',  # Subject
            message='',
            html_message= f'Please verify your mail with the given link <a href={verify_url}>Verify</a>',  # Message body
            from_email = 'momentswithdreams@gmail.com',  # From email
            recipient_list = [user_mail],  # To email
            fail_silently=False,
        )
        # Redirect to the login page or any other page after registration
        context = {"status":200 , 'message' : "A verification mail has been sent to your email Id please verify your email Id"}
        return render(request, 'user/register.html', context)
    
class UserVerifyMail(View):
    def get(self,request):
        id = request.GET.get('id')
        email_token = request.GET.get('email_token')
        user = get_object_or_404(User, user_id = id)
        print(email_token , user.email_token ,user.user_id)
        if user.email_token == email_token:
            user.is_email_verfied = True 
            user.email_token = None
            user.save()
            return HttpResponse("Your email has been verified Now you can login")
        else :
             return HttpResponse("Invalid Request")


       

class UserLoginView(LogoutRequiredMixin,View):
    def get(self, request):
        csrf_token = get_token(request) 
        return render(request, 'user/login.html', {'csrf_token': csrf_token})
    
    def post(self, request):
        user_mail = request.POST.get('user_mail')
        password = request.POST.get('password')

        users = User.objects.all()

        for user in users:
            if user.user_mail == user_mail:
                if user.password == password:
                    if user.is_email_verfied == True:
                        request.session['user_id'] = user.user_mail  # Store user ID in session
                        request.session.save()
                        context = {
                            "message" : "Successfully Logged In",
                            "status_code" : 200
                        }
                        return render(request, 'user/login.html',context)
                    else:
                        context = {
                            "message" : "Please verify your mail",
                            "status_code":400
                        }
                        return render(request,'user/login.html',context)
                else:
                    context = {
                        "message" : "Invalid Password",
                        "status_code" : 400
                    }
                    return render(request, 'user/login.html', context)
            else:
                context = {
                        "message" : "Invalid Credentials",
                        "status_code" : 400
                    }
                return render(request, 'user/login.html', {"message": "Invalid Credentials","status_code":400})



class UserHomeView(LoginRequiredMixin,View):
    def get(self, request):
        # CSRF token for form submissions
        csrf_token = get_token(request)

        # Fetch search query from the request
        query = request.GET.get('q', '')

        # Fetch and sort books
        sort_by = request.GET.get('sort_by', 'book_name')  # Default sort by 'book_name'
        order = request.GET.get('order', 'asc')
        
        if order == 'desc':
            sort_by = f'-{sort_by}'  # Add '-' prefix for descending order

        # Filter books based on the search query
        books = BookName.objects.filter(
            book_name__icontains=query
        ) | BookName.objects.filter(
            book_author_name__icontains=query
        )

        # Apply sorting
        books = books.order_by(sort_by)

        # Pagination
        paginator = Paginator(books, 10)  # Show 10 books per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj,
            'sort_by': sort_by.strip('-'),  # Send sorting information back to the template
            'order': order,
            'csrf_token': csrf_token,
            'query': query,  # Include the search query in the context
        }

        return render(request, 'user/home.html', context)





class UserLogoutView(LoginRequiredMixin,View):
    def get(self,request):           
        # Clear all sessions
        request.session.pop('user_id', None)
        return render(request,'user/login.html')






# User Book Issue 
class UserBookIssueView(LoginRequiredMixin,View):
    def post(self,request):
        user_id = request.session.get('user_id')
        book_id = request.POST.get('book_id')
        csrf_token = get_token(request)
        book = BookName.objects.get(book_id = book_id)
        user = User.objects.get(user_mail = user_id)

        book_issue_record = Book_Issue_Record(
            book_id = book,
            user_id = user,
            is_issue_approve = False,
            is_return_approve = None 
        )
        
        book_issue_record.save()

        return JsonResponse({'message': 'Issue Record Added Successfully'}, status=200)
        

# List Book Issue Records

class UserListBookIssueRecord(LoginRequiredMixin,View):
    def get(self,request):
        user_id = request.session.get('user_id')
        user = User.objects.get(user_mail=user_id)

        book_issue_records = Book_Issue_Record.objects.filter(user_id=user)
        
        if not book_issue_records.exists():
            print("No Record Found")
            return render(request, 'user/issue_record.html')  # Render a different template if no records
        return render(request, 'user/issue_record.html', {'book_issue_records': book_issue_records})

class CancelApproveRequest(LoginRequiredMixin,View):
    def post(self,request):
        book_issue_id = request.POST.get('book_issue_id')
        issue_record = get_object_or_404(Book_Issue_Record, book_issue_id=book_issue_id)
        issue_record.delete()
        return JsonResponse({'message':'Issue Request Deleted'})

class RequestReturn(LoginRequiredMixin,View):
    def post(self,request):
        book_issue_id = request.POST.get('book_issue_id')
        issue_record = get_object_or_404(Book_Issue_Record,book_issue_id = book_issue_id)
        issue_record.is_return_approve = False
        issue_record.save()
        return JsonResponse({'message':"Return Request Sent"})






