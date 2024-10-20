from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem
from drfecommerce.apps.product.models import Product
from drfecommerce.apps.guest.models import Guest
from drfecommerce.apps.store.models import Store
from .serializers import CartSerializer, CartItemSerializer
from drfecommerce.apps.guest.authentication import GuestSafeJWTAuthentication
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger

class CartViewSet(viewsets.ViewSet):
    authentication_classes = [GuestSafeJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='create-cart')
    def create_cart(self, request):
        """
        Create a new cart for the authenticated user.
        - id: guest_id int
        """
        guest_id = request.data.get(id)
        if not guest_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Promotion ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try: 
            guest = Guest.objects.get(id = guest_id)
        except Guest.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Guest not found."
            }, status=status.HTTP_404_NOT_FOUND)
        
        cart = Cart.objects.create(guest=guest)
        cart.save()
        return Response({
            "status": status.HTTP_201_CREATED,
            "message": "Cart created successfully!",
            "data": {
                "id": cart.id,
                "guest": cart.guest.id,
            }
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='my-cart')
    def get_cart_items(self, request):
        """
        Get all items in the user's cart.
        """        
        guest_id = request.data.get('id')
        if not guest_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Guest ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try: 
            guest = Guest.objects.get(id = guest_id)
        except Guest.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Guest not found."
            }, status=status.HTTP_404_NOT_FOUND)
        cart, created = Cart.objects.get_or_create(guest=guest)

        serializer = CartSerializer(cart)
        return Response({
            "status": status.HTTP_200_OK,
            "message": "Cart retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='add-to-cart')
    def add_to_cart(self, request):
        """
        Add a product to the user's cart.
        Required body data:
        - id: guest_id int
        - store_id: id of store
        - product_id: int
        - quantity: int (optional, default=1)
        """
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        guest_id = request.data.get('id')
        store_id = request.data.get('store_id')
        
        try: 
            guest = Guest.objects.get(id = guest_id)
        except Guest.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Guest not found."
            }, status=status.HTTP_404_NOT_FOUND)
            
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Product not found."
            }, status=status.HTTP_404_NOT_FOUND)
            
        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Store not found."
            }, status=status.HTTP_404_NOT_FOUND)
            
        # Kiểm tra nếu giỏ hàng đã tồn tại, nếu không sẽ tạo giỏ hàng mới
        cart, created = Cart.objects.get_or_create(guest=guest)
        # Kiểm tra nếu sản phẩm đã có trong giỏ hàng, nếu có thì cập nhật số lượng
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, store = store)

        if not created:
            # Nếu sản phẩm đã có trong giỏ hàng, tăng số lượng sản phẩm
            # If item already exists in the cart, update the quantity
            cart_item.quantity += quantity
            cart_item.save()
        else:
            cart_item.quantity = quantity
            cart_item.save()

        return Response({
            "status": status.HTTP_201_CREATED,
            "message": "Product added to cart successfully.",
            "data": CartItemSerializer(cart_item).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='update-cart-item')
    def update_cart_item(self, request):
        """
        Update the quantity of a product in the user's cart.
        Required body data:
        - id: guest_id int
        - cart_item_id: int
        - quantity: int
        """

        cart_item_id = request.data.get('cart_item_id')
        quantity = request.data.get('quantity')
        guest_id = request.data.get('id')
            
        try: 
            guest = Guest.objects.get(id = guest_id)
        except Guest.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Guest not found."
            }, status=status.HTTP_404_NOT_FOUND)
            
        cart = Cart.objects.get(guest=guest)
        
        try:
            cart_item = CartItem.objects.get(id=cart_item_id, cart=cart)
            if quantity <= 0:
                cart_item.delete()
                return Response({
                    "status": status.HTTP_204_NO_CONTENT,
                    "message": "Cart item removed successfully."
                }, status=status.HTTP_204_NO_CONTENT)
            cart_item.quantity = quantity
            cart_item.save()
            return Response({
                "status": status.HTTP_200_OK,
                "message": "Cart item updated successfully.",
                "data": CartItemSerializer(cart_item).data
            }, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Cart item not found."
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], url_path='remove-cart-item')
    def remove_cart_item(self, request):
        """
        Remove a product from the user's cart.
        Required body data:
        - cart_item_id: int
        - id: guest_id int
        """

        cart_item_id = request.data.get('cart_item_id')
        guest_id = request.data.get('id')
            
        try: 
            guest = Guest.objects.get(id = guest_id)
        except Guest.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Guest not found."
            }, status=status.HTTP_404_NOT_FOUND)
            
        cart = Cart.objects.get(guest=guest)
        
        try:
            cart_item = CartItem.objects.get(id=cart_item_id, cart=cart)
            cart_item.delete()
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "Cart item removed successfully."
            }, status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Cart item not found."
            }, status=status.HTTP_404_NOT_FOUND)

    # @action(detail=False, methods=['get'], url_path='get-cart-items')
    # def get_cart_items(self, request):
    #     """
    #     Retrieve all items in a cart by cart_id with pagination.
        
    #     Parameters:
    #     - guest_id: ID of the guest
    #     - page_index: The index of the page (default is 1).
    #     - page_size: The number of items per page (default is 10).
    #     """
    #     guest_id = request.query_params.get('guest_id')
    #     if not guest_id:
    #         return Response({
    #             "status": status.HTTP_400_BAD_REQUEST,
    #             "message": "Guest ID is required."
    #         }, status=status.HTTP_400_BAD_REQUEST)
            
    #     try:
    #         cart = Cart.objects.get(guest_id = guest_id)
    #     except Cart.DoesNotExist:
    #         return Response({
    #             "status": status.HTTP_404_NOT_FOUND,
    #             "message": "Cart not found."
    #         }, status=status.HTTP_404_NOT_FOUND)

    #     # Pagination settings
    #     page_index = int(request.GET.get('page_index', 1))
    #     page_size = int(request.GET.get('page_size', 10))

    #     # Get all cart items for the cart
    #     cart_items = CartItem.objects.filter(cart=cart)

    #     # Paginate the cart items
    #     paginator = Paginator(cart_items, page_size)

    #     try:
    #         paginated_items = paginator.page(page_index)
    #     except PageNotAnInteger:
    #         paginated_items = paginator.page(1)
    #     except EmptyPage:
    #         paginated_items = paginator.page(paginator.num_pages)

    #     # Serialize the data
    #     serializer = CartItemSerializer(paginated_items, many=True)

    #     return Response({
    #         "status": status.HTTP_200_OK,
    #         "message": "OK",
    #         "data": {
    #             "total_pages": paginator.num_pages,
    #             "total_items": paginator.count,
    #             "page_index": page_index,
    #             "page_size": page_size,
    #             "cart_items": serializer.data
    #         }
    #     }, status=status.HTTP_200_OK)