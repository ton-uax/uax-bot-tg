from django.urls import path

from . import views

app_name = "core.apps.account"


urlpatterns = [
    path("user/", views.RegisterAccountAPIView.as_view(), name="register"),
    path("<int:tg_id>/", views.AccountCheckAPIView.as_view(), name="check-account"),
]
