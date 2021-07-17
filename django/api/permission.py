from rest_framework import permissions


class IsSuperUserOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user.is_superuser


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return obj.user == request.user or request.user.is_superuser


class IsStaffOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.staffauth.is_staff or request.user.is_superuser


class IsSuperUserOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser
