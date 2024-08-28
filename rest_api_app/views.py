from django.shortcuts import render
from rest_framework import viewsets ,status ,filters
from core_app.models import BookName , User , Librarian , Books_Category , Book_Issue_Record
from .serializers import BookSerializer , UserRegisterSerializer , UserLoginSerializer , LibrarianLoginSerializer , AddBookSerializer , AddCategorySerializer , BookCategorySerializer , Book_Issue_Record_Serializer , BookIDSerializer , BookIssueSerializer
from django.core.mail import send_mail , BadHeaderError
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
import random
from .pagination import BookPagination
from datetime import datetime, date, time, timedelta

import logging



logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ViewSet):
    def get_serializer_class(self):
         if self.action == 'user_login':
            return UserLoginSerializer
         return UserRegisterSerializer


    def get_serializer(self, *args, **kwargs):
        return self.get_serializer_class()(*args, **kwargs)

    # Create or Register User 
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user_mail = serializer.validated_data.get('user_mail')

            # Check if a user with the same email already exists
            if User.objects.filter(user_mail=user_mail).exists():
                return Response(
                    {'status': 400, 'message': 'User with this email already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            email_token = random.randint(1000, 9999)  # Generate a token

            # Generate the verification URL using the email address
            host = request.get_host()
            protocol = 'https' if request.is_secure() else 'http'
            verify_url = f'{protocol}://{host}/users/verify_mail/?email={user_mail}&email_token={email_token}'

            # Send verification email
            try:
                send_mail(
                    subject='Vu-LMS Verification Mail',
                    message='',
                    html_message=f'Please verify your mail with the given link <a href="{verify_url}">Verify</a>',
                    from_email='momentswithdreams@gmail.com',
                    recipient_list=[user_mail],
                    fail_silently=False,
                )

                # Create the user after sending the email
                user_data = serializer.validated_data
                user_data['email_token'] = email_token  # Add the email token
                user = User(**user_data)
                user.save()

                logger.info(f'User {user_mail} registered successfully.')
                return Response(
                    {'status': 200, 'message': 'A verification mail has been sent to your email Id, please verify your email Id'},
                    status=status.HTTP_201_CREATED
                )
            except BadHeaderError:
                logger.error('Invalid header found.')
                return Response(
                    {'status': 400, 'message': 'Invalid header found during email sending'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                logger.error(f'Error sending email: {e}')
                return Response(
                    {'status': 500, 'message': 'Failed to send verification email'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Verify Mail of user 
    @action(detail = False , methods = ['get'])
    def verify_mail(self,request):
        email = request.query_params.get('email')
        email_token = request.query_params.get('email_token')
        if not email or not email_token:
            return Response(
                {'status': 400, 'message': 'Email and email_token are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            # Retrieve user by email
            user = User.objects.get(user_mail=email)

            # Check if the provided token matches the user's token
            if user.email_token == email_token:
                user.is_email_verfied = True # Assuming you have an `is_email_verfied` field
                user.email_token = None
                user.save()
                return Response(
                    {'status': 200, 'message': 'Email verified successfully'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'status': 400, 'message': 'Invalid email token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except User.DoesNotExist:
            return Response(
                {'status': 404, 'message': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f'Error occurred during email verification: {e}')
            return Response(
                {'status': 500, 'message': 'Internal Server Error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    # User Login
    
    @action(detail=False, methods=['post'])
    def user_login(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user_mail = serializer.validated_data.get('user_mail')
            password = serializer.validated_data.get('password')

            try:
                user = User.objects.get(user_mail=user_mail)
                # Check if the password is correct
                if user.password == password:
                    if user.is_email_verfied:
                        # Store user ID in session
                        request.session['user_mail'] = user.user_mail
                        request.session.save()

                        logger.info(f'User {user_mail} logged in successfully.')
                        
                        return Response(
                            {"message": "Successfully Logged In", "status_code": 200},
                            status=status.HTTP_200_OK
                        )
                    else:
                        return Response(
                            {"message": "Please verify your mail", "status_code": 400},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                else:
                    return Response(
                        {"message": "Invalid Password", "status_code": 400},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except User.DoesNotExist:
                return Response(
                    {"message": "Invalid Credentials", "status_code": 400},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                logger.error(f'Error occurred during login: {e}')
                return Response(
                    {"message": "Internal Server Error", "status_code": 500},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


        # Log Out 
    @action(detail=False, methods=['get'])
    def user_logout(self, request):
        try:
            # Clear the session data to log the user out
            #print(request.session.get('user_mail'))
            request.session.pop('user_mail', None)
            logger.info('User logged out successfully.')

            return Response({'status': 200, 'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error during logout: {e}')
            return Response({'status': 'error', 'message': 'An error occurred during logout'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class BookViewSet(viewsets.ModelViewSet):
    queryset = BookName.objects.all()  # Explicitly define the queryset
    serializer_class = BookSerializer  # Default serializer for list and retrieve actions
    pagination_class = BookPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter)
    filterset_fields = ['book_category_id', 'book_author_name', 'book_name']
    search_fields = ['book_name', 'book_author_name']
    ordering_fields = ['book_category_id', 'book_author_name', 'book_name']
    ordering = ['book_name']  # Default ordering

    def get_serializer_class(self):
        if self.action == 'add_book':
            return AddBookSerializer
        if self.action == 'delete_book':
            return BookIDSerializer
        return BookSerializer

    def get_serializer(self, *args, **kwargs):
        return self.get_serializer_class()(*args, **kwargs)
    

    def list(self, request, *args, **kwargs):
        try:
            # Fetch the queryset
            queryset = self.filter_queryset(self.get_queryset())

            # Apply pagination
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            # Serialize the data
            serializer = self.get_serializer(queryset, many=True)

            logger.info('Book list retrieved successfully.')
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f'Error retrieving book list: {e}')
            return Response({'status': 'error', 'message': 'Internal Server Error'}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # Add Books ----------------------------->>>>>>>>>>>>>>>>--------<<<<<<<<<<<<<<<<<<<<<<<<<<<<---------------------------------------

    @action(detail=False, methods=['post'])
    def add_book(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            book_name = serializer.validated_data.get('book_name')
            book_author_name = serializer.validated_data.get('book_author_name')
            book_category_id = serializer.validated_data.get('book_category_id')

            try:
                # Ensure the category exists
                book_category = Books_Category.objects.get(book_category_id=book_category_id)

                # Check for duplicate books
                if BookName.objects.filter(book_name=book_name, book_author_name=book_author_name).exists():
                    return Response({'message': 'Book with the same author already exists'}, status=status.HTTP_400_BAD_REQUEST)

                # Create the new book record
                book = BookName(
                    book_name=book_name,
                    book_author_name=book_author_name,
                    book_category_id=book_category  # Correctly assign the instance
                )
                book.save()

                return Response({'status': 'success', 'message': 'Book Successfully Added'}, status=status.HTTP_201_CREATED)

            except Books_Category.DoesNotExist:
                return Response({'status': 'error', 'message': 'Book Category Does Not Exist'}, status=status.HTTP_404_NOT_FOUND)

            except Exception as e:
                logger.error(f'Error while adding book: {e}')
                return Response({'status': 'error', 'message': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail= False , methods= ['post'])
    def delete_book(self,request):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():

                book_id = serializer.validated_data.get('book_id')
            
                librarian_id = request.session.get('rest_librarian_id')
                if librarian_id is None : 
                    return Response({'status':'error','message':'You are not authorize for this operation'},status=status.HTTP_401_UNAUTHORIZED)
                try:
                    book = BookName.objects.get(book_id=book_id)
                except BookName.DoesNotExist:
                    return Response({'status': 'error', 'message': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)

                # Check if the book is issued to any user
                if Book_Issue_Record.objects.filter(book_id=book).exists():
                    return Response({'status': 'error', 'message': 'Cannot delete book issued to users'}, status=status.HTTP_400_BAD_REQUEST)

                # If not issued, delete the book
                book.delete()
                return Response({'status': 'success', 'message': 'Book successfully deleted'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        except Exception as e:
            return Response({'status':'error','message':f'Internal server error {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(detail=False, methods=['get'])
    def unissued_books(self, request):
        try:
        
            issued_books = Book_Issue_Record.objects.values_list('book_id', flat=True)
            unissued_books = BookName.objects.exclude(pk__in=issued_books)

            serializer = self.get_serializer(unissued_books, many=True)
            return Response({
                'status': 'success',
                'message': 'Unissued books retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f'Error retrieving unissued books: {e}')
            return Response({'status': 'error', 'message': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Librarian ---------------------->>>>>>>>>>>>>>>>>>>>>>>>>>>+++<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<--------------------------------------------------------

class LibrarianViewSet(viewsets.ViewSet):
    def get_serializer_class(self):
        return LibrarianLoginSerializer

    def get_serializer(self, *args, **kwargs):
        return self.get_serializer_class()(*args, **kwargs)
    
    @action(detail=False, methods=['post'])
    def librarian_login(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            librarian_id = serializer.validated_data.get('librarian_id')
            password = serializer.validated_data.get('password')
            try:
                
                librarian = Librarian.objects.get(librarian_id = librarian_id) 

                if librarian.password == password :
                    request.session['rest_librarian_id'] = librarian_id
                    request.session.save()

                   
                    return Response({'status':'succes','message':'Successfully Logged In'},status=status.HTTP_200_OK)
                else :
                    return Response({'status':'error','message':'Invalid Password'},status=status.HTTP_400_BAD_REQUEST)

            except Librarian.DoesNotExist:
                return Response({'status':'error' ,'messsage' :"Invalid Credentials" },status=status.HTTP_400_BAD_REQUEST)
            
            except Exception as e:
                logger.error(f'Error Librarian Login ',{e})
                return Response({'status':'error','message' : 'Internal Server Error'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
    
    @action(detail=False, methods=['get'])
    def librarian_logout(self,request):
        try:
            # Clear the session data to log the librarian out

            request.session.pop('rest_librarian_id', None)
            logger.info('Librarian logged out successfully.')

            return Response({'status': 200, 'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error during logout: {e}')
            return Response({'status': 'error', 'message': 'An error occurred during logout'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Add Category
# Add Book  (book_name , book_author_name , book_cateogry_id)
# Delete Book


class Book_Category_Viewset(viewsets.ViewSet):

    def get_serializer_class(self):
            if self.action == 'add_book':
                return AddCategorySerializer
            return BookCategorySerializer

    def get_serializer(self, *args, **kwargs):
         return self.get_serializer_class()(*args, **kwargs)
    
    def list(self,request, *args, **kwargs):
        try:
            queryset = Books_Category.objects.all()
            serializer = self.get_serializer(queryset, many=True)

            logger.info('Book Category list retrieved successfully.')
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error Occured at Book Cateogry Retrievel{e}')
            return Response({'status':'error','message':'Internal Server Error'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    
    @action(detail=False , methods=['post'])
    def add_book_category(self,request):
        
        serializer = self.get_serializer(data = request.data)

        if serializer.is_valid():
            book_category = serializer.validated_data.get('book_category')
            try :
                if Books_Category.objects.filter(book_category=book_category).exists():
                    return Response({'status':'error','message':'Book Category Already Exist'},status=status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    book_ctg = Books_Category(
                        book_category = book_category
                    )
                    book_ctg.save() 
                    logger.info("Book Category Addded Successfully")
                    return Response({'status':'success','message':'Book Cateogry Added'},status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f'Error occures in adding book category {e}')
                return Response({'status':'error','message':'Internal Server Error'},status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

   

# Get Book 
'''
book_id 
user_id (in case of api we are using user_mail in session storage so that will helpful for us)

'''

class UserGetBookView(viewsets.ViewSet):
    def get_serializer_class(self):
        if self.action == 'user_get_book':
            return BookIDSerializer
        return BookIssueSerializer

    def get_serializer(self, *args, **kwargs):
        return self.get_serializer_class()(*args, **kwargs)
    
    @action(detail=False , methods=['post'])
    def user_get_book(self,request):
        try:
           user_mail = request.session.get('user_mail')
           book_id = request.data.get('book_id')
           print(user_mail)
           if user_mail is None:
               return Response({'status':'error','message':'You need to login to get books'},status=status.HTTP_401_UNAUTHORIZED)
           elif BookName.objects.filter(book_id=book_id).exists() == False:
               return Response({'status':'error','message':'Book Not Exist'},status= status.HTTP_404_NOT_FOUND)
           else:
                book = BookName.objects.get(book_id = book_id)
                user = User.objects.get(user_mail = user_mail)

                new_issue_record = Book_Issue_Record(
                    book_id = book,
                    user_id = user,
                    is_issue_approve = False,
                    is_return_approve = None 
                )
                new_issue_record.save()
                logger.info("Issue Record Added Successfully")
                return Response({'status':'success','message':'Book Issue Record Added Successfully'},status=status.HTTP_201_CREATED)
        except Exception as e:
                logger.error(f'Error Occured at adding issue record {e}')
                return Response({'status':'error','message':'Internal Server Error'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def list(self,request):
        try:
            librarian_id = request.session.get('librarian_id')
    
            if librarian_id is None:    
                  return Response({'status':'error','message':'You are not authorized for this operation'},status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
            else:
                queryset = Book_Issue_Record.objects.all()
                serializer = Book_Issue_Record_Serializer(queryset, many=True)
                logger.info('Book Issue Record list retrieved successfully.')
                return Response(serializer.data, status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.error(f'Error Occured at Book Issue Record Retrievel{e}')
            return Response({'status':'error','message':'Internal Server Error'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False , methods=['get'])
    def user_book_issue_record(self,request):
        try:
            user_id = request.session.get('user_mail')
            
            if user_id is None:
                  return Response({'status':'error','message':'You are not authorized for this operation'},status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
            else :
                user = User.objects.get(user_mail=user_id)
                queryset = Book_Issue_Record.objects.filter(user_id=user)
                serializer = Book_Issue_Record_Serializer(queryset , many = True)
                logger.info('Book Issue Record list retrieved successfully.')
                return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f'Error Occured at Book Issue Record Retrievel{e}')
            return Response({'status':'error','message':'Internal Server Error'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @action(detail=False, methods=['post'])
    def approve_book_request(self, request):
        try:
            librarian_id = request.session.get('rest_librarian_id')
            book_issue_id = request.data.get('book_issue_id')

            if librarian_id is None:
                return Response({'status': 'error', 'message': 'You are not authorized for this request'}, status=status.HTTP_401_UNAUTHORIZED)

            if not Book_Issue_Record.objects.filter(book_issue_id=book_issue_id).exists():
                return Response({'status': 'error', 'message': 'No issue record found'}, status=status.HTTP_404_NOT_FOUND)

            try:
                book_issue_record = Book_Issue_Record.objects.get(book_issue_id=book_issue_id)
            except Book_Issue_Record.DoesNotExist:
                return Response({'status': 'error', 'message': 'No issue record found'}, status=status.HTTP_404_NOT_FOUND)

            if book_issue_record.is_issue_approve:
                return Response({'status': 'success', 'message': 'Issue already approved'}, status=status.HTTP_202_ACCEPTED)

            book_issue_record.is_issue_approve = True
            book_issue_record.issue_date = date.today().strftime("%Y-%m-%d")
            book_issue_record.save()

            return Response({'status': 'success', 'message': 'Issue request approved'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': 'error', 'message': f'Internal Server Error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # User Will request for return ------------------------------------>>>>>>>>------------------>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.
    @action(detail = False , methods= ['post'])
    def user_return_request(self,request):
        try:
            user_mail = request.session.get('user_mail')
         
            book_issue_id = request.data.get('book_issue_id')
            if user_mail is None:
                return Response({'status':'error','message':'You are not authorize for this request'},status=status.HTTP_401_UNAUTHORIZED)
            try:
                 book_issue_record = Book_Issue_Record.objects.get(book_issue_id=book_issue_id)
                 user = User.objects.get(user_mail = user_mail)
                 
                 # Check for user is related to the record or not 
                 if book_issue_record.user_id == user : 

                    # check for the return is already requested or not .
                    if book_issue_record.is_issue_approve == False:
                        return Response({'status':'error','message':'The Book Issue is not approved so return will not allowed'},status=status.HTTP_400_BAD_REQUEST)
                    if book_issue_record.is_return_approve == False :
                        return Response({'status':'success','message':'Already Requested For Return'},status=status.HTTP_200_OK)
                    else:
                        book_issue_record.is_return_approve = False
                        book_issue_record.save() 
                        return Response({'status':'success','message':'Return is Requested'},status=status.HTTP_202_ACCEPTED)
                    
                 else :
                      return Response({'status':'success','message':'The user is not related to the record'},status=status.HTTP_200_OK)
                     
            except Book_Issue_Record.DoesNotExist:
                return Response({'status': 'error', 'message': 'No issue record found'}, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({'status': 'error', 'message': f'Internal Server Error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    @action(detail= False , methods=['post'])
    def approve_return_request(self,request):
        try:
            librarian_id = request.session.get('rest_librarian_id')
            book_issue_id = request.data.get('book_issue_id')

            if librarian_id is None:
                return Response({'status': 'error', 'message': 'You are not authorized for this request'}, status=status.HTTP_401_UNAUTHORIZED)

            if not Book_Issue_Record.objects.filter(book_issue_id=book_issue_id).exists():
                return Response({'status': 'error', 'message': 'No issue record found'}, status=status.HTTP_404_NOT_FOUND)

            try:
                book_issue_record = Book_Issue_Record.objects.get(book_issue_id=book_issue_id)

            except Book_Issue_Record.DoesNotExist:
                return Response({'status': 'error', 'message': 'No issue record found'}, status=status.HTTP_404_NOT_FOUND)
            
            if book_issue_record.is_return_approve is None:
                return Response({'status': 'error', 'message': 'No Return Request for this issue record'}, status=status.HTTP_204_NO_CONTENT)

            if book_issue_record.is_return_approve:
                return Response({'status': 'success', 'message': 'Return already approved'}, status=status.HTTP_202_ACCEPTED)

            book_issue_record.is_return_approve = True
            book_issue_record.return_date = date.today().strftime("%Y-%m-%d")
            book_issue_record.save()

            return Response({'status': 'success', 'message': 'Return request approved'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': 'error', 'message': f'Internal Server Error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






