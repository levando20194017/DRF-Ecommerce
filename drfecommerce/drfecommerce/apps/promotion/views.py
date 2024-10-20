from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Promotion
from .serializers import PromotionSerializer
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from rest_framework.permissions import IsAuthenticated, AllowAny
from drfecommerce.apps.my_admin.authentication import AdminSafeJWTAuthentication
from rest_framework.decorators import action, permission_classes
from dotenv import load_dotenv
from django.utils import timezone

# Load environment variables from .env file
load_dotenv()
# Create your views here.
class PromotionViewSet(viewsets.ViewSet):
    authentication_classes = [AdminSafeJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path="create-new-promotion")
    def create_promotion(self, request):
        """
        Create a new promotion: body data
        - name: string
        - description: string
        - code: string
        - from_date: date form yyyy-mm-dd
        - to_date: date form yyyy-mm-dd
        - special_price: float
        - member_price: float
        - rate: float
        """
        name = request.data.get('name')
        description = request.data.get('description')
        code = request.data.get('code')
        from_date = request.data.get('from_date')
        to_date = request.data.get('to_date')
        special_price = request.data.get('special_price')
        member_price = request.data.get('member_price')
        rate = request.data.get('rate')

        try:
            promotion = Promotion.objects.create(
                name=name,
                description=description,
                code=code,
                from_date=from_date,
                to_date=to_date,
                special_price=special_price,
                member_price=member_price,
                rate=rate
            )
            promotion.save()
            return Response({
                "status": status.HTTP_200_OK,
                "message": "Promotion created successfully!",
                "data": {
                    "id": promotion.id,
                    "name": promotion.name,
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put'], url_path="edit-promotion")
    def edit_promotion(self, request):
        """
        Edit an existing promotion: body data
        - name: string
        - description: string
        - code: string
        - from_date
        - to_date
        - special_price: float
        - member_price: float
        - rate: float
        """
        promotion_id = request.data.get('id')
        name = request.data.get('name')
        description = request.data.get('description')
        code = request.data.get('code')
        from_date = request.data.get('from_date')
        to_date = request.data.get('to_date')
        special_price = request.data.get('special_price')
        member_price = request.data.get('member_price')
        rate = request.data.get('rate')

        try:
            promotion = Promotion.objects.get(id=promotion_id)
            if name:
                promotion.name = name
            if description:
                promotion.description = description
            if code:
                promotion.code = code
            if from_date:
                promotion.from_date = from_date
            if to_date:
                promotion.to_date = to_date
            if special_price:
                promotion.special_price = special_price
            if member_price:
                promotion.member_price = member_price
            if rate:
                promotion.rate = rate
            promotion.save()
            return Response({
                "status": status.HTTP_200_OK,
                "message": "Promotion updated successfully!"
            }, status=status.HTTP_200_OK)
        except Promotion.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Promotion not found."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'], url_path="delete-promotion")
    def delete_promotion(self, request):
        """
        Soft delete a promotion:
        - query_params: id
        """
        promotion_id = request.query_params.get('id')
        if not promotion_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Promotion ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            promotion = Promotion.objects.get(id=promotion_id)
            promotion.delete_at = timezone.now()  # Soft delete by setting delete_at
            promotion.save()
            return Response({
                "status": status.HTTP_200_OK,
                "message": "Promotion soft deleted successfully!"
            }, status=status.HTTP_200_OK)
        except Promotion.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Promotion not found."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put'], url_path="restore-promotion")
    def restore_promotion(self, request):
        """
        Restore a catalog and its child catalogs: body data:
        - id
        """
        promotion_id = request.data.get('id')
        
        if not promotion_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Promotion ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Tìm catalog bị xóa mềm (tức là có delete_at không null)
            promotion = Promotion.objects.get(id=promotion_id, delete_at__isnull=False)
        except Promotion.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Promotion not found or already restored."
            }, status=status.HTTP_404_NOT_FOUND)

        # Khôi phục catalog và các catalog con của nó
        promotion.delete_at = None
        promotion.save()

        return Response({
            "status": status.HTTP_200_OK,
            "message": "Promotion restored successfully."
        }, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['get'], url_path="get-dettail-promotion")
    def get_promotion(self, request):
        """
        Get promotion details: body data:
        - id
        """
        promotion_id = request.query_params.get('id')
        if not promotion_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Promotion ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            promotion = Promotion.objects.get(id=promotion_id)
            serializer = PromotionSerializer(promotion)
            return Response({
                "status": status.HTTP_200_OK,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Promotion.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Promotion not found."
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path="get-list-promotions")
    def list_promotions(self, request):
        """
        Get list of promotions with pagination.

        Parameters:
        - page_index: The index of the page (default is 1).
        - page_size: The number of items per page (default is 10).
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))

        promotions = Promotion.objects.all()  # Chỉ lấy các promotion chưa bị xóa mềm
        paginator = Paginator(promotions, page_size)

        try:
            paginated_promotions = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_promotions = paginator.page(1)
        except EmptyPage:
            paginated_promotions = paginator.page(paginator.num_pages)

        serializer = PromotionSerializer(paginated_promotions, many=True)

        return Response({
            "status": status.HTTP_200_OK,
            "message": "OK",
            "data": {
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_index": page_index,
                "page_size": page_size,
                "promotions": serializer.data
            }
        }, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['get'], url_path="search-promotions")
    def search_promotions(self, request):
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
        promotions = Promotion.objects.filter(name__icontains=name_query)

        paginator = Paginator(promotions, page_size)

        try:
            paginated_products = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_products = paginator.page(1)
        except EmptyPage:
            paginated_products = paginator.page(paginator.num_pages)

        serializer = PromotionSerializer(paginated_products, many=True)

        return Response({
            "status": status.HTTP_200_OK,
            "message": "OK",
            "data": {
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_index": page_index,
                "page_size": page_size,
                "promotions": serializer.data
            }
        }, status=status.HTTP_200_OK)
@permission_classes([AllowAny])
class PublicPromotionViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['get'], url_path="get-list-promotions")
    def list_promotions(self, request):
        """
        Get list of promotions with pagination.

        Parameters:
        - page_index: The index of the page (default is 1).
        - page_size: The number of items per page (default is 10).
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))

        promotions = Promotion.objects.filter(delete_at__isnull = True)  # Chỉ lấy các promotion chưa bị xóa mềm
        paginator = Paginator(promotions, page_size)

        try:
            paginated_promotions = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_promotions = paginator.page(1)
        except EmptyPage:
            paginated_promotions = paginator.page(paginator.num_pages)

        serializer = PromotionSerializer(paginated_promotions, many=True)

        return Response({
            "status": status.HTTP_200_OK,
            "message": "OK",
            "data": {
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_index": page_index,
                "page_size": page_size,
                "promotions": serializer.data
            }
        }, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['get'], url_path="get-dettail-promotion")
    def get_promotion(self, request):
        """
        Get promotion details: body data:
        - id
        """
        promotion_id = request.query_params.get('id')
        if not promotion_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Promotion ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            promotion = Promotion.objects.get(id=promotion_id, delete_at__isnull = True)
            serializer = PromotionSerializer(promotion)
            return Response({
                "status": status.HTTP_200_OK,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Promotion.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Promotion not found."
            }, status=status.HTTP_404_NOT_FOUND)
            
    @action(detail=False, methods=['get'], url_path="search-promotions")
    def search_promotions(self, request):
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
        promotions = Promotion.objects.filter(name__icontains=name_query, delete_at__isnull = True)

        paginator = Paginator(promotions, page_size)

        try:
            paginated_products = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_products = paginator.page(1)
        except EmptyPage:
            paginated_products = paginator.page(paginator.num_pages)

        serializer = PromotionSerializer(paginated_products, many=True)

        return Response({
            "status": status.HTTP_200_OK,
            "message": "OK",
            "data": {
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_index": page_index,
                "page_size": page_size,
                "promotions": serializer.data
            }
        }, status=status.HTTP_200_OK)