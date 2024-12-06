from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Contact
from .serializers import ContactSerializer
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from rest_framework.permissions import IsAuthenticated
from drfecommerce.apps.my_admin.authentication import AdminSafeJWTAuthentication
from rest_framework.decorators import action,  permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
# Create your views here.
@authentication_classes([])
@permission_classes([AllowAny])
class ContactViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'], url_path="create-new-contact")
    def create_contact(self, request):
        """
        Create a new category: body data
        - full_name: string
        - phone_number: string
        - email: string
        - question: string
        """
        full_name = request.data.get('full_name')
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')
        question = request.data.get('question')
        
        # Kiểm tra xem `name` đã tồn tại hay chưa
        try:
            contact = Contact.objects.create(
                full_name=full_name,
                email = email,
                phone_number = phone_number,
                question = question
            )
            contact.save()
            return Response({
                "status": status.HTTP_201_CREATED,
                "message": "contact created successfully!",
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            })
            
class AdminContactViewSet(viewsets.ViewSet):
    authentication_classes = [AdminSafeJWTAuthentication]
    permission_classes = [IsAuthenticated]
    @action(detail=False, methods=['get'], url_path="search-contacts")
    def search_contacts(self, request):
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
        contacts = Contact.objects.all()
        if name_query:
            contacts = Contact.objects.filter(full_name__icontains=name_query)

        paginator = Paginator(contacts, page_size)

        try:
            paginated_contacts = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_contacts = paginator.page(1)
        except EmptyPage:
            paginated_contacts = paginator.page(paginator.num_pages)

        serializer = ContactSerializer(paginated_contacts, many=True)

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