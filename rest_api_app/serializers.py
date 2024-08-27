# serializers.py

from rest_framework import serializers
from core_app.models import BookName , User , Books_Category , Book_Issue_Record
import random




class BookCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Books_Category
        fields = ['book_category_id', 'book_category']


class BookSerializer(serializers.ModelSerializer):
    book_category_id = BookCategorySerializer()  # Use the nested serializer

    class Meta:
        model = BookName
        fields = ['book_id', 'book_name', 'book_author_name', 'book_category_id']
class Book_Issue_Record_Serializer(serializers.ModelSerializer):
    class Meta: 
        model = Book_Issue_Record
        fields  = '__all__'

class AddBookSerializer(serializers.Serializer):
    book_name = serializers.CharField()
    book_author_name = serializers.CharField()
    book_category_id = serializers.IntegerField()

class AddCategorySerializer(serializers.Serializer):
    book_category = serializers.CharField()





class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_name', 'password', 'user_mail']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    def validate_user_name(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError("User name must be a string")
        return value

    def validate_password(self, value):
        return value
    def create(self, validated_data):
        user = User(
            user_name=validated_data['user_name'],
            user_mail=validated_data['user_mail'],
            password=validated_data['password'],  # No hashing
            email_token=random.randint(1000, 9999)  # Generate email token
        )
        user.save()
        return user
    
class UserLoginSerializer(serializers.Serializer):
    user_mail = serializers.EmailField()
    password = serializers.CharField(write_only = True)

class LibrarianLoginSerializer(serializers.Serializer):
    librarian_id = serializers.CharField()
    password = serializers.CharField(write_only = True)


