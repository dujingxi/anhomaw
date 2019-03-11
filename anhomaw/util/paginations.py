from rest_framework.pagination import PageNumberPagination, CursorPagination

class MyNumberPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'size'
    max_page_size = 100

class MyCursorPagination(CursorPagination):
    cursor_query_param = 'cursor'
    ordering = '-id'
    page_size_query_param = "size"
    max_page_size = 100