from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response
from .serializers import RegisterAccountSerializer
from core.apps.account import models as account_models
from core.apps.account import services as account_services


class RegisterAccountAPIView(GenericAPIView):
    serializer_class = RegisterAccountSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        if account_services.register_user(
            tg_id=serializer.validated_data["tg_id"],
            username=serializer.validated_data["username"],
            first_name=serializer.validated_data["first_name"],
            last_name=serializer.validated_data["last_name"]

        ):
            return Response(status=status.HTTP_200_OK)


class AccountCheckAPIView(ListAPIView):
    lookup_field = "tg_id"
    lookup_url_kwarg = "tg_id"

    def list(self, request, *args, **kwargs):
        tg_id = self.kwargs["tg_id"]
        user = account_models.TelegramAccount.objects.filter(tg_id=int(tg_id)).exists()
        if user:
            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_404_NOT_FOUND)