from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Tag
from .serializers import TagSerializer
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from rest_framework.permissions import IsAuthenticated
from drfecommerce.apps.my_admin.authentication import AdminSafeJWTAuthentication
from drfecommerce.apps.blog_tag.models import BlogTag
from rest_framework.decorators import action
from dotenv import load_dotenv
from django.utils import timezone

# Load environment variables from .env file
load_dotenv()
# Create your views here.
class TagViewSet(viewsets.ViewSet):
    authentication_classes = [AdminSafeJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path="create-new-tag")
    def create_tag(self, request):
        """
        Create a new tag: body data
        - name: string
        """
        name = request.data.get('name')

        try:
            tag = Tag.objects.create(
                name=name,
            )
            tag.save()
            return Response({
                "status": status.HTTP_200_OK,
                "message": "Tag created successfully!",
                "data": {
                    "id": tag.id,
                    "name": tag.name,
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            })

    @action(detail=False, methods=['put'], url_path="edit-tag")
    def edit_tag(self, request):
        """
        Edit an existing tag: body data
        - tag_id: int
        - name: string
        """
        tag_id = request.data.get('tag_id')
        name = request.data.get('name')

        try:
            tag = Tag.objects.get(id=tag_id)
            if name:
                tag.name = name
            tag.save()
            return Response({
                "status": status.HTTP_200_OK,
                "message": "Tag updated successfully!"
            }, status=status.HTTP_200_OK)
        except Tag.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Tag not found."
            })
        except Exception as e:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            })

    @action(detail=False, methods=['delete'], url_path="delete-tag")
    def delete_tag(self, request):
        """
        Soft delete a tag:
        - query_params: tag_id
        """
        tag_id = request.query_params.get('tag_id')
        if not tag_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Tag ID is required."
            })

        try:
            # Get the tag associated with the provided tag_id
            tag = Tag.objects.get(id=tag_id)
            
            # Soft delete by setting delete_at for BlogTag entries
            BlogTag.objects.filter(tag_id=tag_id).update(delete_at=timezone.now()) 
            
            # Soft delete the tag itself
            tag.delete_at = timezone.now()  
            tag.save()
            
            return Response({
                "status": status.HTTP_200_OK,
                "message": "Tag and its associations soft deleted successfully!"
            }, status=status.HTTP_200_OK)
        except Tag.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Tag not found."
            })
        except Exception as e:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            })

    @action(detail=False, methods=['put'], url_path="restore-tag")
    def restore_tag(self, request):
        """
        Restore a catalog and its child catalogs: body data:
        - id
        """
        tag_id = request.data.get('tag_id')
        
        if not tag_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Tag ID is required."
            })

        try:
            tag = Tag.objects.get(id=tag_id, delete_at__isnull=False)
        except Tag.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Tag not found or already restored."
            })

        # Khôi phục catalog và các catalog con của nó
        tag.delete_at = None
        tag.save()

        return Response({
            "status": status.HTTP_200_OK,
            "message": "Tag restored successfully."
        }, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['get'], url_path="get-detail-tag")
    def get_tag(self, request):
        """
        Get tag details: body data:
        - tag_id
        """
        tag_id = request.query_params.get('tag_id')
        if not tag_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Tag ID is required."
            })

        try:
            tag = Tag.objects.get(id=tag_id)
            serializer = TagSerializer(tag)
            return Response({
                "status": status.HTTP_200_OK,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Tag.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Tag not found."
            })

    @action(detail=False, methods=['get'], url_path="get-list-tags")
    def list_tags(self, request):
        """
        Get list of tags with pagination.

        Parameters:
        - page_index: The index of the page (default is 1).
        - page_size: The number of items per page (default is 10).
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))

        tags = Tag.objects.all()  # Chỉ lấy các tag chưa bị xóa mềm
        paginator = Paginator(tags, page_size)

        try:
            paginated_tags = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_tags = paginator.page(1)
        except EmptyPage:
            paginated_tags = paginator.page(paginator.num_pages)

        serializer = TagSerializer(paginated_tags, many=True)

        return Response({
            "status": status.HTTP_200_OK,
            "message": "OK",
            "data": {
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_index": page_index,
                "page_size": page_size,
                "tags": serializer.data
            }
        }, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['get'], url_path="search-tags")
    def search_tags(self, request):
        """
        API to search products by name with pagination.
        - page_index (default=1)
        - page_size (default=10)
        - name: product name to search
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))
        name_query = request.GET.get('name', '').strip()
        
        tags = Tag.objects.all()
        # Lọc sản phẩm theo tên
        if name_query:
            tags = Tag.objects.filter(name__icontains=name_query)

        paginator = Paginator(tags, page_size)

        try:
            paginated_tags = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_tags = paginator.page(1)
        except EmptyPage:
            paginated_tags = paginator.page(paginator.num_pages)

        serializer = TagSerializer(paginated_tags, many=True)

        return Response({
            "status": status.HTTP_200_OK,
            "message": "OK",
            "data": {
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_index": page_index,
                "page_size": page_size,
                "tags": serializer.data
            }
        }, status=status.HTTP_200_OK)