from uuid import uuid4
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff set to True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser set to True')
        return self.create_user(email=email, password=password, **extra_fields)


class User(AbstractUser):

    ROLE_CHOICES = [
        ('guest', 'guest'),
        ('host', 'host'),
        ('admin', 'admin')
    ]
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    # first_name = models.CharField(max_length=255)
    # last_name = models.CharField(max_length=255)
    username = models.CharField(
        max_length=150, blank=True, null=True, unique=False)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']

    class Meta:
        indexes = [
            models.Index(fields=['email'])
        ]

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Conversation(models.Model):
    conversation_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False)
    participants = models.ManyToManyField(
        User, related_name='conversations')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Conversation {self.conversation_id} created at {self.created_at}"


class Message(models.Model):
    message_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False)
    sender_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='messages')
    conversation_id = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='messages')
    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['sent_at'])
        ]
        ordering = ['sent_at']

    def __str__(self):
        return f"Message from {self.sender.email} at {self.sent_at}"
