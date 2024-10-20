from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Product
from drfecommerce.apps.my_admin.models import MyAdmin
from drfecommerce.apps.catalog.models import Catalog
from drfecommerce.apps.promotion.models import Promotion
from .serializers import ProductSerializer
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from rest_framework.permissions import IsAuthenticated, AllowAny
from drfecommerce.apps.my_admin.authentication import AdminSafeJWTAuthentication
from rest_framework.decorators import action,permission_classes
from dotenv import load_dotenv
from django.utils import timezone
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from drfecommerce.settings import base

# Load environment variables from .env file
load_dotenv()
# Create your views here.
class ProductViewSet(viewsets.ViewSet):
    authentication_classes = [AdminSafeJWTAuthentication]
    permission_classes = [IsAuthenticated]
    @action(detail=False, methods=['get'], url_path="get-list-products")
    def list_products(self, request):
        """
        API to get list of products with pagination.
        - page_index (default=1)
        - page_size (default=10)
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))

        products = Product.objects.all()
        paginator = Paginator(products, page_size)

        try:
            paginated_products = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_products = paginator.page(1)
        except EmptyPage:
            paginated_products = paginator.page(paginator.num_pages)

        serializer = ProductSerializer(paginated_products, many=True)

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

    @action(detail=False, methods=['get'], url_path="search-products")
    def search_products(self, request):
        """
        API to search products by name with pagination.
        - page_index (default=1)
        - page_size (default=10)
        - name: product name to search
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))
        name_query = request.GET.get('name', '').strip()

        # Lọc sản phẩm theo tên
        products = Product.objects.filter(name__icontains=name_query)

        paginator = Paginator(products, page_size)

        try:
            paginated_products = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_products = paginator.page(1)
        except EmptyPage:
            paginated_products = paginator.page(paginator.num_pages)

        serializer = ProductSerializer(paginated_products, many=True)

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
        
    @action(detail=False, methods=['post'], url_path="create-product")
    def create_product(self, request):
        """
        API to create a new product.
        - admin_id: int
        - catalog_id: int
        - promotion_id: int allow null
        - sku: string (max_length: 50)
        - code: string (max_length: 50)
        - part_number: string (max_length: 50)
        - name: string (max_length: 255)
        - short_description: string (max_length: 255)
        - description: string (text_filed)
        - product_type: string (text_filed)
        - price: float
        - member_price: float
        - quantity: int
        - image: string (max_length: 255)
        - gallery: string (text_filed)
        - weight: float
        - diameter: float
        - dimensions: string (max_length: 255)
        - material: string (max_length: 255)
        - label: string (max_length: 255)
        """
        data = request.data
        try:
            admin = MyAdmin.objects.get(id=data['admin_id'])
            catalog = Catalog.objects.get(id=data['catalog_id'])
            promotion = Promotion.objects.get(id=data['promotion_id']) if data.get('promotion_id') else None

            product = Product.objects.create(
                admin=admin,
                catalog=catalog,
                promotion=promotion,
                code=data['code'],
                name=data['name'],
                short_description=data['short_description'],
                description=data['description'],
                product_type=data['product_type'],
                price=data['price'],
                member_price=data['member_price'],
                quantity=data['quantity'],
                image=data['image'],
                gallery=data['gallery'],
                weight=data['weight'],
                diameter=data['diameter'],
                dimensions=data['dimensions'],
                material=data['material'],
                label=data['label']
            )
            product.save()

            return Response({
                "status": status.HTTP_201_CREATED,
                "message": "Product created successfully!",
                "data": ProductSerializer(product).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": f"Error: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
            
    @action(detail=False, methods=['put'], url_path="edit-product")
    def edit_product(self, request):
        """
        API to edit an existing product.
        - id: integer
        - sku: string (max_length: 50)
        - code: string (max_length: 50)
        - part_number: string (max_length: 50)
        - name: string (max_length: 255)
        - short_description: string (max_length: 255)
        - description: string (text_filed)
        - product_type: string (text_filed)
        - price: float
        - member_price: float
        - quantity: int
        - image: string (max_length: 255)
        - gallery: string (text_filed)
        - weight: float
        - diameter: float
        - dimensions: string (max_length: 255)
        - material: string (max_length: 255)
        - label: string (max_length: 255)
        """
        data = request.data
        product_id = data.get('id')
        try:
            product = Product.objects.get(id=product_id)
            promotion = Promotion.objects.get(id=data['promotion_id']) if data.get('promotion_id') else None
            product.promotion = promotion
            if data['sku']:
                product.sku = data['sku']
            if data['code']:
                product.code = data['code']
            if data['part_number']:
                product.part_number = data['part_number']
            if data['name']:
                product.name = data['name']
            if data['short_description']:
                product.short_description = data['short_description']
            if data['description']:
                product.description = data['description']
            if data['product_type']:
                product.product_type = data['product_type']
            if data['price']:
                product.price = data['price']
            if data['member_price']:
                product.member_price = data['member_price']
            if data['quantity']:
                product.quantity = data['quantity']
            if data['image']:
                product.image = data['image']
            if data['gallery']:
                product.gallery = data['gallery']
            if data['weight']:
                product.weight = data['weight']
            if data['diameter']:
                product.diameter = data['diameter']
            if data['dimensions']:
                product.dimensions = data['dimensions']
            if data['material']:
                product.material = data['material']
            if data['label']:
                product.label = data['label']
            product.save()

            return Response({
                "status": status.HTTP_200_OK,
                "message": "Product updated successfully!",
                "data": ProductSerializer(product).data
            }, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Product not found."
            }, status=status.HTTP_404_NOT_FOUND)
        except Promotion.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Promotion not found."
            }, status=status.HTTP_404_NOT_FOUND)
                     
    @action(detail=False, methods=['delete'], url_path="delete-product")
    def delete_product(self, request):
        """
        API to soft delete a product.
        - query_params: id
        """
        product_id = request.query_params.get('id')
        if not product_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Product ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
            product.delete_at = timezone.now()  # Soft delete by setting the delete_at field
            product.save()

            return Response({
                "status": status.HTTP_200_OK,
                "message": "Product soft deleted successfully."
            }, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Product not found."
            }, status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=False, methods=['put'], url_path="restore-product")
    def restore_product(self, request):
        """
        Restore a product: body data:
        - id
        """
        product_id = request.data.get('id')
        
        if not product_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Product ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Tìm product bị xóa mềm (tức là có delete_at không null)
            product = Product.objects.get(id=product_id, delete_at__isnull=False)
        except Product.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Product not found or already restored."
            }, status=status.HTTP_404_NOT_FOUND)
        # Khôi phục catalog và các catalog con của nó
        product.delete_at = None
        product.save() 
        return Response({
            "status": status.HTTP_200_OK,
            "message": "Product restored successfully."
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path="upload-gallery")
    def upload_gallery(self, request):
        """
        form-data: files
        """
        if 'files' not in request.FILES:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "No image files found in request."
            }, status=status.HTTP_400_BAD_REQUEST)

        files = request.FILES.getlist('files')  # Lấy danh sách các file từ request
        image_urls = []  # Danh sách lưu URL của các ảnh đã upload

        for image in files:
            img_name = image.name

            # Sử dụng default_storage để lưu ảnh vào thư mục cục bộ hoặc dịch vụ lưu trữ khác trong tương lai
            save_path = os.path.join(base.MEDIA_ROOT, img_name)
            file_path = default_storage.save(save_path, ContentFile(image.read()))
            file_url = default_storage.url(file_path)

            # Lưu URL của ảnh vào danh sách
            image_urls.append(file_url)

        return Response({
            "status": status.HTTP_200_OK,
            "message": "Images uploaded successfully!",
            "image_urls": image_urls  # Trả về danh sách các URL của ảnh đã upload
        }, status=status.HTTP_200_OK)
        
