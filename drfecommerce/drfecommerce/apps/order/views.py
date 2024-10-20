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
from drfecommerce.apps.product_store.models import ProductStore
from drfecommerce.apps.store.models import Store
from drfecommerce.apps.guest.models import Guest
from drfecommerce.apps.payment.models import Payment
from drfecommerce.settings import base
from rest_framework.permissions import IsAuthenticated, AllowAny
from drfecommerce.apps.guest.authentication import GuestSafeJWTAuthentication
from rest_framework.decorators import action,permission_classes
from django.shortcuts import get_object_or_404
import json
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class OrderViewSet(viewsets.ViewSet):
    #api xử lí tạo đơn hàng khi mà người dùng chọn phương thức là thanh toán khi nhận hàng
    authentication_classes = [GuestSafeJWTAuthentication]
    permission_classes = [IsAuthenticated]
    @action(detail=False, methods=['post'], url_path="create-new-order")
    def create_new_order(self, request, *args, **kwargs):
        # Step 1: Tạo đơn hàng
        """
        request body data
        - guest_id
        - order_details (array has object such as [{
            store_id: int,
            product_id: int
            quantity: int
        }])
        - payment_methods: option select
        - shipping_cost (tạm thời là 0)
        - gst_amount (tạm thời là 0)
        - shipping_address: string
        - recipient_phone: string
        - recipient_name: string
        """
        data = request.data.copy()
        guest_id = data.get('guest_id')
        gst_amount = float(data['gst_amount'])  # Chuyển đổi gst_amount sang số
        shipping_cost = float(data['shipping_cost'])  # Chuyển đổi shipping_cost sang số
        # Nhận order_details dưới dạng chuỗi
        order_details_str = data.get('order_details', [])

        # Kiểm tra xem order_details có phải là chuỗi không
        if isinstance(order_details_str, str):
            try:
                # Chuyển đổi chuỗi JSON thành danh sách
                order_details = json.loads(order_details_str)
            except json.JSONDecodeError:
                return Response({"message": "Invalid JSON format for order details."}, status=status.HTTP_400_BAD_REQUEST)
        elif isinstance(order_details_str, list):
            order_details = order_details_str  # Nếu đã là list thì dùng trực tiếp
        else:
            return Response({"message": "Invalid data type for order details."}, status=status.HTTP_400_BAD_REQUEST)
        if not order_details:
            return Response({"message": "Order details are required."}, status=status.HTTP_400_BAD_REQUEST)

        total_cost = 0
        
        for detail in order_details:
            quantity = detail['quantity']
            #cần check thêm ở chỗ product_store. Nếu sản phẩm còn hàng thì cho vào
            product = get_object_or_404(Product, id=int(detail['product_id']))
            store = get_object_or_404(Store, id=detail['store_id'])
            
            # Kiểm tra số lượng tồn kho
            product_store = get_object_or_404(ProductStore, product=product, store=store)
            if product_store.remaining_stock < quantity:
                return Response({"message": f"Not enough stock for {product.name}. Available: {product_store.remaining_stock}"}, status=status.HTTP_400_BAD_REQUEST)

            if quantity <= 0:
                return Response({"message": "Quantity must be greater than zero."}, status=status.HTTP_400_BAD_REQUEST)

            product = get_object_or_404(Product, id=int(detail['product_id']))
            unit_price = product.price
            total_cost += unit_price * quantity
        #chỗ này cần xem lại gst_amount với shipping_cost (cái này không thể tự truyền lên được)
        total_cost += total_cost * gst_amount + shipping_cost

        data['total_cost'] = total_cost
        # data['payment_methods'] = "cash_on_delivery"

        # guest = get_object_or_404(Guest, id=guest_id)
        data['guest'] = guest_id
        
        serializer = OrderSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            order = serializer.save()

            # Step 2: Create OrderDetails
            for detail in order_details:
                product = get_object_or_404(Product, id=detail['product_id'])
                store = get_object_or_404(Store, id=detail['store_id'])
                quantity = detail['quantity']
                unit_price = product.price
                
                OrderDetail.objects.create(
                    order=order,
                    product=product,
                    store=store,
                    product_code=product.code,
                    product_name=product.name,
                    quantity=quantity,
                    unit_price=unit_price,
                    location_pickup=store.address
                )

            # Handle payment processing
            payment_method = data['payment_methods']
            if payment_method == "e_wallet":
                return self.redirect_to_payment_gateway(order)
            elif payment_method == "cash_on_delivery":
                self.send_order_email_to_admin(order)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def redirect_to_payment_gateway(self, order, *args, **kwargs):
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
        
    def payment_callback(self, request, *args, **kwargs):
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

    def send_order_email_to_admin(self, order, *args, **kwargs):
        # Gửi email với thông tin order cho admin
        subject = f"New order #{order.id} - {order.recipient_name}"

        # Lấy chi tiết đơn hàng từ OrderDetail liên kết với Order
        order_details_html = ""
        order_details = OrderDetail.objects.filter(order=order)

        # Lặp qua các chi tiết của đơn hàng và thêm chúng vào bảng HTML
        for detail in order_details:
            order_details_html += f"""
            <tr>
                <td>{detail.product_name}</td>
                <td>{detail.quantity}</td>
                <td>{detail.unit_price} VND</td>
                <td>{detail.location_pickup}</td>
            </tr>
            """

        # Tạo nội dung HTML cho email
        html_message = f"""
        <html>
            <body>
                <h2 style="color: #1a73e8;">You have a new order from {order.recipient_name}</h2>
                <p><strong>Order ID:</strong> {order.id}</p>
                <p><strong>Recipient Name:</strong> {order.recipient_name}</p>
                <p><strong>Phone:</strong> {order.recipient_phone}</p>
                <p><strong>Shipping Cost:</strong> <span style="color: red;">{order.shipping_cost} VND</span></p>
                <p><strong>GST amount:</strong> <span style="color: red;">{order.gst_amount} VND</span></p>
                <p><strong>Total Cost:</strong> <span style="color: red;">{order.total_cost} VND</span></p>
                <p><strong>Payment Method:</strong> {order.payment_method}</p>
                <p><strong>Shipping Address:</strong> {order.shipping_address}</p>

                <h3>Order Details</h3>
                <table border="1" cellpadding="5" cellspacing="0">
                    <thead>
                        <tr>
                            <th>Product Name</th>
                            <th>Quantity</th>
                            <th>Unit Price</th>
                            <th>Location Pickup</th>
                        </tr>
                    </thead>
                    <tbody>
                        {order_details_html}
                    </tbody>
                </table>

                <br>
                <p style="color: green;">Please confirm your order now!</p>
            </body>
        </html>
        """

        # Tạo nội dung văn bản thuần từ HTML để đảm bảo email vẫn hiển thị ở dạng text nếu cần
        plain_message = strip_tags(html_message)

        # Danh sách người nhận
        recipient_list = [base.ADMIN_EMAIL]

        # Gửi email
        send_mail(
            subject,
            plain_message,  # Nội dung thuần
            base.DEFAULT_FROM_EMAIL,
            recipient_list,
            html_message=html_message  # Nội dung HTML
        )

        # Log gửi email
        print(f"Email sent to admin: {base.ADMIN_EMAIL} for Order {order.id}")
