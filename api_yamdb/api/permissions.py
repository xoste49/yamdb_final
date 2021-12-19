from rest_framework.permissions import SAFE_METHODS, BasePermission


class AuthorPermisssion(BasePermission):
    """
        С этим разрешением:
        - анонимы могут читать
        - пользователи создавать
        - авторы редактировать и удалять
    """
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS
            or request.user and obj.author
            and request.user.is_authenticated
            and request.user == obj.author
        )


class AdminPermission(BasePermission):
    """
        С этим разрешением:
        - только админы могут читать, создавать, редактировать и удалять
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_admin
        )

    def has_object_permission(self, request, view, obj):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_admin
        )


class AdminOrReadOnly(BasePermission):
    """
        С этим разрешением:
        - пользователи могут читать
        - админы могут создавать, редактировать и удалять
    """
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS
            or request.user
            and request.user.is_authenticated
            and request.user.is_admin
        )

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS
            or request.user
            and request.user.is_authenticated
            and request.user.is_admin
        )


class ModeratorPermission(BasePermission):
    """
        С этим разрешением:
        - только модераторы могут читать, создавать, редактировать и удалять
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_moderator
        )

    def has_object_permission(self, request, view, obj):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_moderator
        )
