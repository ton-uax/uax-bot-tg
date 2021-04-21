from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response
from core.apps.wallet import services as wallet_services
from core.package.ton.api import TonCli


class CreateWalletAPIView(ListAPIView):
    lookup_field = "tg_id"
    lookup_url_kwarg = "tg_id"

    def list(self, request, *args, **kwargs):
        tg_id = self.kwargs["tg_id"]
        new_wallet = wallet_services.create_wallet(tg_id)
        response_data = {
            "address": new_wallet["address"],
            "balance": new_wallet["balance"]
        }
        return Response(status=status.HTTP_200_OK, data=response_data)


class CheckWalletAddressAPIView(ListAPIView):
    lookup_field = "address"
    lookup_url_kwarg = "address"

    def list(self, request, *args, **kwargs):
        address = self.kwargs["address"]
        cli = TonCli(test=True)
        valid_address = cli.check_address(address)
        print(valid_address)
        if valid_address:
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


class SendTXAPIView(GenericAPIView):

    def post(self, request, *args, **kwargs):
        wallet_services.send_tx(request.data)
        return Response(status=status.HTTP_200_OK)


class ActivateWalletAPIView(ListAPIView):
    lookup_field = "wallet_id"
    lookup_url_kwarg = "wallet_id"

    def list(self, request, *args, **kwargs):
        wallet_id = int(self.kwargs["wallet_id"])
        wallet_services.activate_wallet(wallet_id)
        return Response(status=status.HTTP_200_OK)


class EditWalletTitleAPIView(GenericAPIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        wallet_services.edit_wallet_title(data["id"], data["title"])
        return Response(status=status.HTTP_200_OK)


class DeleteWalletAPIView(ListAPIView):
    lookup_field = "wallet_id"
    lookup_url_kwarg = "wallet_id"

    def list(self, request, *args, **kwargs):
        wallet_id = int(self.kwargs["wallet_id"])
        wallet_services.delete_wallet(wallet_id)
        return Response(status=status.HTTP_200_OK)