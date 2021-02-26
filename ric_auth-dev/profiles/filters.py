import django_filters


class NumberRangeFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    pass


class CustomUserFilterSet(django_filters.FilterSet):
    organization = django_filters.NumberFilter(lookup_expr='exact')
    katakana_name = django_filters.CharFilter(lookup_expr="icontains")
    hiragana_name = django_filters.CharFilter(lookup_expr="icontains")
    group_ids = NumberRangeFilter(
        method='filter_by_group',
        label='Filter by group ids. Values can be comma separated. ex: 1,2',
        required=False
    )
    exclude_current_user = django_filters.BooleanFilter(
        label='Specify whether to exclude current user or not',
        method="do_exclude_current_user",
        required=False,
    )

    def do_exclude_current_user(self, queryset, field_name, value):
        current_user = self.request.user
        if value and current_user:
            return queryset.exclude(pk=current_user.pk)
        else:
            return queryset

    def filter_by_group(self, queryset, field_name, value):
        if value:
            ids = (obj.id for obj in queryset.iterator() if any(id in obj.group_ids for id in value))
            return queryset.filter(id__in=ids)
        return queryset


class GroupFilterSet(django_filters.FilterSet):
    organization = django_filters.NumberFilter(lookup_expr='exact')
    hierarchy = django_filters.CharFilter(lookup_expr="exact")
    ids = NumberRangeFilter(
        field_name='id',
        lookup_expr='in',
        label='Filter by ids. Values can be comma separated. ex: 1,2',
        required=False
    )
