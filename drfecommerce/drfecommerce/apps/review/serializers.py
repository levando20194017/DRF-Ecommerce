from rest_framework import serializers
from .models import Review, ReviewReply
from drfecommerce.apps.guest.serializers import GuestSerializerGetData
from drfecommerce.apps.product.serializers import ProductSerializer

class ReviewReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewReply
        fields = '__all__'
        
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
        
class GetAllReviewSerializer(serializers.ModelSerializer):
    replies = ReviewReplySerializer(many=True, read_only=True, source='reviewreply_set') 
    guest = GuestSerializerGetData(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'guest', 'product', 'store', 'rating', 'comment', 'gallery', 'created_at', 'updated_at', 'replies']
