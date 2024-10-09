import jwt
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Catalog
from .serializers import serializerCreateCatalog, serializerGetCatalog
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from drfecommerce.apps.my_admin.authentication import SafeJWTAuthentication
from rest_framework.decorators import action, permission_classes
from rest_framework import exceptions
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class CatalogViewSetGetData(viewsets.ViewSet):
    """
    A simple Viewset for handling user actions.
    """
    queryset = Catalog.objects.all()
    serializer_class = serializerGetCatalog
    
    authentication_classes = [SafeJWTAuthentication]
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
        catalogs = Catalog.objects.all().order_by('sort_order')

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
            'children': []
        }

        # Lấy danh sách con của catalog này
        children = [cat for cat in catalog_dict.values() if cat.parent_id == catalog]

        for child in children:
            catalog_data['children'].append(self.build_catalog_tree(child, catalog_dict))

        return catalog_data