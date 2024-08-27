# core_app/admin.py
from django.contrib import admin
from .models import User, BookName, Books_Category, Book_Issue_Record , Librarian
from django.contrib.sessions.models import Session

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'user_name', 'password', 'user_mail','email_token', 'is_email_verfied')  # List fields to display
    search_fields = ('user_name', 'user_mail')  # Enable search on user_name and user_mail

@admin.register(BookName)
class BookNameAdmin(admin.ModelAdmin):
    list_display = ('book_id', 'book_name', 'book_author_name', 'book_category_id')  # List fields to display
    search_fields = ('book_name', 'book_author_name')  # Enable search on book_name and book_author_name

@admin.register(Books_Category)
class BooksCategoryAdmin(admin.ModelAdmin):
    list_display = ('book_category_id', 'book_category')  # List fields to display
    search_fields = ('book_category',)  # Enable search on book_category


@admin.register(Book_Issue_Record)
class BookIssueRecordAdmin(admin.ModelAdmin):
    list_display = ('book_issue_id', 'book_id', 'user_id', 'is_issue_approve', 'issue_date', 'is_return_approve', 'return_date', 'fine')  # List fields to display
    search_fields = ('book_issue_id', 'book_id', 'user_id')  # Enable search on book_issue_id, book_id, and user_id



@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'session_data', 'expire_date')
    search_fields = ('session_key',)
    readonly_fields = ('session_key', 'session_data', 'expire_date')

@admin.register(Librarian)
class LibrarianAdmin(admin.ModelAdmin):
    list_display = ('librarian_id','password')


