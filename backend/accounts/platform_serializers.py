from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class AccountCreateSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    roles = serializers.ListField(child=serializers.CharField(), required=False)
    send_email = serializers.BooleanField(required=False, default=False)

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value


class AccountUpdateSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=150, required=False)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    roles = serializers.ListField(child=serializers.CharField(), required=False)


class DecisionSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(choices=["accept", "reject"])
    note = serializers.CharField(required=False, allow_blank=True)