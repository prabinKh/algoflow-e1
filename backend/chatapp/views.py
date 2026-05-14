from rest_framework import permissions, viewsets

from eadmin.models import ChatMessage, ChatSession

from .serializers import ChatMessageSerializer, ChatSessionSerializer
from .tasks import generate_ai_response


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class ChatSessionViewSet(viewsets.ModelViewSet):
    queryset = ChatSession.objects.all().order_by("-last_message_time")
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        if self.request.user.is_authenticated and getattr(self.request.user, "is_admin", False):
            return ChatSession.objects.all().order_by("-last_message_time")

        if self.request.user.is_authenticated:
            return ChatSession.objects.filter(user=self.request.user).order_by("-last_message_time")

        guest_id = self.request.query_params.get("guest_id")
        if guest_id:
            return ChatSession.objects.filter(user_id_str=guest_id).order_by("-last_message_time")

        return ChatSession.objects.none()

    def perform_update(self, serializer):
        instance = serializer.save()
        if self.request.data.get("unreadAdminCount") == 0 or self.request.data.get("unread_admin_count") == 0:
            instance.unread_admin_count = 0
            instance.save(update_fields=["unread_admin_count", "updated_at"])
        if self.request.data.get("unreadUserCount") == 0 or self.request.data.get("unread_user_count") == 0:
            instance.unread_user_count = 0
            instance.save(update_fields=["unread_user_count", "updated_at"])


@method_decorator(csrf_exempt, name='dispatch')
class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        session_id = self.request.query_params.get("session_id")
        if session_id:
            return ChatMessage.objects.filter(session_id=session_id).order_by("timestamp")
        return ChatMessage.objects.none()

    def perform_create(self, serializer):
        message = serializer.save()
        session = message.session

        session.last_message = message.text
        if message.sender in ["user"]:
            session.unread_admin_count = (session.unread_admin_count or 0) + 1
        else:
            session.unread_user_count = (session.unread_user_count or 0) + 1
        session.save(update_fields=["last_message", "unread_admin_count", "unread_user_count", "last_message_time", "updated_at"])

        if message.sender == "user":
            try:
                generate_ai_response.delay(message.session.id, message.text)
            except Exception:
                pass
