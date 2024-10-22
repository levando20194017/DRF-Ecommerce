from rest_framework import serializers
from .models import Review, ReviewReply

class ReviewReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewReply
        fields = '__all__'
        
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
        
class GetAllReviewSerializer(serializers.ModelSerializer):
    replies = ReviewReplySerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'guest', 'product', 'store', 'rating', 'comment', 'gallery', 'created_at', 'updated_at', 'replies']