@permission_classes([AllowAny])
class PublicProductViewset(viewsets.ViewSet):
    @action(detail=False, methods=['get'], url_path="get-list-products")
    def list_products(self, request):
        """
        API to get list of products with pagination.
        - page_index (default=1)
        - page_size (default=10)
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))

        products = Product.objects.filter(delete_at__isnull=True)
        paginator = Paginator(products, page_size)

        try:
            paginated_products = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_products = paginator.page(1)
        except EmptyPage:
            paginated_products = paginator.page(paginator.num_pages)

        serializer = ProductSerializer(paginated_products, many=True)

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
        
    @action(detail=False, methods=['get'], url_path="get-detail-product")
    def get_product(self, request):
        """
        Get product details:
        - query_params: id
        """
        product_id = request.query_params.get('id')
        if not product_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Product ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
            serializer = ProductSerializer(product)
            return Response({
                "status": status.HTTP_200_OK,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Product not found."
            }, status=status.HTTP_404_NOT_FOUND)
            
    @action(detail=False, methods=['get'], url_path="get-list-products-by-catalog")
    def list_products_by_catalog(self, request):
        """
        API to get list of products with pagination.
        - page_index (default=1)
        - page_size (default=10)
        - catalog_id: int
        example api/get-list-products/?page_index=1&page_size=10&catalog_id=1
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))
        catalog_id = request.GET.get('catalog_id') if request.GET.get('catalog_id') else None
        
        if not catalog_id:
            return Response({
            "status": status.HTTP_200_OK,
            "message": "OK",
            "data": {
            "status": 404,
            "message": "Catalog not found"
            }})
        
        try:
            catalog = Catalog.objects.get(id = catalog_id)
            if catalog.delete_at is not None:
                return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Catalog not found."
            }, status=status.HTTP_404_NOT_FOUND)
        except Catalog.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Catalog not found."
            }, status=status.HTTP_404_NOT_FOUND)
            
        products = Product.objects.filter(catalog_id = catalog_id, delete_at__isnull=True)
        paginator = Paginator(products, page_size)
        
        try:
            paginated_products = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_products = paginator.page(1)
        except EmptyPage:
            paginated_products = paginator.page(paginator.num_pages)

        serializer = ProductSerializer(paginated_products, many=True)

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
        
    @action(detail=False, methods=['get'], url_path="get-list-products-by-promotion")
    def list_products_by_promotion(self, request):
        """
        API to get list of products with pagination.
        - page_index (default=1)
        - page_size (default=10)
        - promotion_id: int
        example api/get-list-products/?page_index=1&page_size=10&promotion_id=1
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))
        promotion_id = int(request.GET.get('promotion_id')) if request.GET.get('promotion_id') else None
        
        # xét 2 trường hợp sản phẩm được khuyễn mãi và sản phẩm không được khuyến mãi (promotion_id = null)
        if promotion_id:  
            try:
                promotion = Promotion.objects.get(id = promotion_id)
                if promotion.delete_at is not None:
                    return Response({
                    "status": status.HTTP_404_NOT_FOUND,
                    "message": "Promotion not found."
                }, status=status.HTTP_404_NOT_FOUND)
            except Promotion.DoesNotExist:
                return Response({
                    "status": status.HTTP_404_NOT_FOUND,
                    "message": "Promotion not found."
                }, status=status.HTTP_404_NOT_FOUND)
                
        products = Product.objects.filter(promotion_id = promotion_id, delete_at__isnull=True)
        paginator = Paginator(products, page_size)
            
        try:
            paginated_products = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_products = paginator.page(1)
        except EmptyPage:
            paginated_products = paginator.page(paginator.num_pages)

        serializer = ProductSerializer(paginated_products, many=True)
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
        
    @action(detail=False, methods=['get'], url_path="search-products")
    def search_products(self, request):
        """
        API to search products by name with pagination.
        - page_index (default=1)
        - page_size (default=10)
        - name: product name to search
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))
        name_query = request.GET.get('name')
        
        if name_query is None or name_query == "":
            products = Product.objects.filter(delete_at__isnull=True)
        else:
            products = Product.objects.filter(name__icontains=name_query, delete_at__isnull=True)

        paginator = Paginator(products, page_size)

        try:
            paginated_products = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_products = paginator.page(1)
        except EmptyPage:
            paginated_products = paginator.page(paginator.num_pages)

        serializer = ProductSerializer(paginated_products, many=True)

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