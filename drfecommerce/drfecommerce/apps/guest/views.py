import jwt
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Guest
from drfecommerce.apps.guest.serializers import GuestSerializerCreate, GuestSerializerGetData, GuestSerializerLogin, GuestRefreshTokenSerializer, GuestSerializerChangeInfor, GuestSerializerChangeAvatar
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from drfecommerce.apps.guest.authentication import GuestSafeJWTAuthentication
from rest_framework.permissions import AllowAny
from drfecommerce.apps.my_admin.serializers import AdminSerializerGetData
from drfecommerce.apps.my_admin.models import MyAdmin
from rest_framework.decorators import action, permission_classes, authentication_classes
from drfecommerce.apps.guest.utils import generate_access_token, generate_refresh_token
from rest_framework import exceptions
import os
from dotenv import load_dotenv
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from drfecommerce.settings import base

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
# Load environment variables from .env file
load_dotenv()

class GuestViewSetGetData(viewsets.ViewSet):
    """
    A simple Viewset for handling user actions.
    """
    queryset = Guest.objects.all()
    serializer_class = GuestSerializerGetData
    
    authentication_classes = [GuestSafeJWTAuthentication]
    permission_classes = [IsAuthenticated] #cái này là áp dụng cho toàn bộ view
    # @permission_classes([IsAuthenticated]) #cái này là áp dụng quyền cho từng view khác nhau
    
    #api get all users
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('page_index', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Index of the page'),
        openapi.Parameter('page_size', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of items per page'),
    ])
    @action(detail=False, methods=['get'], url_path="list-guests")
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
        
    #api detail user
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('id', in_=openapi.IN_PATH, type=openapi.TYPE_STRING, description='ID of the user'),
    ])
    @action(detail=False, methods=['get'], url_path="guest-information/(?P<id>[^/]+)")
    def detail_guest(self, request, id=None):
        """
        Get details of a specific user based on ID.

        Parameters:
        - id: The ID of the user to retrieve.
        """
        if id is None:
            return Response({
                "status": 400,
                "message": "ID parameter is required."
            }, status=400)

        try:
            user = Guest.objects.get(id=id)
            serializer = GuestSerializerGetData(user)
            return Response({
                "status": 200,
                "message": "OK",
                "data": serializer.data
            })
        except Guest.DoesNotExist:
            return Response({
                "status": 404,
                "message": "User not found."
            }, status=404)
        except ValidationError:
            return Response({
                "status": 400,
                "message": "Invalid ID format."
            }, status=400)

class GuestViewSetChangeInfor(viewsets.ViewSet):
    serializer_class = GuestSerializerChangeInfor
    
    authentication_classes = [GuestSafeJWTAuthentication]
    permission_classes = [IsAuthenticated] 
    
    @action(detail=False, methods=['put'], url_path="change-information")
    def change_infor(self, request):
        try:
            user_id = request.data.get('user_id')
            user = Guest.objects.get(id=user_id)
            
            for field, value in request.data.items():
                if field != "user_id" and field != "role":
                    setattr(user, field, value)
                    
            serializer = GuestSerializerChangeInfor(instance=user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                serializerInfo = GuestSerializerGetData(user)
                return Response({
                    "status": 200,
                    "message": "Change user information successfully!",
                    "data": serializerInfo.data
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors)
            
        except Guest.DoesNotExist:
            return Response({
                "status": 404,
                "message": "User not found."
            })
            
    @action(detail=False, methods=['put'], url_path="change-avatar")
    def change_avatar(self, request):
        if 'file' not in request.FILES:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "No image file found in request."
            })

        user_id = request.data.get('user_id')
        if not user_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "User ID is required."
            })

        try:
            user = Guest.objects.get(id=user_id)
        except Guest.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "User not found."
            })

        image = request.FILES['file']
        img_name = image.name

        try:
            # Sử dụng default_storage để lưu ảnh
            save_path = os.path.join(base.MEDIA_ROOT, img_name)
            file_path = default_storage.save(save_path, ContentFile(image.read()))
            file_url = default_storage.url(file_path)

            # Cập nhật avatar của user
            user.avatar = file_url
            user.save()

            return Response({
                "status": status.HTTP_200_OK,
                "message": "Avatar changed successfully!",
                "img_url": file_url
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": f"An error occurred while saving the image: {str(e)}"
            })
            
