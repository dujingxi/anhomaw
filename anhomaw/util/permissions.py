
from rest_framework.permissions import BasePermission


class MyCommonPermission(BasePermission):
    def has_permission(self, request, view):
        user_obj = request.user
        user_role = user_obj.role
        if user_role < 1:
            return False
        return True

class MyAdminPermission(BasePermission):
    def has_permission(self, request, view):
        user_obj = request.user
        user_role = user_obj.role
        if user_role < 2:
            return False
        return True

class MySuperAdminPermission(BasePermission):
    def has_permission(self, request, view):
        user_obj = request.user
        user_role = user_obj.role
        if user_role < 3:
            return False
        return True