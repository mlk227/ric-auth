from rest_framework.pagination import PageNumberPagination


class DefaultResultSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 500

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'count': {
                    'type': 'integer',
                    'description': 'Total number of the result',
                    'example': 123,
                },
                'next': {
                    'type': 'string',
                    'description': 'Link to the next page of the result. `Null` if this is the last page.',
                    'nullable': True,
                },
                'previous': {
                    'type': 'string',
                    'description': 'Link to the previous page of the result. `Null` if this is the first page.',
                    'nullable': True,
                },
                'results': schema,
            },
        }
