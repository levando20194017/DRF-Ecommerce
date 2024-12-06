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

        contacts = Contact.objects.all().order_by('-created_at')
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
                "contacts": serializer.data
            }
        }, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['delete'], url_path="delete-contact")
    def delete_contact(self, request):
        """
        API to search categories by name with pagination.
        - contact_id: int
        """
        contact_id = request.query_params.get("contact_id")

        if not contact_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Contact ID is required."
            })

        try:
            contact = Contact.objects.get(id=contact_id)
            contact.delete()
            return Response({
                "status": status.HTTP_200_OK,
                "message": "OK"
            }, status=status.HTTP_200_OK)
        except Contact.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Contact not found."
            })
        except Exception as e:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            })
    
    @action(detail=False, methods=['patch'], url_path="update-advised-status")
    def update_advised_status(self, request):
        """
        API to update `is_advised` field for multiple contacts.
        Request body example:
        [
            {"id": 1, "value": true},
            {"id": 2, "value": false}
        ]
        """
        try:
            data = request.data  # Expecting a list of objects
            if not isinstance(data, list):
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Request data should be a list of objects."
                })

            # Validate each item in the list
            for item in data:
                if not isinstance(item, dict) or 'id' not in item or 'is_advised' not in item:
                    return Response({
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": "Each item must contain 'id' and 'value' fields."
                    }, status=status.HTTP_400_BAD_REQUEST)

                contact_id = item['id']
                is_advised = item['is_advised']

                # Update the record
                try:
                    contact = Contact.objects.get(id=contact_id)
                    contact.is_advised = is_advised
                    contact.save()
                except Contact.DoesNotExist:
                    return Response({
                        "status": status.HTTP_404_NOT_FOUND,
                        "message": f"Contact with id {contact_id} not found."
                    })

            return Response({
                "status": status.HTTP_200_OK,
                "message": "All records updated successfully."
            })

        except Exception as e:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            })