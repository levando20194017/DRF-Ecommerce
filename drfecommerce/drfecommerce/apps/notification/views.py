from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer
from drfecommerce.apps.order_detail.models import OrderDetail
from drfecommerce.apps.product.models import Product
from drfecommerce.apps.guest.models import Guest
from rest_framework.permissions import IsAuthenticated
from drfecommerce.apps.guest.authentication import GuestSafeJWTAuthentication
from drfecommerce.apps.my_admin.authentication import AdminSafeJWTAuthentication
from rest_framework.decorators import action
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger

def create_notification(
    guest, notification_type, message, 
    related_object_id=None, url=None, attachment_url = None, total_cost = 0, image = None ):
    """
    Hàm tiện ích để tạo thông báo
    :param recipient: Người nhận thông báo (Guest)
    :param notification_type: Loại thông báo (str)
    :param message: Nội dung thông báo (str)
    :param related_object_id: ID của đối tượng liên quan, ví dụ: Review, Order (int)
    :param url: URL dẫn đến đối tượng liên quan (str)
    :attachment_url: đính kèm thêm ví dụ như link ảnh
    :return: None
    """
    Notification.objects.create(
        guest=guest,
        notification_type=notification_type,
        message=message,
        related_object_id=related_object_id,
        url=url,
        attachment_url = attachment_url,
        total_cost = total_cost,
        image = image
    )

class NotificationViewSet(viewsets.ViewSet):
    authentication_classes = [GuestSafeJWTAuthentication]
    permission_classes = [IsAuthenticated]
    @action(detail=False, methods=['get'], url_path="get-list-notifications")
    def list_notifications(self, request):
        """
        query_params:
        - guest_id: id of guest
        - page_index: The index of the page (default is 1).
        - page_size: The number of items per page (default is 10).
        """
        guest_id = request.GET.get('id')
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))
        if not guest_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Guest ID is required."
            })

        try:
            guest = Guest.objects.get(id=guest_id)
        except Guest.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Guest not found."
            })
            
        notifications = Notification.objects.filter(guest=guest).order_by("-created_at")
        
        paginator = Paginator(notifications, page_size)

        try:
            paginated_notifications = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_notifications = paginator.page(1)
        except EmptyPage:
            paginated_notifications = paginator.page(paginator.num_pages)
            
        serializer = NotificationSerializer(paginated_notifications, many=True)
        
        return Response({
            "status": status.HTTP_200_OK,
            "message": "OK",
            "data": {
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_index": page_index,
                "page_size": page_size,
                "notifications": serializer.data
            }
        }, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['put'], url_path="read-notification")
    def read_notification(self, request):
        """
        request body:
        - noti_id: id of notification
        """
        noti_id = request.data.get('noti_id')
        
        if not noti_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Noti ID is required."
            })

        try:
            noti = Notification.objects.get(id=noti_id)
        except Notification.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Notification not found."
            })
            
        if not noti.is_read:
            noti.is_read = True
        
        noti.save()
        
        return Response({
            "status": status.HTTP_200_OK,
            "message": "Seen this notification",
        }, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['get'], url_path="count-unread")
    def count_unread_notifications(self, request):
        """
        API đếm số thông báo chưa đọc.
        """
        guest_id = request.GET.get('id')
        notification = Notification.objects.filter(guest_id=guest_id, is_read = False)
        unread_count = notification.count()
        return Response({
            "status": status.HTTP_200_OK,
            "message": "Counted unread notifications.",
            "unread_count": unread_count
        }, status=status.HTTP_200_OK)