from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Catalog
from .serializers import serializerCreateCatalog, serializerGetCatalog
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated, AllowAny
from drfecommerce.apps.my_admin.authentication import AdminSafeJWTAuthentication
from rest_framework.decorators import action, permission_classes
import os
from dotenv import load_dotenv
from django.utils import timezone

# Load environment variables from .env file
load_dotenv()

class CatalogViewSetGetData(viewsets.ViewSet):
    queryset = Catalog.objects.all()
    serializer_class = serializerGetCatalog
    
    authentication_classes = [AdminSafeJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('page_index', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Index of the page'),
        openapi.Parameter('page_size', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of items per page'),
    ])
    @action(detail=False, methods=['get'], url_path="get-list-catalogs")
    def list_catalogs(self, request):
        """
        List catalogs with pagination and hierarchical structure.

        Parameters:
        - page_index: The index of the page (default is 1).
        - page_size: The number of items per page (default is 10).
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))

        # Lấy toàn bộ danh sách catalog
        catalogs = Catalog.objects.all()

        # Chia trang
        paginator = Paginator(catalogs, page_size)
        try:
            catalogs_page = paginator.page(page_index)
        except PageNotAnInteger:
            catalogs_page = paginator.page(1)
        except EmptyPage:
            catalogs_page = paginator.page(paginator.num_pages)

        # Chuyển đổi dữ liệu thành cấu trúc phân cấp
        data = self.get_hierarchical_data(catalogs_page)

        return Response({
            "status": 200,
            "message": "OK",
            "data": {
                "total_pages": paginator.num_pages,
                "data": data
            }
        })

    def get_hierarchical_data(self, catalogs):
        """
        Xây dựng cấu trúc phân cấp cho các catalog.
        """
        catalog_dict = {catalog.id: catalog for catalog in catalogs}
        hierarchical_data = []

        for catalog in catalogs:
            if catalog.parent_id is None:  # Nếu không có parent, thêm vào cấp cao nhất
                hierarchical_data.append(self.build_catalog_tree(catalog, catalog_dict))

        return hierarchical_data

    def build_catalog_tree(self, catalog, catalog_dict):
        """
        Xây dựng cây phân cấp cho một catalog.
        """
        catalog_data = {
            'id': catalog.id,
            'name': catalog.name,
            'description': catalog.description,
            'level': catalog.level,
            'sort_order': catalog.sort_order,
            'image': catalog.image,
            'created_at': catalog.created_at,
            'updated_at': catalog.updated_at,
            'delete_at': catalog.delete_at,
            'children': []
        }

        # Lấy danh sách con của catalog này
        children = [cat for cat in catalog_dict.values() if cat.parent_id == catalog]

        for child in children:
            catalog_data['children'].append(self.build_catalog_tree(child, catalog_dict))

        return catalog_data
    
    @action(detail=False, methods=['get'], url_path="search-catalogs")
    def search_catalogs(self, request):
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
        catalogs = Catalog.objects.filter(name__icontains=name_query)

        paginator = Paginator(catalogs, page_size)

        try:
            paginated_products = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_products = paginator.page(1)
        except EmptyPage:
            paginated_products = paginator.page(paginator.num_pages)

        serializer = serializerGetCatalog(paginated_products, many=True)

        return Response({
            "status": status.HTTP_200_OK,
            "message": "OK",
            "data": {
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_index": page_index,
                "page_size": page_size,
                "catalogs": serializer.data
            }
        }, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['get'], url_path="get-detail-catalog")
    def get_catalog(self, request):
        """
        Get catalog details:
        - query params: id
        """
        catalog_id = request.query_params.get('id')
        if not catalog_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Catalog ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            catalog = Catalog.objects.get(id=catalog_id)
            serializer = serializerGetCatalog(catalog)
            return Response({
                "status": status.HTTP_200_OK,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Catalog.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Catalog not found."
            }, status=status.HTTP_404_NOT_FOUND)
            
class CatalogViewSetCreateData(viewsets.ViewSet):
    serializer_class = serializerCreateCatalog
    
    authentication_classes = [AdminSafeJWTAuthentication]
    permission_classes = [IsAuthenticated]
    @action(detail=False, methods=['post'], url_path="create-new-catalog")
    def create_catalog(self, request):    
        """ form data:
        - description: string
        - parent_id: integer (allow null, id of parent catalog)
        - name: string
        - image: string
        """  
        parent_id = request.data.get('parent_id')
        name = request.data.get('name')
        
        allowed_fields = ['name', 'description', 'parent_id', 'image']
        catalog_data = {}
        
        for field in allowed_fields:
            if field in request.data:
                catalog_data[field] = request.data[field]
                
        try:
            if(parent_id):
                catalog_parent = Catalog.objects.get(id=parent_id)
                catalog_data['level'] = catalog_parent.level  + 1
                
                #check trùng tên catalog trong cùng 1 bậc thuộc cùng 1 lớp cha parent_id
                list_catalog_children = Catalog.objects.filter(parent_id=parent_id)
                
                # Kiểm tra xem có tên trùng lặp với new_name trong danh sách không
                duplicates = [catalog.name for catalog in list_catalog_children if catalog.name == name]
                if duplicates:
                    return Response({
                            'status': 201,
                            'message': "Catalog at this level already exists"
                            })
            else:
                catalog_data['level'] = 1
                
                #check trùng tên catalog ở catalog bậc 1. bậc cao nhất
                list_catalog_children = Catalog.objects.filter(level=1)
                
                duplicates = [catalog.name for catalog in list_catalog_children if catalog.name == name]
                if duplicates:
                    return Response({
                            'status': 201,
                            'message': "Catalog at this level already exists"
                            })
                    
            serializer = serializerCreateCatalog(data=catalog_data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "status": 200,
                    "message": "Create new user successfully!",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'message': serializer.errors
                })
        except Catalog.DoesNotExist:
            return Response({
                "status": 404,
                "message": "Catalog parent not found."
            }, status=status.HTTP_404_NOT_FOUND)
        
class CatalogViewSetDeleteData(viewsets.ViewSet):
    authentication_classes = [AdminSafeJWTAuthentication]
    permission_classes = [IsAuthenticated]
    @action(detail=False, methods=['delete'], url_path="delete-catalog")
    def delete_catalog(self, request):
        """
        Soft delete a catalog and its child catalogs.
        - query_params: id
        """
        catalog_id = request.query_params.get('id')

        if not catalog_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Catalog ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            catalog = Catalog.objects.get(id=catalog_id, delete_at__isnull=True)
        except Catalog.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Catalog not found or already deleted."
            }, status=status.HTTP_404_NOT_FOUND)

        # Perform soft delete on the catalog and its child catalogs
        self.soft_delete_catalog_and_children(catalog)

        return Response({
            "status": status.HTTP_200_OK,
            "message": "Catalog and related child catalogs soft deleted successfully."
        }, status=status.HTTP_200_OK)

    def soft_delete_catalog_and_children(self, catalog):
        """
        Recursively soft delete the catalog and its child catalogs.
        """
        # Đặt thời gian hiện tại cho trường delete_at
        catalog.delete_at = timezone.now()
        catalog.save()

        # Tìm các catalog con của catalog hiện tại
        child_catalogs = Catalog.objects.filter(parent_id=catalog.id, delete_at__isnull=True)

        # Đệ quy xóa mềm các catalog con
        for child in child_catalogs:
            self.soft_delete_catalog_and_children(child)
            
class CatalogViewSetRestoreData(viewsets.ViewSet):
    authentication_classes = [AdminSafeJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['put'], url_path="restore-catalog")
    def restore_catalog(self, request):
        """
        Restore a catalog and its child catalogs: body data:
        - id
        """
        catalog_id = request.data.get('id')
        
        if not catalog_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Catalog ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Tìm catalog bị xóa mềm (tức là có delete_at không null)
            catalog = Catalog.objects.get(id=catalog_id, delete_at__isnull=False)
        except Catalog.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Catalog not found or already restored."
            }, status=status.HTTP_404_NOT_FOUND)

        # Khôi phục catalog và các catalog con của nó
        self.restore_catalog_and_children(catalog)

        return Response({
            "status": status.HTTP_200_OK,
            "message": "Catalog and related child catalogs restored successfully."
        }, status=status.HTTP_200_OK)

    def restore_catalog_and_children(self, catalog):
        """
        Recursively restore the catalog and its child catalogs.
        """
        # Đặt delete_at = None để phục hồi catalog
        catalog.delete_at = None
        catalog.save()

        # Tìm các catalog con của catalog hiện tại bị xóa mềm
        child_catalogs = Catalog.objects.filter(parent_id=catalog.id, delete_at__isnull=False)

        # Đệ quy phục hồi các catalog con
        for child in child_catalogs:
            self.restore_catalog_and_children(child)
            
class CatalogViewSetEditData(viewsets.ViewSet):
    authentication_classes = [AdminSafeJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['put'], url_path="edit-catalog")
    def edit_catalog(self, request):
        """
        Edit catalog details. body data:
        - id: integer (id of catalog)
        - name: string
        - description: string
        - image: string (link of image catalog)
        """
        catalog_id = request.data.get('id')
        name = request.data.get('name')
        description = request.data.get('description')
        image = request.data.get('image')

        if not catalog_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Catalog ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            catalog = Catalog.objects.get(id=catalog_id)
        except Catalog.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Catalog does not exist."
            }, status=status.HTTP_404_NOT_FOUND)

        # Chỉ cập nhật nếu trường đó được gửi lên từ request
        if name:
            catalog.name = name
        if description:
            catalog.description = description
        if image:
            catalog.image = image

        catalog.save()

        return Response({
            "status": status.HTTP_200_OK,
            "message": "Catalog updated successfully."
        }, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['put'], url_path="edit-image-catalog")
    def edit_image_catalog(self, request):
        """
        change image of catalog. form body:
        - id: integer
        - img_data: binary
        - img_name: string
        """
        catalog_id = request.data.get('id')
        img_data = request.data.get('file')
        img_name = request.data.get('file_name')
        
        if not catalog_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Catalog ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            catalog = Catalog.objects.get(id = catalog_id)
        except Catalog.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Catalog not found or already deleted."
            }, status=status.HTTP_404_NOT_FOUND)
        
        if img_name:
            # Lưu file ảnh vào đường dẫn cục bộ
            img_path = os.path.join("C:/Users/Mine/Documents/document/PROJECT/DATN/Ecommerce_Images/", img_name)
            # Đọc dữ liệu từ InMemoryUploadedFile và ghi vào file
            with open(img_path, 'wb') as img_file:
                for chunk in img_data.chunks():
                    img_file.write(chunk)

            # Cập nhật đường dẫn ảnh vào trường image của catalog
            catalog.image = f'file:///C:/Users/Mine/Documents/document/PROJECT/DATN/Ecommerce_Images/{img_name}'
            print(catalog)
            catalog.save()
            return Response({
                "status": status.HTTP_200_OK,
                "message": "Catalog updated image successfully."
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": 404,
                "message": "file_name is required"
            }, status=status.HTTP_200_OK)
            
@permission_classes([AllowAny])         
class PublicCatalogViewSetGetData(viewsets.ViewSet):
    queryset = Catalog.objects.all()
    serializer_class = serializerGetCatalog
    
    authentication_classes = [AdminSafeJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('page_index', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Index of the page'),
        openapi.Parameter('page_size', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of items per page'),
    ])
    @action(detail=False, methods=['get'], url_path="get-list-catalogs")
    def list_catalogs(self, request):
        """
        List catalogs with pagination and hierarchical structure.

        Parameters:
        - page_index: The index of the page (default is 1).
        - page_size: The number of items per page (default is 10).
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))

        # Lấy toàn bộ danh sách catalog
        catalogs = Catalog.objects.filter(delete_at__isnull = True)

        # Chia trang
        paginator = Paginator(catalogs, page_size)
        try:
            catalogs_page = paginator.page(page_index)
        except PageNotAnInteger:
            catalogs_page = paginator.page(1)
        except EmptyPage:
            catalogs_page = paginator.page(paginator.num_pages)

        # Chuyển đổi dữ liệu thành cấu trúc phân cấp
        data = self.get_hierarchical_data(catalogs_page)

        return Response({
            "status": 200,
            "message": "OK",
            "data": {
                "total_pages": paginator.num_pages,
                "data": data
            }
        })

    def get_hierarchical_data(self, catalogs):
        """
        Xây dựng cấu trúc phân cấp cho các catalog.
        """
        catalog_dict = {catalog.id: catalog for catalog in catalogs}
        hierarchical_data = []

        for catalog in catalogs:
            if catalog.parent_id is None:  # Nếu không có parent, thêm vào cấp cao nhất
                hierarchical_data.append(self.build_catalog_tree(catalog, catalog_dict))

        return hierarchical_data

    def build_catalog_tree(self, catalog, catalog_dict):
        """
        Xây dựng cây phân cấp cho một catalog.
        """
        catalog_data = {
            'id': catalog.id,
            'name': catalog.name,
            'description': catalog.description,
            'level': catalog.level,
            'sort_order': catalog.sort_order,
            'image': catalog.image,
            'created_at': catalog.created_at,
            'updated_at': catalog.updated_at,
            'delete_at': catalog.delete_at,
            'children': []
        }

        # Lấy danh sách con của catalog này
        children = [cat for cat in catalog_dict.values() if cat.parent_id == catalog]

        for child in children:
            catalog_data['children'].append(self.build_catalog_tree(child, catalog_dict))

        return catalog_data
    
    @action(detail=False, methods=['get'], url_path="search-catalogs")
    def search_catalogs(self, request):
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
        catalogs = Catalog.objects.filter(name__icontains=name_query, delete_at__isnull=True)

        paginator = Paginator(catalogs, page_size)

        try:
            paginated_products = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_products = paginator.page(1)
        except EmptyPage:
            paginated_products = paginator.page(paginator.num_pages)

        serializer = serializerGetCatalog(paginated_products, many=True)

        return Response({
            "status": status.HTTP_200_OK,
            "message": "OK",
            "data": {
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_index": page_index,
                "page_size": page_size,
                "catalogs": serializer.data
            }
        }, status=status.HTTP_200_OK)