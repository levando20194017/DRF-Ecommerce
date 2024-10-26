from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Category
from .serializers import CategorySerializer
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from rest_framework.permissions import IsAuthenticated
from drfecommerce.apps.my_admin.authentication import AdminSafeJWTAuthentication
from rest_framework.decorators import action
from dotenv import load_dotenv
from django.utils import timezone

# Load environment variables from .env file
load_dotenv()
# Create your views here.
class CategoryViewSet(viewsets.ViewSet):
    authentication_classes = [AdminSafeJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path="create-new-category")
    def create_category(self, request):
        """
        Create a new category: body data
        - name: string
        """
        name = request.data.get('name')
        description = request.data.get('description')
        image = request.data.get('image')

        try:
            category = Category.objects.create(
                name=name,
                description = description,
                image = image
            )
            category.save()
            return Response({
                "status": status.HTTP_200_OK,
                "message": "category created successfully!",
                "data": {
                    "id": category.id,
                    "name": category.name,
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put'], url_path="edit-category")
    def edit_category(self, request):
        """
        Edit an existing category: body data
        - category_id: int
        - name: string
        """
        category_id = request.data.get('category_id')
        name = request.data.get('name')
        description = request.data.get('description')
        image = request.data.get('image')

        try:
            category = Category.objects.get(id=category_id)
            if name:
                category.name = name
            if description:
                category.description = description
            if name:
                category.image = image    
            category.save()
            return Response({
                "status": status.HTTP_200_OK,
                "message": "Category updated successfully!"
            }, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Category not found."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'], url_path="delete-category")
    def delete_category(self, request):
        """
        Soft delete a Category:
        - query_params: category_id
        """
        category_id = request.query_params.get('category_id')
        if not category_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Category ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            category = Category.objects.get(id=category_id)
            category.delete_at = timezone.now()  # Soft delete by setting delete_at
            category.save()
            return Response({
                "status": status.HTTP_200_OK,
                "message": "Category soft deleted successfully!"
            }, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Category not found."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put'], url_path="restore-category")
    def restore_category(self, request):
        """
        Restore a catalog and its child catalogs: body data:
        - id
        """
        category_id = request.data.get('category_id')
        
        if not category_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Category ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            category = Category.objects.get(id=category_id, delete_at__isnull=False)
        except Category.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Category not found or already restored."
            }, status=status.HTTP_404_NOT_FOUND)

        # Khôi phục catalog và các catalog con của nó
        category.delete_at = None
        category.save()

        return Response({
            "status": status.HTTP_200_OK,
            "message": "Category restored successfully."
        }, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['get'], url_path="get-dettail-category")
    def get_category(self, request):
        """
        Get category details: body data:
        - category_id
        """
        category_id = request.query_params.get('id')
        if not category_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Category ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            category = Category.objects.get(id=category_id)
            serializer = CategorySerializer(category)
            return Response({
                "status": status.HTTP_200_OK,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Category not found."
            }, status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=False, methods=['get'], url_path="search-categories")
    def search_categories(self, request):
        """
        API to search categories by name with pagination.
        - page_index (default=1)
        - page_size (default=10)
        - name: category name to search
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))
        name_query = request.GET.get('name', '').strip()

        # Lọc sản phẩm theo tên
        categorys = Category.objects.all()
        if name_query:
            categorys = Category.objects.filter(name__icontains=name_query)

        paginator = Paginator(categorys, page_size)

        try:
            paginated_categorys = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_categorys = paginator.page(1)
        except EmptyPage:
            paginated_categorys = paginator.page(paginator.num_pages)

        serializer = CategorySerializer(paginated_categorys, many=True)

        return Response({
            "status": status.HTTP_200_OK,
            "message": "OK",
            "data": {
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_index": page_index,
                "page_size": page_size,
                "categories": serializer.data
            }
        }, status=status.HTTP_200_OK)