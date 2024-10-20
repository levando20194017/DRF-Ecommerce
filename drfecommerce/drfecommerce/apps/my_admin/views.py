import jwt
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import MyAdmin
from drfecommerce.apps.guest.models import Guest
from drfecommerce.apps.my_admin.serializers import  AdminSerializerGetData, AdminSerializerLogin, AdminRefreshTokenSerializer
from drfecommerce.apps.guest.serializers import  GuestSerializerGetData
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from drfecommerce.apps.my_admin.authentication import AdminSafeJWTAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action, permission_classes
from drfecommerce.apps.my_admin.utils import generate_access_token, generate_refresh_token
from rest_framework import exceptions
import os
from dotenv import load_dotenv
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from drfecommerce.settings import base

# Load environment variables from .env file
load_dotenv()

class GuestViewSetGetData(viewsets.ViewSet):
    """
    A simple Viewset for handling user actions.
    """
    queryset = Guest.objects.all()
    serializer_class = GuestSerializerGetData
    
    authentication_classes = [AdminSafeJWTAuthentication]
    permission_classes = [IsAuthenticated] #cái này là áp dụng cho toàn bộ view
    # @permission_classes([IsAuthenticated]) #cái này là áp dụng quyền cho từng view khác nhau
    
    #api get all users
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('page_index', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Index of the page'),
        openapi.Parameter('page_size', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of items per page'),
    ])
    @action(detail=False, methods=['get'], url_path="get-list-guests")
    # @ensure_csrf_cookie
    def list_guests(self, request):
        """
        List users with pagination.

        Parameters:
        - page_index: The index of the page (default is 1).
        - page_size: The number of items per page (default is 10).
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))

        paginator = Paginator(self.queryset, page_size)
        try:
            users = paginator.page(page_index)
        except PageNotAnInteger:
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)

        serializer = GuestSerializerGetData(users, many=True)

        return Response({
            "status": 200,
            "message": "OK",
            "data": {
                "total_pages": paginator.num_pages,
                "data": serializer.data
                }
        })
        
class AdminViewSetGetData(viewsets.ViewSet):
    """
    A simple Viewset for handling user actions.
    """
    queryset = MyAdmin.objects.all()
    serializer_class = AdminSerializerGetData
    
    authentication_classes = [AdminSafeJWTAuthentication]
    permission_classes = [IsAuthenticated] #cái này là áp dụng cho toàn bộ view
    # @permission_classes([IsAuthenticated]) #cái này là áp dụng quyền cho từng view khác nhau
    
    #api get all users
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('page_index', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Index of the page'),
        openapi.Parameter('page_size', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of items per page'),
    ])
    @action(detail=False, methods=['get'], url_path="list-admins")
    # @ensure_csrf_cookie
    def list_admins(self, request):
        """
        List users with pagination.

        Parameters:
        - page_index: The index of the page (default is 1).
        - page_size: The number of items per page (default is 10).
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))

        paginator = Paginator(self.queryset, page_size)
        try:
            admins = paginator.page(page_index)
        except PageNotAnInteger:
            admins = paginator.page(1)
        except EmptyPage:
            admins = paginator.page(paginator.num_pages)

        serializer = AdminSerializerGetData(admins, many=True)

        return Response({
            "status": 200,
            "message": "OK",
            "data": {
                "total_pages": paginator.num_pages,
                "data": serializer.data
                }
        })
        
    #api detail user
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('id', in_=openapi.IN_PATH, type=openapi.TYPE_STRING, description='ID of the user'),
    ])
    @action(detail=False, methods=['get'], url_path="admin-information/(?P<id>[^/]+)")
    def detail_admin(self, request, id=None):
        """
        Get details of a specific admin based on ID.

        Parameters:
        - id: The ID of the admin to retrieve.
        """
        if id is None:
            return Response({
                "status": 400,
                "message": "ID parameter is required."
            }, status=400)

        try:
            admin = MyAdmin.objects.get(id=id)
            serializer = AdminSerializerGetData(admin)
            return Response({
                "status": 200,
                "message": "OK",
                "data": serializer.data
            })
        except MyAdmin.DoesNotExist:
            return Response({
                "status": 404,
                "message": "User not found."
            }, status=404)
        except ValidationError:
            return Response({
                "status": 400,
                "message": "Invalid ID format."
            }, status=400)

@permission_classes([AllowAny])
class AdminViewSetLogin(viewsets.ViewSet):
    """
    A simple Viewset for handling user actions.
    """
    queryset = MyAdmin.objects.all()
    serializer_class = AdminSerializerLogin
    @action(detail=False, methods=['post'], url_path='admin/login')
    # @ensure_csrf_cookie
    #api login
    def login(self, request):
        try:
            admin = MyAdmin.objects.get(email=request.data['email'], password=request.data['password'])
            serializer_admin = AdminSerializerGetData(admin)
            # refresh = RefreshToken.for_user(user)
            
            access_token = generate_access_token(admin)
            refresh_token = generate_refresh_token(admin)
            
            # response = Response()
            # response.set_cookie(key='refreshtoken', value=refresh_token, httponly=True)     
            return Response({
                    "status": 200,
                    "message": "OK",
                    "data": {
                            'access_token': access_token,
                            'refresh_token': refresh_token,
                            'user_infor': serializer_admin.data
                        }
                    })
        except MyAdmin.DoesNotExist:
            return Response({
                "status": 404,
                "message": "Invalid email or password"
            }, status=404)
            
@permission_classes([AllowAny])
class RefreshTokenView(viewsets.ViewSet):
    serializer_class = AdminRefreshTokenSerializer
    
    #api refresh token
    @action(detail=False, methods=['post'], url_path='admin/token/refresh')
    def post(self, request):
        refresh_token = request.data['refresh_token']
        
        if refresh_token is None:
            raise exceptions.AuthenticationFailed(
                'Authentication credentials were not provided.')
        try:
            payload = jwt.decode(
                refresh_token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed(
                'expired refresh token, please login again.')

        admin = MyAdmin.objects.filter(id=payload.get('admin_id')).first()
        if admin is None:
            raise exceptions.AuthenticationFailed('Admin not found')
        
        access_token = generate_access_token(admin)
        return Response({
            'status': 200,
            'message': "OK",
            'data': {
                'access_token': access_token
            }
            })

class AdminViewsetUploadImage(viewsets.ViewSet):
    """
    A simple Viewset for handling upload image actions.
    """
    authentication_classes = [AdminSafeJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='upload-image')
    def upload_image(self, request):
        if 'file' not in request.FILES:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "No image file found in request."
            }, status=status.HTTP_400_BAD_REQUEST)

        image = request.FILES['file']
        img_name = image.name

        # Sử dụng default_storage để lưu ảnh vào thư mục cục bộ hoặc dịch vụ lưu trữ khác trong tương lai
        save_path = os.path.join(base.MEDIA_ROOT, img_name)
        file_path = default_storage.save(save_path, ContentFile(image.read()))
        print(file_path)
        file_url = default_storage.url(file_path)

        return Response({
            "status": status.HTTP_200_OK,
            "message": "Image uploaded successfully!",
            "img_url": file_url
        }, status=status.HTTP_200_OK)