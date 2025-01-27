from django.shortcuts import render
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet
from .models import Conversation, Message, User
from .filters import MessageFilter
from .serializers import ConversationSerializer, MessageSerializer, SignUpSerializer
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from .permissions import IsParticipantOfConversation
from rest_framework.generics import ListAPIView
from .auth import get_token_pair
# Create your views here.


class ConversationViewSet(ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsParticipantOfConversation, IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['created_at']  # Enable filtering by created_at
    # Enable search by participant email
    search_fields = ['participants__email']
    ordering_fields = ['created_at']  # Enable ordering by created_at

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'message': 'Conversation created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


class MessageViewSet(ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter

    def create(self, request, *args, **kwargs):
        # response = super().create(request, *args, **kwargs)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender_id=request.user)
            return Response({
                'message': 'Message created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "error": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class SignUpView(generics.GenericAPIView):
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]

    def post(self, request: Request, *args, **kwargs):
        data = request.data.copy()
        data['password'] = make_password(data.pop('password', None))
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'User created successfully',
                # 'token': get_token_pair(user)
                'user': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'error': serializer.errors
        }, status.HTTP_400_BAD_REQUEST)


class UserListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
