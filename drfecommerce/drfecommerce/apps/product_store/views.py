from rest_framework import status, viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from drfecommerce.apps.product.models import Product
from drfecommerce.apps.store.models import Store
from .models import ProductStore
from .serializers import ProductStoreSerializer, StoreHasProductSerializer, DetailProductStoreSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from drfecommerce.apps.my_admin.authentication import AdminSafeJWTAuthentication
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger

class ProductStoreViewSet(viewsets.ModelViewSet):
    queryset = ProductStore.objects.all()
    serializer_class = ProductStoreSerializer
    authentication_classes = [AdminSafeJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='soft-delete-product-of-store')
    def soft_delete(self, request, pk=None):
        """
        Soft delete ProductIncoming and update ProductStore stock.
        Query params:
        - id (ProductIncoming ID)
        """
        product_id = request.query_params.get('product_id')

        if not product_id:
            return Response({"message": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(id = product_id)
        except Product.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Product not found."
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            # Get the ProductIncoming entry
            product_store = ProductStore.objects.get(product=product)
            if product_store.delete_at is None:
                product_store.delete_at = timezone.now()  # Đánh dấu xóa mềm
                product_store.save()
                return Response({
                    "status": status.HTTP_200_OK,
                    "message": "Product deleted successfully."
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Product has already been deleted."
                }, status=status.HTTP_400_BAD_REQUEST)
        except ProductStore.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Product not found."
            }, status=status.HTTP_404_NOT_FOUND)
            
    @action(detail=True, methods=['get'], url_path='list-products-in-store')
    def list_products_in_store(self, request, pk=None):
        """
        API lấy danh sách các sản phẩm trong cửa hàng theo store
        query_params:
        - page_index: trang (mặc định là 1)
        - page_size: số lượng sản phẩm trên mỗi trang (mặc định là 10)
        - store_id: ID của store để lọc
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))
        store_id = request.GET.get('store_id')
        
        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Store not found."
            }, status=status.HTTP_404_NOT_FOUND)

        products = ProductStore.objects.filter(store=store)

        paginator = Paginator(products, page_size)

        try:
            paginated_products = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_products = paginator.page(1)
        except EmptyPage:
            paginated_products = paginator.page(paginator.num_pages)

        serializer = ProductStoreSerializer(paginated_products, many=True)

        return Response({
            "status": status.HTTP_200_OK,
            "message": "OK",
            "data": {
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_index": page_index,
                "page_size": page_size,
                "products": serializer.data
            }
        }, status=status.HTTP_200_OK)
        
    @action(detail=True, methods=['get'], url_path='search-products-in-store')
    def search_products_in_store(self, request):
        """
        API tìm kiếm các sản phẩm trong cửa hàng theo store
        query_params:
        - page_index: trang (mặc định là 1)
        - page_size: số lượng sản phẩm trên mỗi trang (mặc định là 10)
        - store_id: ID của store để lọc
        - product_name: string (tên của sản phẩm)
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))
        product_name = request.GET.get('product_name', None)
        store_id = request.GET.get('store_id')
        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Store not found."
            }, status=status.HTTP_404_NOT_FOUND)

        products = ProductStore.objects.filter(store=store)

        # Lọc theo tên hoặc mã sản phẩm
        if product_name:
            products = products.filter(product__name__icontains=product_name)

        paginator = Paginator(products, page_size)

        try:
            paginated_products = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_products = paginator.page(1)
        except EmptyPage:
            paginated_products = paginator.page(paginator.num_pages)

        serializer = ProductStoreSerializer(paginated_products, many=True)

        return Response({
            "status": status.HTTP_200_OK,
            "message": "OK",
            "data": {
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_index": page_index,
                "page_size": page_size,
                "products": serializer.data
            }
        }, status=status.HTTP_200_OK)
        
@permission_classes([AllowAny])   
class PublicProductStoreViewSet(viewsets.ModelViewSet):
    @action(detail=False, methods=['get'], url_path='list-stores-has-product')
    def list_stores_with_product(self, request):
        """
        API lấy danh sách cửa hàng mà tại đó có bán sản phẩm => áp dụng phía người dùng
        query_params:
        - page_index: trang (mặc định là 1)
        - page_size: số lượng sản phẩm trên mỗi trang (mặc định là 10)
        - product_id: ID của product để lọc
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))
        product_id = request.GET.get('product_id')

        if not product_id:
            return Response({"message": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            product = Product.objects.get(id = product_id)
        except Product.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Product not found."
            }, status=status.HTTP_404_NOT_FOUND)
            
        stores_has_product = ProductStore.objects.filter(product = product)
            
        paginator = Paginator(stores_has_product, page_size)

        try:
            paginated_stores = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_stores = paginator.page(1)
        except EmptyPage:
            paginated_stores = paginator.page(paginator.num_pages)

        serializer = StoreHasProductSerializer(paginated_stores, many=True)
        
        return Response({
            "status": status.HTTP_200_OK,
            "message": "OK",
            "data": {
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_index": page_index,
                "page_size": page_size,
                "stores": serializer.data
            }
        }, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['get'], url_path='search-stores-has-product')
    def search_stores_by_product(self, request):
        """
        API lấy danh sách cửa hàng mà tại đó có bán sản phẩm => áp dụng phía người dùng
        query_params:
        - page_index: trang (mặc định là 1)
        - page_size: số lượng sản phẩm trên mỗi trang (mặc định là 10)
        - product_id: ID của product để lọc
        - product_name: tên của product (có thể không truyền)
        """
        
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))
        product_name = request.GET.get('product_name', None)
        product_id = request.GET.get('product_id')
        
        if not product_id:
            return Response({"message": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            product = Product.objects.get(id = product_id)
        except Product.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Product not found."
            }, status=status.HTTP_404_NOT_FOUND)
            
        stores_has_product = ProductStore.objects.filter(product = product)
        
        if product_name:
            stores_has_product = stores_has_product.filter(
                productstore__product__name__icontains=product_name
            ).distinct()

        paginator = Paginator(stores_has_product, page_size)

        try:
            paginated_stores = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_stores = paginator.page(1)
        except EmptyPage:
            paginated_stores = paginator.page(paginator.num_pages)

        serializer = StoreHasProductSerializer(paginated_stores, many=True)

        return Response({
            "status": status.HTTP_200_OK,
            "message": "OK",
            "data": {
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_index": page_index,
                "page_size": page_size,
                "stores": serializer.data
            }
        }, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['get'], url_path='detail-of-product-and-store')
    def detail_product_store(self, request):
        """
        API lấy danh sách cửa hàng mà tại đó có bán sản phẩm => áp dụng phía người dùng
        query_params:
        - product_id: ID của product để lọc
        - store_id: ID của store
        """
        product_id = request.GET.get('product_id')
        store_id = request.GET.get('store_id')

        if not product_id:
            return Response({"message": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not store_id:
            return Response({"message": "Store ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            product = Product.objects.get(id = product_id)
        except Product.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Product not found."
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            store = Store.objects.get(id = store_id)
        except Store.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Store not found."
            }, status=status.HTTP_404_NOT_FOUND)
                
        detail_product = ProductStore.objects.filter(product = product, store= store)
            
        serializer = DetailProductStoreSerializer(detail_product, many=True)
        
        return Response({
            "status": status.HTTP_200_OK,
            "message": "OK",
            "data": {
                'product': serializer.data
            }
        }, status=status.HTTP_200_OK)