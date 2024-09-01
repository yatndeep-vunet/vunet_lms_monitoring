from django.db import models
from django_prometheus.models import ExportModelOperationsMixin
class User(ExportModelOperationsMixin('Users'),models.Model):
    user_id = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    user_name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    user_mail = models.CharField(max_length=255)
    email_token = models.CharField(max_length=255 , null=True)
    is_email_verfied = models.BooleanField(default=False)

    def __str__(self):
        return self.user_name

class BookName(ExportModelOperationsMixin('Books'),models.Model):
    book_id = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    book_name = models.CharField(max_length=255)
    book_author_name = models.CharField(max_length=255)
    book_category_id = models.ForeignKey('Books_Category', on_delete=models.CASCADE)

    def __str__(self):
        return self.book_name

class Books_Category(ExportModelOperationsMixin('Book_category'),models.Model):
    book_category_id = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    book_category = models.CharField(max_length=255)

    def __str__(self):
        return self.book_category


class Book_Issue_Record(ExportModelOperationsMixin('Book_Issue_Record'),models.Model):
    book_issue_id = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    book_id = models.ForeignKey('BookName', on_delete=models.CASCADE)  # Changed to ForeignKey for proper relation
    user_id = models.ForeignKey('User', on_delete=models.CASCADE)  # Changed to ForeignKey for proper relation
    is_issue_approve = models.BooleanField()
    issue_date = models.DateField(null=True)
    is_return_approve = models.BooleanField(null=True)
    return_date = models.DateField(null=True)
    fine = models.IntegerField(null=True)

    def __str__(self):
        return str(self.book_issue_id)

class Librarian(models.Model):
    librarian_id = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    
    def __str__(self):
        return str(self.librarian_id)