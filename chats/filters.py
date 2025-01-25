import django_filters
from .models import Message


class MessageFilter(django_filters.FilterSet):
    conversation_id = django_filters.UUIDFilter(
        field_name='conversation_id', lookup_expr='exact')
    sender_id = django_filters.UUIDFilter(
        field_name='sender_id', lookup_expr='exact')
    start_date = django_filters.DateTimeFilter(
        field_name='sent_at', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(
        field_name='sent_at', lookup_expr='lte')

    class Meta:
        model = Message
        fields = ['conversation_id', 'sender_id', 'start_date', 'end_date']
