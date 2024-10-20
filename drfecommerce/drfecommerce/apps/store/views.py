from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Store
from .serializers import StoreSerializer
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from rest_framework.permissions import IsAuthenticated
from drfecommerce.apps.my_admin.authentication import AdminSafeJWTAuthentication
from rest_framework.decorators import action
from dotenv import load_dotenv
from django.utils import timezone
from django.db import models

# Load environment variables from .env file
load_dotenv()

class StoreViewSet(viewsets.ViewSet):
    """
    ViewSet cho các thao tác với Store.
    """
    authentication_classes = [AdminSafeJWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path="create-store")
    def create_store(self, request):
        """
        API để tạo một Store mới: body data
        - name: string
        - phone_number: string
        - email: string
        - address: string
        - postal_code: string
        - opening_hours: string (hh:mm:ss)
        - closing_hours: string (hh:mm:ss)
        """
        serializer = StoreSerializer(data=request.data)
        if serializer.is_valid():
            store = serializer.save()
            return Response({
                "status": status.HTTP_201_CREATED,
                "message": "Store created successfully!",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['put'], url_path="edit-store")
    def edit_store(self, request):
        """
        API để cập nhật một Store: body data
        - id: int (bắt buộc)
        - Các trường khác nếu có dữ liệu thì cập nhật, nếu không có thì giữ nguyên.
        """
        store_id = request.data.get('id')
        if not store_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Store ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Store not found."
            }, status=status.HTTP_404_NOT_FOUND)

        # Cập nhật chỉ những trường có trong request.data (partial=True)
        serializer = StoreSerializer(store, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # Lưu lại các thay đổi
            return Response({
                "status": status.HTTP_200_OK,
                "message": "Store updated successfully!",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'], url_path="delete-store")
    def delete_store(self, request):
        """
        API để soft delete một Store: query_params
        - id: int
        """
        store_id = request.query_params.get('id')
        if not store_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Store ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            store = Store.objects.get(id=store_id)
            store.delete_at = timezone.now()  # Soft delete by setting delete_at
            store.save()
            return Response({
                "status": status.HTTP_200_OK,
                "message": "Store soft deleted successfully!"
            }, status=status.HTTP_200_OK)
        except Store.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Store not found."
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['put'], url_path="restore-store")
    def restore_store(self, request):
        """
        API để khôi phục một Store: body data
        - id: int
        """
        store_id = request.data.get('id')
        if not store_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Store ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            store = Store.objects.get(id=store_id, delete_at__isnull=False)
        except Store.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Store not found or already restored."
            }, status=status.HTTP_404_NOT_FOUND)
        
        store.delete_at = None
        store.save()
        return Response({
            "status": status.HTTP_200_OK,
            "message": "Store restored successfully!"
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path="get-detail-store")
    def get_store(self, request):
        """
        API để lấy thông tin chi tiết của một Store: query_params
        - id: int
        """
        store_id = request.query_params.get('id')
        if not store_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Store ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            store = Store.objects.get(id=store_id)
            serializer = StoreSerializer(store)
            return Response({
                "status": status.HTTP_200_OK,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Store.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Store not found."
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'], url_path="get-list-stores")
    def list_stores(self, request):
        """
        Lấy danh sách tất cả các store (cửa hàng) với phân trang.

        Parameters:
        - page_index: Chỉ số của trang (mặc định là 1).
        - page_size: Số lượng item trên mỗi trang (mặc định là 10).
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))

        stores = Store.objects.all().order_by('-created_at')  # Lấy tất cả các store
        paginator = Paginator(stores, page_size)

        try:
            paginated_stores = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_stores = paginator.page(1)
        except EmptyPage:
            paginated_stores = paginator.page(paginator.num_pages)

        serializer = StoreSerializer(paginated_stores, many=True)

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

    @action(detail=False, methods=['get'], url_path="search-stores")
    def search_stores(self, request):
        """
        Tìm kiếm store theo tên hoặc địa chỉ với phân trang.

        Parameters:
        - search: Từ khóa tìm kiếm.
        - page_index: Chỉ số của trang (mặc định là 1).
        - page_size: Số lượng item trên mỗi trang (mặc định là 10).
        """
        search_query = request.GET.get('search', '')
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))

        stores = Store.objects.filter(
            models.Q(name__icontains=search_query) | models.Q(address__icontains=search_query)
        ).order_by('-created_at')

        paginator = Paginator(stores, page_size)

        try:
            paginated_stores = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_stores = paginator.page(1)
        except EmptyPage:
            paginated_stores = paginator.page(paginator.num_pages)

        serializer = StoreSerializer(paginated_stores, many=True)

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