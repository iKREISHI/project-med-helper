from rest_framework.pagination import PageNumberPagination


class DialogMessagePagination(PageNumberPagination):
    """
    page / page_size пагинация для сообщений диалога.
    """
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200
