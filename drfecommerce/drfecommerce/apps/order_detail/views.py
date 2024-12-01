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
    serializer_class = OrderDetailSerializer
    authentication_classes = [AdminSafeJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path="get-order-detail")
    def get_order_detail(self, request):
        """
        Get order details including total_cost, list of products with location and quantity.
        Parameters:
        - order_id: ID of the order
        """
        order_id = request.GET.get('id')

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

        # Get the related order details
        order_details = OrderDetail.objects.filter(order=order)
        if not order_details.exists():
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Order detail not found."
            })

        # Serialize order and order details
        order_data = {
            "id": order.id,
            "total_cost": order.total_cost,
            "shipping_cost": order.shipping_cost,
            "gst_amount": order.gst_amount,
            "order_status": order.order_status,
            "payment_method": order.payment_method,
            "payment_status": order.payment_status,
            "order_date": order.order_date,
            "guest_first_name": order.guest.first_name,
            "guest_last_name": order.guest.last_name,
            "guest_email": order.guest.email,
            "guest_phone_number": order.guest.phone_number,
            "guest_address": order.guest.address,
            "recipient_name": order.recipient_name,
            "recipient_phone": order.recipient_phone,
            "shipping_address": order.shipping_address,
            "guest_city": order.guest.city,
            "guest_country": order.guest.country,
            "details": []
        }
        
        for detail in order_details:
            order_data["details"].append({
                "product_name": detail.product_name,
                "product_image": detail.product.image,
                "product_color": detail.product.color,
                "product_type": detail.product.product_type,
                "product_launch_date": detail.product.launch_date,
                "promotion_name": detail.product.promotion.name if detail.product.promotion else "",
                "promotion_rate": detail.product.promotion.rate if detail.product.promotion else "",
                "catalog_name": detail.product.catalog.name,
                "product_code": detail.product_code,
                "location_pickup": detail.location_pickup,
                "quantity": detail.quantity,
                "unit_price": detail.unit_price
            })

        return Response({
            "status": status.HTTP_200_OK,
            "data": order_data
        }, status=status.HTTP_200_OK)