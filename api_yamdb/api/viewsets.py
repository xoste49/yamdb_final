from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response


class CustomModelViewSet(viewsets.ModelViewSet):

    def retrieve(self, request, *args, **kwargs):
        try:
            super().retrieve(self, request, *args, **kwargs)
        except Exception:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(self.get_queryset(), slug=kwargs['pk'])
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
