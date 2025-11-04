"""
Notification API ViewSet
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from apps.notifications.models import Notification
from apps.api.serializers.notifications import NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Notifications (read-only with mark as read actions)

    Permissions:
    - Users can only see their own notifications
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Users can only see their own notifications"""
        return Notification.objects.filter(
            recipient=self.request.user
        ).order_by('-created_at')

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """
        Get only unread notifications

        GET /api/notifications/unread/
        """
        queryset = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'notifications': serializer.data
        })

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """
        Mark a single notification as read

        POST /api/notifications/{id}/mark-read/
        """
        notification = self.get_object()

        if notification.is_read:
            return Response(
                {'message': 'Notification already marked as read'},
                status=status.HTTP_200_OK
            )

        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()

        serializer = self.get_serializer(notification)
        return Response({
            'message': 'Notification marked as read',
            'data': serializer.data
        })

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """
        Mark all notifications as read

        POST /api/notifications/mark-all-read/
        """
        unread_count = self.get_queryset().filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )

        return Response({
            'message': f'Marked {unread_count} notification(s) as read',
            'count': unread_count
        })

    @action(detail=True, methods=['delete'])
    def delete_notification(self, request, pk=None):
        """
        Delete a notification

        DELETE /api/notifications/{id}/delete-notification/
        """
        notification = self.get_object()
        notification.delete()

        return Response(
            {'message': 'Notification deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get notification statistics

        GET /api/notifications/stats/
        """
        queryset = self.get_queryset()
        total = queryset.count()
        unread = queryset.filter(is_read=False).count()

        return Response({
            'total': total,
            'unread': unread,
            'read': total - unread,
        })
