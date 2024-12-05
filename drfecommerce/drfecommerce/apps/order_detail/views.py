from rest_framework import viewsets
from rest_framework import viewsets, status
from rest_framework.response import Response
from drfecommerce.apps.order.serializers import OrderSerializer
from drfecommerce.apps.order.models import Order
from rest_framework.permissions import IsAuthenticated
from drfecommerce.apps.guest.authentication import GuestSafeJWTAuthentication
from rest_framework.decorators import action

class OrderDetailViewSet(viewsets.ModelViewSet):
    authentication_classes = [GuestSafeJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path="get-order-detail")
    def get_order_detail(self, request):
        """
        Get order details including total_cost, list of products with location and quantity.
        Parameters:
        - order_id: ID of the order
        """
        order_id = request.query_params.get('order_id')

        if not order_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Order ID is required."
            })

        try:
            # Get the order
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Order not found."
            })
        serializer = OrderSerializer(order)
        return Response({
            "status": status.HTTP_200_OK,
            "data": serializer.data
        }, status=status.HTTP_200_OK)