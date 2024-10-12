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
from drfecommerce.apps.my_admin.authentication import SafeJWTAuthentication
from rest_framework.decorators import action,permission_classes
from dotenv import load_dotenv
from django.utils import timezone

# Load environment variables from .env file
load_dotenv()
# Create your views here.
class ProductViewSet(viewsets.ViewSet):
    authentication_classes = [SafeJWTAuthentication]
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

    @action(detail=False, methods=['post'], url_path="create-product")
    def create_product(self, request):
        """
        API to create a new product.
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
                sku=data['sku'],
                code=data['code'],
                part_number=data['part_number'],
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

            product.sku = data['sku']
            product.code = data['code']
            product.part_number = data['part_number']
            product.name = data['name']
            product.short_description = data['short_description']
            product.description = data['description']
            product.product_type = data['product_type']
            product.price = data['price']
            product.member_price = data['member_price']
            product.quantity = data['quantity']
            product.image = data['image']
            product.gallery = data['gallery']
            product.weight = data['weight']
            product.diameter = data['diameter']
            product.dimensions = data['dimensions']
            product.material = data['material']
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