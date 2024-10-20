from rest_framework import viewsets, status
from rest_framework.response import Response
from django.core.mail import send_mail
from django.utils import timezone
from .models import Order
from .serializers import OrderSerializer
from drfecommerce.apps.order_detail.serializers import OrderDetailSerializer
from drfecommerce.apps.payment.serializers import PaymentSerializer
from drfecommerce.apps.order_detail.models import OrderDetail
from drfecommerce.apps.product.models import Product
from drfecommerce.apps.store.models import Store
from drfecommerce.apps.payment.models import Payment
from drfecommerce.settings import base
from rest_framework.permissions import IsAuthenticated, AllowAny
from drfecommerce.apps.guest.authentication import GuestSafeJWTAuthentication
from rest_framework.decorators import action,permission_classes

class OrderViewSet(viewsets.ViewSet):
    #api xử lí tạo đơn hàng khi mà người dùng chọn phương thức là thanh toán khi nhận hàng
    @action(detail=False, methods=['post'], url_path="create-new-order")
    def create_new_order(self, request):
        # Step 1: Tạo đơn hàng
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            order = serializer.save()

            # Step 2: Tạo các mục chi tiết đơn hàng (OrderDetail)
            order_details = request.data.get('order_details', [])
            total_cost = 0
            for detail in order_details:
                product = Product.objects.get(id=detail['product_id'])
                quantity = detail['quantity']
                unit_price = product.price  # lấy giá từ Product model
                total_cost += unit_price * quantity  # tính tổng giá

                # Tạo OrderDetail
                OrderDetail.objects.create(
                    order=order,
                    product_id=detail['product_id'],
                    store_id=detail['store_id'],
                    product_name=detail['product_name'],
                    quantity=detail['quantity'],
                    unit_price=unit_price,
                    location_pickup=detail['location_pickup']
                )

            # Step 3: Lưu total_cost vào order
            order.total_cost = total_cost
            order.save()

            # Bắt đầu quá trình thanh toán nếu thanh toán trực tuyến
            payment_method = serializer.data['payment_method']
            if payment_method == 'e_wallet':
                return self.redirect_to_payment_gateway(order)
            elif payment_method == 'cash_on_delivery':
                self.send_order_email_to_admin(order)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def redirect_to_payment_gateway(self, order):
        # Bước 1: Lấy thông tin cần thiết cho yêu cầu thanh toán
        payment_data = {
            "amount": order.total_cost,  # Số tiền cần thanh toán
            "order_id": order.id,
            # Các thông tin cần thiết khác
        }

        # Bước 2: Gửi yêu cầu POST đến PayPal hoặc Momo API
        paypal_url = "https://api.sandbox.paypal.com/v1/payments/payment"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer <Access-Token>"  # Thay Access-Token bằng token nhận được từ PayPal
        }
        
        # Dữ liệu để tạo thanh toán trên PayPal
        data = {
            "intent": "sale",
            "redirect_urls": {
                "return_url": "https://your-backend-url.com/payment-success",
                "cancel_url": "https://your-backend-url.com/payment-cancel"
            },
            "payer": {
                "payment_method": "paypal"
            },
            "transactions": [{
                "amount": {
                    "total": str(order.total_cost),
                    "currency": "USD"
                },
                "description": f"Order #{order.id} payment"
            }]
        }
        
        # Bước 3: Gửi yêu cầu đến PayPal API
        response = requests.post(paypal_url, json=data, headers=headers)
        response_data = response.json()
        
        # Bước 4: Kiểm tra phản hồi và lấy link thanh toán
        if response.status_code == 201:
            for link in response_data['links']:
                if link['rel'] == 'approval_url':
                    payment_url = link['href']
                    return Response({'redirect_url': payment_url, 'amount': order.total_cost}, status=status.HTTP_302_FOUND)
        else:
            return Response({'error': 'Payment failed'}, status=status.HTTP_400_BAD_REQUEST)
        
    def payment_callback(self, request):
        # Nhận thông tin từ cổng thanh toán (giả sử cổng thanh toán gọi callback tới endpoint này)
        transaction_data = request.data
        order_id = transaction_data.get('order_id')
        paid_amount = transaction_data.get('amount')  # Số tiền người dùng đã thanh toán
        payment_status = transaction_data.get('status')  # Trạng thái thanh toán

        try:
            order = Order.objects.get(id=order_id)

            # Kiểm tra nếu số tiền thanh toán có khớp với total_cost
            if paid_amount == order.total_cost and payment_status == 'success':
                # Cập nhật trạng thái thanh toán của đơn hàng
                order.payment_status = 'paid'
                order.order_status = 'confirmed'
                order.save()

                # Gửi email xác nhận
                self.send_order_email_to_admin(order)

                return Response({'message': 'Payment successful and order confirmed.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Payment amount mismatch or payment failed.'}, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

    def send_order_email_to_admin(self, order):
        # Gửi email với thông tin order cho admin
        subject = f"New Order #{order.id} - {order.recipient_name}"
        message = f"""
        Order ID: {order.id}
        Recipient Name: {order.recipient_name}
        Phone: {order.recipient_phone}
        Total Cost: {order.total_cost}
        Payment Method: {order.payment_method}
        Shipping Address: {order.shipping_address}
        """
        recipient_list = [base.ADMIN_EMAIL]
        send_mail(subject, message, base.DEFAULT_FROM_EMAIL, recipient_list)

        # Log sending email
        print(f"Email sent to admin: {base.ADMIN_EMAIL} for Order {order.id}")