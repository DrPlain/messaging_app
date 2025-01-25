from rest_framework.permissions import BasePermission


class IsParticipantOfConversation(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user in obj.participants.all():
            return True
        return False
