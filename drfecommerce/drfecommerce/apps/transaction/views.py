from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Transaction
from .serializers import TransactionSerializer
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from rest_framework.permissions import IsAuthenticated
from drfecommerce.apps.my_admin.authentication import AdminSafeJWTAuthentication
from drfecommerce.apps.blog.models import Blog
from rest_framework.decorators import action
from dotenv import load_dotenv
from django.utils import timezone

# Load environment variables from .env file
load_dotenv()
# Create your views here.
class TransactionViewSet(viewsets.ViewSet):
    authentication_classes = [AdminSafeJWTAuthentication]
    permission_classes = [IsAuthenticated]
        
    @action(detail=False, methods=['get'], url_path="get-detail-transaction")
    def get_transaction(self, request):
        """
        Get transaction details: body data:
        - id
        """
        transaction_id = request.query_params.get('id')
        if not transaction_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Transaction ID is required."
            })

        try:
            transaction = Transaction.objects.get(id=transaction_id)
            serializer = TransactionSerializer(transaction)
            return Response({
                "status": status.HTTP_200_OK,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Transaction.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Transaction not found."
            })
        
    @action(detail=False, methods=['get'], url_path="search-transactions")
    def search_transactions(self, request):
        """
        API to search transactions by name with pagination.
        - page_index (default=1)
        - page_size (default=10)
        - name: category name to search
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))
        name_query = request.GET.get('text_search', '').strip()
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        # Lọc sản phẩm theo tên
        transactions = Transaction.objects.all()
        if name_query:
            transactions = Transaction.objects.filter(transaction_number__icontains=name_query) 
        if start_date and end_date:
            transactions = transactions.filter(created_at__range=[start_date, end_date])
        elif start_date:
            transactions = transactions.filter(created_at__gte=start_date)
        elif end_date:
            transactions = transactions.filter(created_at__lte=end_date)

        paginator = Paginator(transactions, page_size)

        try:
            paginated_transactions = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_transactions = paginator.page(1)
        except EmptyPage:
            paginated_transactions = paginator.page(paginator.num_pages)

        serializer = TransactionSerializer(paginated_transactions, many=True)

        return Response({
            "status": status.HTTP_200_OK,
            "message": "OK",
            "data": {
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_index": page_index,
                "page_size": page_size,
                "transactions": serializer.data
            }
        }, status=status.HTTP_200_OK)