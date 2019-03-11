
from rest_framework.throttling import SimpleRateThrottle


class MyDefaultThrottle(SimpleRateThrottle):
    scope = 'default'

    def get_cache_key(self, request, view):
        return self.get_ident(request)

class MyDatabaseThrottle(SimpleRateThrottle):
    scope = 'database'

    def get_cache_key(self, request, view):
        return self.get_ident(request)