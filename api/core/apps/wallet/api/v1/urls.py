from django.urls import path

from . import views

app_name = "core.apps.wallet"


urlpatterns = [
    path("create/<int:tg_id>/", views.CreateWalletAPIView.as_view(), name="create_wallet"),
    path("check/<str:address>/", views.CheckWalletAddressAPIView.as_view(), name="check_wallet"),
    path("sendTx/", views.SendTXAPIView.as_view(), name="send_tx"),
    path("activate/<int:wallet_id>/", views.ActivateWalletAPIView.as_view(), name="activate_wallet"),
    path("editTitle/", views.EditWalletTitleAPIView.as_view(), name="edit_wallet_title"),
    path("delete/<int:wallet_id>/", views.DeleteWalletAPIView.as_view(), name="delete_wallet"),
    path("addFromPhrase/", views.AddFromPhraseAPIView.as_view(), name="add_wallet_from_mnemonic")


]
