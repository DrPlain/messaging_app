from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import User, Conversation, Message
from .serializers import SignUpSerializer, MessageSerializer, ConversationSerializer
from django.urls import reverse
from uuid import uuid4


class UserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "securepassword",
            "phone_number": "123456789",
            "role": "User",
        }

    def test_signup_user(self):
        response = self.client.post(reverse('signup'), self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'User created successfully')

    def test_signup_user_with_existing_email(self):
        User.objects.create(**self.user_data)
        response = self.client.post(reverse('signup'), self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('A user with this email already exist',
                      str(response.data['error']))


class ConversationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create(
            email="user1@example.com", password="password")
        self.user2 = User.objects.create(
            email="user2@example.com", password="password")
        self.conversation_data = {
            "participants": [str(self.user1.id), str(self.user2.id)],
        }
        self.client.force_authenticate(user=self.user1)

    def test_create_conversation(self):
        response = self.client.post(
            reverse('conversation-list'), self.conversation_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'],
                         'Conversation created successfully')

    def test_list_conversations(self):
        Conversation.objects.create()
        response = self.client.get(reverse('conversation-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)


class MessageTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            email="user@example.com", password="password")
        self.conversation = Conversation.objects.create()
        self.message_data = {
            "conversation_id": self.conversation.id,
            "message_body": "Hello, World!",
        }
        self.client.force_authenticate(user=self.user)

    def test_create_message(self):
        response = self.client.post(reverse('message-list'), self.message_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'],
                         'Message created successfully')

    def test_list_messages(self):
        Message.objects.create(
            conversation_id=self.conversation,
            sender_id=self.user,
            message_body="Test message"
        )
        response = self.client.get(reverse('message-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)


class SerializerTests(TestCase):
    def test_signup_serializer_validation(self):
        data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com",
            "password": "securepassword",
            "phone_number": "987654321",
            "role": "Admin",
        }
        serializer = SignUpSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_signup_serializer_existing_email(self):
        User.objects.create(
            first_name="Jane",
            last_name="Doe",
            email="jane.doe@example.com",
            password="securepassword",
        )
        data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com",
            "password": "securepassword",
            "phone_number": "987654321",
            "role": "Admin",
        }
        serializer = SignUpSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_message_serializer(self):
        user = User.objects.create(
            email="user@example.com", password="password")
        conversation = Conversation.objects.create()
        data = {
            "conversation_id": conversation.id,
            "message_body": "Test message",
            "sender_id": user.id,
        }
        serializer = MessageSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_conversation_serializer(self):
        user1 = User.objects.create(
            email="user1@example.com", password="password")
        user2 = User.objects.create(
            email="user2@example.com", password="password")
        data = {
            "participants": [str(user1.id), str(user2.id)],
        }
        serializer = ConversationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
