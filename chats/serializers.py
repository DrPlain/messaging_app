from rest_framework import serializers
from .models import User, Message, Conversation
from django.contrib.auth.hashers import make_password
from rest_framework.validators import ValidationError


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'password',
            'phone_number',
            'role',
            'created_at',
            # 'password_hash',
            # 'is_active'
        ]
        read_only_fields = ['created_at', 'id']

    def validate(self, attrs):
        email = attrs['email']
        email_exists = User.objects.filter(email=email).exists()
        if email_exists:
            raise ValidationError('A user with this email already exist')
        return super().validate(attrs)


class MessageSerializer(serializers.ModelSerializer):
    # sender = UserSerializer(read_only=True)
    # conversation = ConversationSerializer(read_only=True)
    # sender_id = serializers.PrimaryKeyRelatedField(
    #     queryset=User.objects.all())  # or use `User` if it's not a custom model
    conversation_id = serializers.PrimaryKeyRelatedField(
        queryset=Conversation.objects.all())  # making it read-only

    class Meta:
        model = Message
        fields = ['message_id', 'conversation_id',
                  'message_body', 'sent_at', 'sender_id']
        read_only_fields = ['message_id', 'sent_at', 'sender_id']


class ConversationSerializer(serializers.ModelSerializer):
    # participants = UserSerializer(many=True, read_only=True)
    # messages = MessageSerializer(many=True, read_only=True)
    participants = serializers.ListField(
        child=serializers.UUIDField(), write_only=True  # Accept a list of user UUIDs
    )
    messages = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'messages', 'created_at']
        read_only_fields = ['conversation_id', 'created_at']

    def get_messages(self, obj):
        messages = obj.messages.all()  # Reverse relationship via related_name
        return MessageSerializer(messages, many=True).data

    def validate_participants(self, value):
        participants = User.objects.filter(id__in=value)
        if participants.count() != len(value):
            raise serializers.ValidationError(
                'One or more of the participants do not exist')
        return value
