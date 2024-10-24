from rest_framework import viewsets, status
from rest_framework.response import Response
from django.core.mail import send_mail
from .models import Order
from .serializers import OrderSerializer
from drfecommerce.apps.order_detail.models import OrderDetail
from drfecommerce.apps.product.models import Product
from drfecommerce.apps.cart.models import Cart, CartItem
from drfecommerce.apps.product_store.models import ProductStore
from drfecommerce.apps.product_sale.models import ProductSale
from drfecommerce.apps.store.models import Store
from drfecommerce.apps.guest.models import Guest
from drfecommerce.settings import base
from rest_framework.permissions import IsAuthenticated
from drfecommerce.apps.guest.authentication import GuestSafeJWTAuthentication
from drfecommerce.apps.my_admin.authentication import AdminSafeJWTAuthentication
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
import json
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from datetime import datetime
from drfecommerce.apps.notification.views import create_notification
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

            # Step 3: Xử lý các sản phẩm trong giỏ hàng sau khi tạo đơn hàng thành công
            #Check nếu nó nằm trong giỏ hàng thì loại bỏ nó đi
            cart = Cart.objects.filter(guest_id=guest_id).first()
            if cart:
                for detail in order_details:
                    product = get_object_or_404(Product, id=detail['product_id'])
                    store = get_object_or_404(Store, id=detail['store_id'])
                    
                    # Kiểm tra sản phẩm có trong giỏ hàng không
                    cart_item = CartItem.objects.filter(cart=cart, product=product, store=store).first()
                    if cart_item:
                        # Nếu có, loại bỏ nó ra khỏi giỏ hàng
                        cart_item.delete()
            # Step 4: Gửi thông báo đến guest
            try:
                guest = Guest.objects.get(id=guest_id)  # Lấy đối tượng guest
            except Guest.DoesNotExist:
                return Response({'Guest': 'Order not found.', "status":status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
            
            create_notification(
                guest=guest,  # Gửi đối tượng guest
                notification_type="order_update",  # Loại thông báo
                message=f"Your order #{order.id} has been placed successfully.",  # Nội dung thông báo
                related_object_id=order.id,  # Liên kết với mã đơn hàng
                url=f"/orders/{order.id}"  # URL dẫn đến đơn hàng
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

                return Response({'message': 'Payment successful and order confirmed.', "status":status.HTTP_200_OK}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Payment amount mismatch or payment failed.', "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found.', "status":status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)

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
        
    @action(detail=True, methods=['put'], url_path="cancel-order")
    def cancel_order(self, request):
        """
        order_id: id of order
        """
        order_id = request.data.get('order_id')
        try:
            # Get the order by its primary key (id)
            order = Order.objects.get(id=order_id)

            # Check if the order status is 'pending'
            if order.order_status == 'pending':
                # Update the order status to 'cancel'
                order.order_status = 'cancelled'
                order.save()
                
                guest = order.guest  # Assuming the guest is related to the order
                create_notification(
                    guest=guest,  # Gửi đối tượng guest
                    notification_type="order_update",  # Loại thông báo
                    message=f"Your order #{order.id} has been canceled.",  # Nội dung thông báo
                    related_object_id=order.id,  # Liên kết với mã đơn hàng
                    url=f"/orders/{order.id}"  # URL dẫn đến đơn hàng đã hủy
                )
            
                # Send email notification to the admin
                self.send_order_cancellation_email(order)

                return Response({
                    'message': 'Order successfully canceled.',
                    'status': status.HTTP_200_OK
                    }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Order cannot be canceled because it is not in pending status.',
                    'status': status.HTTP_400_BAD_REQUEST
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Order.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

    def send_order_cancellation_email(self, order):
        # Define email subject
        subject = f'Order #{order.id} Cancellation Notice'

        # Generate HTML message with order details and design
        html_message = render_to_string('email/order_cancellation_email.html', {'order': order})

        # Strip HTML tags for plain text version
        plain_message = strip_tags(html_message)

        # Define recipient list
        recipient_list = [base.ADMIN_EMAIL]

        # Send the email
        send_mail(
            subject,
            plain_message,  # Plain text version
            base.DEFAULT_FROM_EMAIL,
            recipient_list,
            html_message=html_message  # HTML content version
        )
        
    #get list order
    @action(detail=False, methods=['get'], url_path="get-list-orders")
    def list_orders(self, request):
        """
        Get list of orders with pagination and optional date range filtering.

        Parameters:
        - page_index: The index of the page (default is 1).
        - page_size: The number of items per page (default is 10).
        - guest_id: ID of the guest.
        - start_date: The start date to filter orders (format: YYYY-MM-DD).
        - end_date: The end date to filter orders (format: YYYY-MM-DD).
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))
        guest_id = request.GET.get('guest_id')
        start_date = request.GET.get('start_date')  # Get the start date parameter
        end_date = request.GET.get('end_date')      # Get the end date parameter

        if not guest_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Guest ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            guest = Guest.objects.get(id=guest_id)
        except Guest.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Guest not found."
            }, status=status.HTTP_404_NOT_FOUND)

        # Start building the query
        orders = Order.objects.filter(guest=guest)

        # If start_date or end_date is provided, filter orders by date range
        if start_date or end_date:
            if start_date:
                try:
                    # Parse the start date string to a date object
                    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                    orders = orders.filter(order_date__date__gte=start_date)  # Greater than or equal to start_date
                except ValueError:
                    return Response({
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": "Invalid start date format. Please use YYYY-MM-DD."
                    }, status=status.HTTP_400_BAD_REQUEST)

            if end_date:
                try:
                    # Parse the end date string to a date object
                    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                    orders = orders.filter(order_date__date__lte=end_date)  # Less than or equal to end_date
                except ValueError:
                    return Response({
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": "Invalid end date format. Please use YYYY-MM-DD."
                    }, status=status.HTTP_400_BAD_REQUEST)

        paginator = Paginator(orders, page_size)

        try:
            paginated_orders = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_orders = paginator.page(1)
        except EmptyPage:
            paginated_orders = paginator.page(paginator.num_pages)

        serializer = OrderSerializer(paginated_orders, many=True)

        return Response({
            "status": status.HTTP_200_OK,
            "message": "OK",
            "data": {
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_index": page_index,
                "page_size": page_size,
                "orders": serializer.data
            }
        }, status=status.HTTP_200_OK)
    #admin get list order and xử lí đơn hàng
    
class AdminOrderViewSet(viewsets.ViewSet):
    #api xử lí tạo đơn hàng khi mà người dùng chọn phương thức là thanh toán khi nhận hàng
    authentication_classes = [AdminSafeJWTAuthentication]
    permission_classes = [IsAuthenticated]
    #get list order
    @action(detail=False, methods=['get'], url_path="get-list-orders")
    def list_orders(self, request):
        """
        Get list of orders with pagination and optional date range filtering.

        Parameters:
        - page_index: The index of the page (default is 1).
        - page_size: The number of items per page (default is 10).
        - start_date: The start date to filter orders (format: YYYY-MM-DD).
        - end_date: The end date to filter orders (format: YYYY-MM-DD).
        - order_status: The status of the order to filter.
        - payment_method: The payment method to filter.
        - payment_status: The payment status to filter.
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))
        start_date = request.GET.get('start_date')  # Get the start date parameter
        end_date = request.GET.get('end_date')      # Get the end date parameter
        order_status = request.GET.get('order_status')  # Get order status filter
        payment_method = request.GET.get('payment_method')  # Get payment method filter
        payment_status = request.GET.get('payment_status')  # Get payment status filter
        # Start building the query
        orders = Order.objects.all()

        # If start_date or end_date is provided, filter orders by date range
        if start_date or end_date:
            if start_date:
                try:
                    # Parse the start date string to a date object
                    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                    orders = orders.filter(order_date__date__gte=start_date)  # Greater than or equal to start_date
                except ValueError:
                    return Response({
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": "Invalid start date format. Please use YYYY-MM-DD."
                    }, status=status.HTTP_400_BAD_REQUEST)

            if end_date:
                try:
                    # Parse the end date string to a date object
                    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                    orders = orders.filter(order_date__date__lte=end_date)  # Less than or equal to end_date
                except ValueError:
                    return Response({
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": "Invalid end date format. Please use YYYY-MM-DD."
                    }, status=status.HTTP_400_BAD_REQUEST)        
         # Apply filters for order status, payment method, and payment status
        if order_status:
            orders = orders.filter(order_status=order_status)
        
        if payment_method:
            orders = orders.filter(payment_method=payment_method)

        if payment_status:
            orders = orders.filter(payment_status=payment_status)
            
        paginator = Paginator(orders, page_size)

        try:
            paginated_orders = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_orders = paginator.page(1)
        except EmptyPage:
            paginated_orders = paginator.page(paginator.num_pages)

        serializer = OrderSerializer(paginated_orders, many=True)

        return Response({
            "status": status.HTTP_200_OK,
            "message": "OK",
            "data": {
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_index": page_index,
                "page_size": page_size,
                "orders": serializer.data
            }
        }, status=status.HTTP_200_OK)
    
    #admin update order
    @action(detail=False, methods=['put'], url_path="update-order-status")
    def update_order_status(self, request):
        """
        request body data:
        - order_id: ID of the order
        - order_status: new status of the order (confirm, shipped, delivered, cancelled, returned)
        """
        data = request.data
        order_id = data.get('order_id')
        new_status = data.get('order_status')
        # Nếu confirm thì trừ số lượng quantity trong product_store
        # Returned thì cộng lại quantity vào trong product_store
        # Delivered thì cập nhật lại vào phần product_sale
        # Mỗi lần cập nhật trạng thái sẽ báo mail về cho người dùng.
        
        # Validate order status
        if new_status not in ['confirmed', 'shipped', 'delivered', 'cancelled', 'returned']:
            return Response({
                "status":status.HTTP_400_BAD_REQUEST,
                "message": "Invalid order status."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the order
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"message": "Order not found.", "status":status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)

        # Handle status-specific actions
        if new_status == 'confirmed':
            # Reduce quantity from ProductStore for each order detail
            for detail in order.orderdetail_set.all():
                product_store = ProductStore.objects.get(product=detail.product, store=detail.store)
                if product_store.remaining_stock < detail.quantity:
                    return Response({
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": f"Not enough stock for product {detail.product.name}."
                        }, status=status.HTTP_400_BAD_REQUEST)
                product_store.remaining_stock -= detail.quantity
                product_store.save()

        elif new_status == 'returned':
            # Add quantity back to ProductStore
            for detail in order.orderdetail_set.all():
                product_store = ProductStore.objects.get(product=detail.product, store=detail.store)
                product_store.remaining_stock += detail.quantity
                product_store.save()

        elif new_status == 'delivered':
            # Update ProductSale with sale details
            for detail in order.orderdetail_set.all():
                ProductSale.objects.create(
                    product=detail.product,
                    store=detail.store,
                    order_detail=detail,
                    sale_price=detail.unit_price,
                    quantity_sold=detail.quantity,
                    vat=order.gst_amount,
                    shipping_cost=order.shipping_cost
                )

        # Update the order status
        order.order_status = new_status
        if order.order_status == "confirmed":
            guest = order.guest  # Assuming the guest is related to the order
            create_notification(
                guest=guest,  # Gửi đối tượng guest
                notification_type="order_update",  # Loại thông báo
                message=f"Your order #{order.id} has been confirmed by VivaFlower.",  # Nội dung thông báo
                related_object_id=order.id,  # Liên kết với mã đơn hàng
                url=f"/orders/{order.id}"  # URL dẫn đến đơn hàng đã hủy
            )
        if order.order_status == "delivered":
            guest = order.guest  # Assuming the guest is related to the order
            create_notification(
                guest=guest,  # Gửi đối tượng guest
                notification_type="order_update",  # Loại thông báo
                message=f"Your order #{order.id} has been delivered. You can rate the product quality.",  # Nội dung thông báo
                related_object_id=order.id,  # Liên kết với mã đơn hàng
                url=f"/orders/{order.id}"  # URL dẫn đến đơn hàng đã hủy
            )
            
        if order.order_status == "shipped":
            guest = order.guest  # Assuming the guest is related to the order
            create_notification(
                guest=guest,  # Gửi đối tượng guest
                notification_type="order_update",  # Loại thông báo
                message=f"Your order #{order.id} has been delivered to the carrier.",  # Nội dung thông báo
                related_object_id=order.id,  # Liên kết với mã đơn hàng
                url=f"/orders/{order.id}"  # URL dẫn đến đơn hàng đã hủy
            )
            
        order.save()
        # Send notification email
        self.send_order_status_update_email(order, new_status)

        return Response({
            "status":status.HTTP_200_OK,
            "message": f"Order status updated to {new_status}."}, status=status.HTTP_200_OK)

    def send_order_status_update_email(self, order, new_status):
        subject = f"Order #{order.id} Status Update: {new_status.capitalize()}"
        html_message = render_to_string('email/order_status_update_email.html', {
            'order': order,
            'new_status': new_status.capitalize(),
        })
        plain_message = strip_tags(html_message)
        recipient_list = [order.guest.email]

        send_mail(
            subject,
            plain_message,
            base.DEFAULT_FROM_EMAIL,
            recipient_list,
            html_message=html_message,
        )

    #admin update order
    @action(detail=False, methods=['put'], url_path="update-payment-status")
    def update_payment_status(self, request):
        """
        request body data:
        - order_id: ID of the order
        - payment_status: new status of the order (paid, unpaid)
        """
        #cập nhật trạng thái thanh toán đối với 
        data = request.data
        order_id = data.get('order_id')
        new_status = data.get('payment_status')
        # Nếu confirm thì trừ số lượng quantity trong product_store
        # Returned thì cộng lại quantity vào trong product_store
        # Delivered thì cập nhật lại vào phần product_sale
        # Mỗi lần cập nhật trạng thái sẽ báo mail về cho người dùng.
        
        # Validate order status
        if new_status not in ['paid', 'unpaid']:
            return Response({
                "status":status.HTTP_400_BAD_REQUEST,
                "message": "Invalid order status."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the order
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"message": "Order not found.", "status":status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
        
        # Update the order status
        order.payment_status = new_status
        order.save()
        
        return Response({
            "status":status.HTTP_200_OK,
            "message": f"Payment status updated to {new_status}."}, status=status.HTTP_200_OK)
        
        