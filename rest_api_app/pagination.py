from rest_framework.pagination import PageNumberPagination

class BookPagination(PageNumberPagination):
    page_size = 2  # Default number of items per page
    page_size_query_param = 'page_size'  # Allow clients to set the page size with a query parameter
    max_page_size = 100  # Maximum limit for page size
