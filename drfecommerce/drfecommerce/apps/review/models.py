from django.db import models
from drfecommerce.apps.guest.models import Guest
from drfecommerce.apps.product.models import Product
from drfecommerce.apps.order_detail.models import OrderDetail
from drfecommerce.apps.store.models import Store
from django.utils import timezone

class Review(models.Model):
    id = models.AutoField(primary_key=True)
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)  # The user submitting the review
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # The product being reviewed
    store = models.ForeignKey(Store, on_delete=models.CASCADE)  # The store being reviewed
    order_detail = models.ForeignKey(OrderDetail, on_delete=models.SET_NULL, null=True, blank=True)  # Link to the order detail
    rating = models.IntegerField()  # Rating, e.g., 1-5 stars
    comment = models.TextField(blank=True, null=True)  # Optional review comment
    gallery = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)  # Review submission date
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Review {self.id} by {self.guest} for {self.product}'