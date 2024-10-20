from rest_framework import viewsets
from .models import OrderDetail
from .serializers import OrderDetailSerializer

class OrderDetailViewSet(viewsets.ModelViewSet):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer

    def create(self, request):
        # Step 1: Validate and create order detail
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order_detail = serializer.save()

        # Step 2: Respond with created order detail
        return Response(serializer.data, status=status.HTTP_201_CREATED)
