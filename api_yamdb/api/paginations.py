from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """
    Пагинация для API по 10 элементов на страницу
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000
