from rest_framework import permissions, status, exceptions


class OrganizationPermission(permissions.BasePermission):
    message = 'You are not Organization, you can not'
    status_code = status.HTTP_403_FORBIDDEN

    def has_permission(self, request, view):
        if request.user.role == 'organization':
            raise ServiceUnavailable
        return True


class ServiceUnavailable(exceptions.APIException):
    status_code = 403
    default_detail = 'You are not Organization,you can not'
    default_code = 'You are not Organization,you can not'
