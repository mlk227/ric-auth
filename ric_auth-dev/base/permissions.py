from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly


class IsOptionsOrAuthenticated(IsAuthenticated):
    """
    Allow OPTIONS from anyone, otherwise require authenticated.
    """

    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return True

        return super(IsOptionsOrAuthenticated, self).has_permission(request, view)


class IsOptionsOrAuthenticatedOrReadOnly(IsAuthenticatedOrReadOnly):
    """
    Allow OPTIONS from anyone, otherwise require authenticated or read-only.
    """

    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return True

        return super(IsOptionsOrAuthenticatedOrReadOnly, self).has_permission(request, view)
