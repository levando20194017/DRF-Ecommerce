from rest_framework import viewsets
from .models import OrderDetail
from .serializers import OrderDetailSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from drfecommerce.apps.guest.models import Guest
from drfecommerce.apps.order.models import Order
from rest_framework.permissions import IsAuthenticated
from drfecommerce.apps.guest.authentication import GuestSafeJWTAuthentication
from drfecommerce.apps.my_admin.authentication import AdminSafeJWTAuthentication
from rest_framework.decorators import action

class OrderDetailViewSet(viewsets.ModelViewSet):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
    authentication_classes = [GuestSafeJWTAuthentication, AdminSafeJWTAuthentication]
    permission_classes = [IsAuthenticated]
    #api view order detail
    @action(detail=False, methods=['get'], url_path="get-order-detail")
    def get_order_detail(self, request):
        """
        Parameters:
        - order_id: ID or the order
        """
        order_id = request.GET.get('order_id')

        if not order_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Order ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Order not found."
            }, status=status.HTTP_404_NOT_FOUND)
            
        try:
            order_detail = OrderDetail.objects.get(order=order)
            serializer = OrderDetailSerializer(order_detail)
            return Response({
                "status": status.HTTP_200_OK,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except OrderDetail.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Order detail not found."
            }, status=status.HTTP_404_NOT_FOUND)
            