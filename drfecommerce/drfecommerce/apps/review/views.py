from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Review, ReviewReply
from .serializers import ReviewSerializer, ReviewReplySerializer, GetAllReviewSerializer
from drfecommerce.apps.order_detail.models import OrderDetail
from drfecommerce.apps.guest.models import Guest
from drfecommerce.apps.notification.views import create_notification
from drfecommerce.settings import base
from rest_framework.permissions import IsAuthenticated, AllowAny
from drfecommerce.apps.guest.authentication import GuestSafeJWTAuthentication
from drfecommerce.apps.my_admin.authentication import AdminSafeJWTAuthentication
from rest_framework.decorators import action, permission_classes
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.db.models import Avg

class ReviewViewSet(viewsets.ViewSet):
    authentication_classes = [GuestSafeJWTAuthentication]
    permission_classes = [IsAuthenticated]
    @action(detail=False, methods=['post'], url_path="guest-review")
    def guest_review(self, request):
        # Lấy thông tin từ request
        """
        request body data
        - guest_id: int
        - order_detail_id: int
        - product_id: int
        - rating: int (1 <= rating <= 5)
        - comment: string
        - gallery: string
        """
        
        guest_id = request.data.get('guest_id')
        order_detail_id = request.data.get('order_detail_id')
        product_id = request.data.get('product_id')
        store_id = request.data.get('store_id')
        rating = request.data.get('rating')
        comment = request.data.get('comment', '')
        gallery = request.data.get('gallery', '')

        if not guest_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Guest ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            guest = Guest.objects.get(id=guest_id)
        except Guest.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Guest not found."
            }, status=status.HTTP_404_NOT_FOUND)
        # Kiểm tra xem OrderDetail có tồn tại hay không
        try:
            order_detail = OrderDetail.objects.get(id=order_detail_id, product_id=product_id, order__guest=guest)
        except OrderDetail.DoesNotExist:
            return Response({'error': 'Invalid order detail or product.',
                             'status': 400}, status=status.HTTP_400_BAD_REQUEST)
        
        # Kiểm tra trạng thái của order
        if order_detail.order.order_status != 'delivered':
            return Response({'error': 'You can only review a product after the order has been delivered.',
                             'status': 403
                             }, status=status.HTTP_403_FORBIDDEN)
        
        #Kiểm tra xem người dùng đã đánh giá sản phẩm này trong order này chưa
        if Review.objects.filter(guest=guest, order_detail=order_detail, product_id=product_id).exists():
            return Response({'error': 'You have already submitted a review for this product in this order.',
                             'status': 400
                             }, status=status.HTTP_400_BAD_REQUEST)
        
        # Tạo đánh giá
        review = Review.objects.create(
            guest=guest,
            product_id=product_id,
            store_id=store_id,
            order_detail=order_detail,
            rating=rating,
            comment=comment,
            gallery=gallery
        )
        
        # Serialize và trả về phản hồi
        serializer = ReviewSerializer(review)
        return Response({
            "data": serializer.data,
            "status": status.HTTP_201_CREATED
            }, status=status.HTTP_201_CREATED)
        
    @action(detail=False, methods=['put'], url_path="update-review")
    def update_review(self, request):
        # Lấy thông tin từ request
        """
        request body data
        - guest_id: int
        - product_id: int
        - rating: int (1 <= rating <= 5)
        - comment: string
        - gallery: string
        """
        guest_id = request.data.get('guest_id')
        product_id = request.data.get('product_id')
        store_id = request.data.get('store_id')
        rating = request.data.get('rating')
        comment = request.data.get('comment', '')
        gallery = request.data.get('gallery', '')
        
        if not guest_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Guest ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            guest = Guest.objects.get(id=guest_id)
        except Guest.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Guest not found."
            }, status=status.HTTP_404_NOT_FOUND)
        try:
            review = Review.objects.get(guest=guest, product_id=product_id, store_id = store_id)
        except Review.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Review not found."
            }, status=status.HTTP_404_NOT_FOUND)
        review.comment = comment
        review.rating = rating
        review.gallery = gallery
        review.save()
        return Response({
            "data": "Update reiew successfully",
            "status": 200
            }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['delete'], url_path="delete-review")
    def delete_review(self, request):
        # Lấy thông tin từ request
        """
        query_params:
        - guest_id: int
        - product_id: int
        - store_id: int
        """
        product_id = request.query_params.get('product_id')
        guest_id = request.query_params.get('guest_id')
        store_id = request.query_params.get('store_id')
        
        if not guest_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Guest ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            guest = Guest.objects.get(id=guest_id)
        except Guest.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Guest not found."
            }, status=status.HTTP_404_NOT_FOUND)
        try:
            review = Review.objects.get(guest=guest, product_id=product_id, store_id = store_id)
        except Review.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Review not found."
            }, status=status.HTTP_404_NOT_FOUND)
        review.delete()
        return Response({
            "data": "Delete reiew successfully",
            "status": 200
            }, status=status.HTTP_200_OK)

class AdminReviewViewset(viewsets.ViewSet):
    authentication_classes = [AdminSafeJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path="admin-reply-review")
    def admin_reply_review(self, request):
        # Lấy thông tin từ request
        """
        request body data
        - review_id: int
        - comment: string
        """
        admin_id = request.data.get('admin_id')
        review_id = request.data.get('review_id')
        reply = request.data.get('reply')
        
        if not review_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Review ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Review not found."
            }, status=status.HTTP_404_NOT_FOUND)

        # Create the reply
        reply_review = ReviewReply.objects.create(
            review=review,
            admin_id=admin_id,
            reply=reply
        )
        
        # Create a notification for the guest (review author)
        create_notification(
            guest=review.guest,  # Assuming `review.guest` gets the guest/author
            notification_type="review_reply",  # Define your notification type
            message=f"Admin replied to your review: {reply}",  # Customize the message
            related_object_id=review.id,  # Link it to the review ID
            url=f"/reviews/{review.id}"  # Optionally add a URL to the review
        )
        
        # Serialize and return the response
        serializer = ReviewReplySerializer(reply_review)
        return Response({
            "data": serializer.data,
            "status": status.HTTP_201_CREATED
        }, status=status.HTTP_201_CREATED)

@permission_classes([AllowAny])
class PublicReviewViewset(viewsets.ViewSet):
    @action(detail=False, methods=['get'], url_path="get-list-reviews")
    def get_list_reviews(self, request):
        """
        query params
        - product_id: id of product
        - store_id: id of product
        - page_index (default=1)
        - page_size (default=10)
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))
        product_id = request.GET.get('product_id')
        store_id = request.GET.get('store_id')

        reviews = Review.objects.filter(product_id=product_id, store_id = store_id)
          # Tính toán đánh giá trung bình
        average_rating = reviews.aggregate(average_rating=Avg('rating'))['average_rating'] or 0
        
        paginator = Paginator(reviews, page_size)

        try:
            paginated_reviews = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_reviews = paginator.page(1)
        except EmptyPage:
            paginated_reviews = paginator.page(paginator.num_pages)

        serializer = GetAllReviewSerializer(paginated_reviews, many=True)

        return Response({
            "status": status.HTTP_200_OK,
            "message": "OK",
            "data": {
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_index": page_index,
                "page_size": page_size,
                "average_rating": round(average_rating, 2),  # Đánh giá trung bình, làm tròn đến 2 chữ số
                "reviews": serializer.data
            }
        }, status=status.HTTP_200_OK)
        
            