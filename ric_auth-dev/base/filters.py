from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _

from rest_framework.compat import coreapi, coreschema
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter


class DynamicSearchFilter(SearchFilter):
    search_pattern_param = "search_pattern"
    search_pattern_title = _("search pattern")
    search_pattern_description = _('Choose which pattern to use when searching.')

    def get_search_patterns(self, view):
        return getattr(view, 'search_patterns', None)

    def get_search_fields(self, view, request):
        """
        Search fields are obtained from the view, but the request is always
        passed to this method. Sub-classes can override this method to
        dynamically change the search fields based on request content.
        """
        default_search_fields = super(DynamicSearchFilter, self).get_search_fields(view, request)

        search_pattern = request.query_params.get(self.search_pattern_param, None)
        if not search_pattern:
            return default_search_fields

        search_patterns = self.get_search_patterns(view)
        if search_pattern in search_patterns:
            return search_patterns[search_pattern]
        else:
            raise ValidationError("Search pattern {} is not supported".format(search_pattern))

    def get_schema_fields(self, view):
        parent_fields = super(DynamicSearchFilter, self).get_schema_fields(view)
        return parent_fields + [
            coreapi.Field(
                name=self.search_pattern_param,
                required=False,
                location='query',
                schema=coreschema.String(
                    title=force_str(self.search_pattern_title),
                    description=force_str(self.search_pattern_description)
                )
            )
        ]

    def get_schema_operation_parameters(self, view):
        parent_parameters = super(DynamicSearchFilter, self).get_schema_operation_parameters(view)
        return parent_parameters + [
            {
                'name': self.search_pattern_param,
                'required': False,
                'in': 'query',
                'description': force_str(self.search_pattern_description),
                'schema': {
                    'type': 'string',
                    'enum': list(self.get_search_patterns(view).keys()),
                },
            },
        ]