@authentication_classes([])            
@permission_classes([AllowAny])       
class GuestViewSetCreate(viewsets.ViewSet):
    """
    A simple Viewset for handling user actions.
    """

    queryset = Guest.objects.all()
    serializer_class = GuestSerializerCreate
    #api register
    @action(detail=False, methods=['post'], url_path='register')
    def create_guest(self, request):
        user_data = {}

        allowed_fields = ['first_name', 'last_name', 'email', 'password', 'address', 'city', 'country', 'phone_number']  # Các trường bạn muốn chấp nhận

        for field in allowed_fields:
            if field in request.data:
                user_data[field] = request.data[field]

        # # Tạo mã xác nhận 6 chữ số
        # confirmation_code = ''.join(random.choices('0123456789', k=6))

        # # Địa chỉ email người gửi
        # sender_email = 'levando0708@gmail.com'

        # # Gửi email chứa mã xác nhận
        # send_mail(
        #     'Xác nhận đăng ký',
        #     f'Mã xác nhận của bạn là: {confirmation_code}',
        #     sender_email,
        #     [user_data['email']],
        #     fail_silently=False,
        # )

        serializer = GuestSerializerCreate(data=user_data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": 200,
                "message": "Create new user successfully!",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status': status.HTTP_400_BAD_REQUEST,
            'message': serializer.errors['email'][0]
            })

@authentication_classes([])
@permission_classes([AllowAny])
class GuestViewSetLogin(viewsets.ViewSet):
    """
    A simple Viewset for handling user actions.
    """
    queryset = Guest.objects.all()
    serializer_class = GuestSerializerLogin
    @action(detail=False, methods=['post'], url_path='login')
    # @ensure_csrf_cookie
    #api login
    def login(self, request):
        # try:
            user = Guest.objects.filter(email=request.data['email'], password=request.data['password'])
            if not user:
                try:            
                    admin = MyAdmin.objects.get(email=request.data['email'], password=request.data['password'])
                    serializer_admin = AdminSerializerGetData(admin)
                    access_token = generate_access_token(admin)
                    refresh_token = generate_refresh_token(admin)
                    
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
                    })
                    
            else:
                try:    
                    user = Guest.objects.get(email=request.data['email'], password=request.data['password'])
                    serializer_user = GuestSerializerGetData(user)
                    # refresh = RefreshToken.for_user(user)
                    
                    access_token = generate_access_token(user)
                    refresh_token = generate_refresh_token(user)
                    
                    # response = Response()
                    # response.set_cookie(key='refreshtoken', value=refresh_token, httponly=True)
                    if not user.is_verified:
                        return Response({
                            "status": 201,
                            "message": "This account is not verified.", 
                        })
                    else:       
                        return Response({
                            "status": 200,
                            "message": "OK",
                            "data": {
                                    'access_token': access_token,
                                    'refresh_token': refresh_token,
                                    'user_infor': serializer_user.data
                                }
                            })
                except Guest.DoesNotExist:
                    return Response({
                        "status": 404,
                        "message": "Invalid email or password"
                    })

@authentication_classes([])            
@permission_classes([AllowAny])
class RefreshTokenView(viewsets.ViewSet):
    serializer_class = GuestRefreshTokenSerializer
    
    #api refresh token
    @action(detail=False, methods=['post'], url_path='token/refresh')
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

        user = Guest.objects.filter(id=payload.get('user_id')).first()
        if user is None:
            raise exceptions.AuthenticationFailed('User not found')

        if not user.is_verified:
            raise exceptions.AuthenticationFailed('user is inactive')

        access_token = generate_access_token(user)
        return Response({
            'status': 200,
            'message': "OK",
            'data': {
                'access_token': access_token
            }
            })


    
            