from django.urls import path

from . import views

app_name = "core.apps.wallet"


urlpatterns = [
    path("create/<int:tg_id>/", views.CreateWalletAPIView.as_view(), name="create_wallet"),
    path("check/<str:address>/", views.CheckWalletAddressAPIView.as_view(), name="check_wallet"),
    path("sendTx/", views.SendTXAPIView.as_view(), name="check_wallet")

]
