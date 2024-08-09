from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ViewSet
from rest_framework_nested.routers import NestedMixin


class AppRouter(DefaultRouter):
    """
    Custom router class that disables indicated methods.
    """

    EXCLUDED_METHODS = ('put',)

    def get_method_map(self, viewset: ViewSet, method_map: dict) -> dict:
        """
        SimpleRouter.get_method_map() method extended with excluding indicated methods from method_map.

        Args:
             viewset [ViewSet]: View
             method_map [dict]: Dictionary containing mapping of HTTP methods to View functions like:
             {'delete': 'destroy', 'get': 'retrieve', 'patch': 'partial_update', 'put': 'update'}

        Returns:
            dict: Cleared method map like: {'delete': 'destroy', 'get': 'retrieve', 'patch': 'partial_update'}.
        """
        bound_methods = {}
        for method, action in method_map.items():
            if method in self.EXCLUDED_METHODS:
                continue
            elif hasattr(viewset, action):
                bound_methods[method] = action
        return bound_methods


class AppNestedRouter(NestedMixin, AppRouter):
    """
    Custom nested router class that disables indicated methods.
    """

    pass
