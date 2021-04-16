from django.conf import settings
from rest_framework import serializers


class RegisterAccountSerializer(serializers.Serializer):
    tg_id = serializers.IntegerField()
    username = serializers.CharField(max_length=255)
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)

    class Meta:
        fields = (
            "tg_id",
            "user_name",
            "first_name",
            "last_name"
        )
