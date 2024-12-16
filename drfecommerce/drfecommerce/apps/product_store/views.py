from rest_framework import status, viewsets
from rest_framework.decorators import action, permission_classes, authentication_classes
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
from django.db.models import Sum
from django.db.models import Avg
from drfecommerce.apps.product.serializers import ProductSerializer
from drfecommerce.apps.catalog.models import Catalog
from drfecommerce.apps.review.models import Review
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

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
            return Response({"message": "Product ID is required."})
        
        try:
            product = Product.objects.get(id = product_id)
        except Product.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Product not found."
            })

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
                })
        except ProductStore.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Product not found."
            })
            
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
            })

        products = ProductStore.objects.filter(store=store).order_by('-updated_at')

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
            })

        products = ProductStore.objects.filter(store=store).order_by('-updated_at')

        # Lọc theo tên hoặc mã sản phẩm
        if product_name:
            products = products.filter(product__name__icontains=product_name)
            
        products = products.order_by('-updated_at')

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

@authentication_classes([])        
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
            return Response({"message": "Product ID is required."})
        try:
            product = Product.objects.get(id = product_id)
        except Product.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Product not found."
            })
            
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
            return Response({"message": "Product ID is required."})
        try:
            product = Product.objects.get(id = product_id)
        except Product.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Product not found."
            })
            
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
        
    @action(detail=True, methods=['get'], url_path='search-products-in-store')
    def search_products_in_store(self, request, pk=None):
        """
        API lấy danh sách các sản phẩm trong cửa hàng theo store đối với người dùng
        query_params:
        - page_index: trang (mặc định là 1)
        - page_size: số lượng sản phẩm trên mỗi trang (mặc định là 10)
        - store_id: ID của store để lọc
        - textSearch: string search theo tên sản phẩm
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))
        store_id = request.GET.get('store_id')
        name = request.GET.get('textSearch')
        
        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Store not found."
            })

        products = ProductStore.objects.filter(store=store, delete_at__isnull = True)
        
        if name: 
            products = products.filter(product__name__icontains=name)

        paginator = Paginator(products, page_size)

        try:
            paginated_products = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_products = paginator.page(1)
        except EmptyPage:
            paginated_products = paginator.page(paginator.num_pages)

        serializer = DetailProductStoreSerializer(paginated_products, many=True)

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
        
    @action(detail=False, methods=['get'], url_path='detail-of-product-and-store')
    def detail_product_store(self, request):
        """
        API lấy thông tin sản phẩm ở trong cửa hàng
        query_params:
        - product_id: ID của product để lọc
        - store_id: ID của store
        """
        product_id = request.GET.get('product_id')
        store_id = request.GET.get('store_id')

        if not product_id:
            return Response({"message": "Product ID is required."})
        if not store_id:
            return Response({"message": "Store ID is required."})
        try:
            product = Product.objects.get(id = product_id)
        except Product.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Product not found."
            })
        
        try:
            store = Store.objects.get(id = store_id)
        except Store.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Store not found."
            })
                
        detail_product = ProductStore.objects.filter(product = product, store= store)
            
        serializer = DetailProductStoreSerializer(detail_product, many=True)
        
        return Response({
            "status": status.HTTP_200_OK,
            "message": "OK",
            "data": {
                'product': serializer.data
            }
        }, status=status.HTTP_200_OK)
        
        
    @action(detail=True, methods=['get'], url_path='search-products-in-store-by-catalog')
    def search_products_in_store_by_catalog(self, request, pk=None):
        """
        API lấy danh sách các sản phẩm trong cửa hàng theo store và catalog (bao gồm catalog con).
        query_params:
        - page_index: trang (mặc định là 1)
        - page_size: số lượng sản phẩm trên mỗi trang (mặc định là 10)
        - store_id: ID của store để lọc
        - catalog_id: ID của catalog để lọc sản phẩm
        - textSearch: string search theo tên sản phẩm
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))
        store_id = request.GET.get('store_id')
        catalog_id = request.GET.get('catalog_id')
        name = request.GET.get('textSearch')

        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Store not found."
            })

        # Lấy danh sách các catalog con của catalog_id truyền vào
        catalog = Catalog.objects.get(id=catalog_id)
        
        # Hàm đệ quy lấy tất cả các catalog con
        def get_child_catalogs(parent_catalog):
            children = Catalog.objects.filter(parent_id=parent_catalog, delete_at__isnull=True)
            result = list(children)
            for child in children:
                result.extend(get_child_catalogs(child))
            return result

        all_catalogs = [catalog]
        all_catalogs.extend(get_child_catalogs(catalog))

        catalog_ids = [cat.id for cat in all_catalogs]

        # Lọc sản phẩm trong store thuộc các catalog này
        products = ProductStore.objects.filter(store=store, delete_at__isnull=True, product__catalog_id__in=catalog_ids).order_by('-updated_at')
        
        if name:
            products = products.filter(product__name__icontains=name)

        # Tính toán avg_rating cho mỗi sản phẩm
        product_data = []
        for product_store in products:
            product = product_store.product
            store = product_store.store
            
            # Tính avg_rating từ bảng ProductReview
            avg_rating = Review.objects.filter(product=product, store = store).aggregate(Avg('rating'))['rating__avg'] or 0
            
            product_serializer = ProductSerializer(product)
            product_data.append({
                "product": product_serializer.data,
                "remaining_stock": product_store.remaining_stock,
                "avg_rating": avg_rating
            })

        # Phân trang sản phẩm
        paginator = Paginator(product_data, page_size)
        try:
            paginated_products = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_products = paginator.page(1)
        except EmptyPage:
            paginated_products = paginator.page(paginator.num_pages)

        # Trả về kết quả
        return Response({
            "status": status.HTTP_200_OK,
            "message": "OK",
            "data": {
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_index": page_index,
                "page_size": page_size,
                "products": paginated_products.object_list
            }
        }, status=status.HTTP_200_OK)
        
    #api gợi ý sản phẩm, sử dụng thuật toán Collaborative filtering
    @action(detail=True, methods=['get'], url_path='recommend-products')
    def recommend_products(self, request, pk=None):
        """
        Gợi ý các sản phẩm cho người dùng trong cửa hàng dựa trên Collaborative Filtering.
        """
        guest_id = request.query_params.get('guest_id')  # Lấy guest_id từ query parameters
        store_id = request.query_params.get('store_id')  # store_id là primary key của cửa hàng từ URL
        
        if not guest_id:
            return Response({"error": "guest_id is required"}, status=400)

        # Lấy các sản phẩm mà khách hàng đã đánh giá
        reviews = Review.objects.filter(guest__id=guest_id, store__id=store_id)
        
        if not reviews.exists():
            return Response({"message": "No reviews found for this user in this store"}, status=404)

        rated_products = reviews.values_list('product', flat=True)

        # Lấy tất cả các sản phẩm trong cửa hàng
        products_in_store = ProductStore.objects.filter(store__id=store_id).values_list('product', flat=True)

        # Lấy đánh giá của tất cả sản phẩm trong cửa hàng
        product_ratings = {}
        for product in products_in_store:
            ratings = Review.objects.filter(product__id=product, store__id=store_id).values('rating')
            if ratings:
                product_ratings[product] = [rating['rating'] for rating in ratings]

        # Tạo ma trận đánh giá (rating matrix)
        product_ids = list(product_ratings.keys())
        rating_matrix = []

        for product in product_ids:
            ratings = product_ratings[product]
            row = [0] * len(product_ids)
            row[product_ids.index(product)] = np.mean(ratings)  # Giá trị trung bình cho sản phẩm
            rating_matrix.append(row)

        # Tính toán cosine similarity giữa các sản phẩm
        similarity_matrix = cosine_similarity(rating_matrix)

        # Gợi ý sản phẩm có độ tương đồng cao với các sản phẩm đã đánh giá
        recommended_products = []
        for i, product_id in enumerate(product_ids):
            if product_id not in rated_products:
                similarity_score = np.sum(similarity_matrix[i])  # Tổng độ tương đồng với các sản phẩm đã đánh giá
                recommended_products.append((product_id, similarity_score))

        # Sắp xếp theo độ tương đồng giảm dần và lấy top 5 sản phẩm
        recommended_products = sorted(recommended_products, key=lambda x: x[1], reverse=True)[:5]

        # Lấy thông tin sản phẩm gợi ý
        top_recommended_product_ids = [product for product, _ in recommended_products]
        products = Product.objects.filter(id__in=top_recommended_product_ids)
        serializer = ProductSerializer(products, many=True)

        return Response({
            "status": 200,
            "data": serializer.data
            })