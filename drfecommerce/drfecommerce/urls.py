from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from drfecommerce.apps.guest import views as views_guest

# from drfecommerce.product import views

router = DefaultRouter()
router.register(r'users', views_guest.GuestViewSetCreate, basename='guests-register')

# router.register(r"category", views.CategoryViewSet)
# router.register(r"brand", views.BrandViewSet)
# router.register(r"product", views.ProductViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    
    path('api/login/',  views_guest.GuestViewSetLogin.as_view({'post': 'login'}), name='guest-login'),
    path('api/token/refresh/', views_guest.RefreshTokenView.as_view({'post': 'post'}), name='token_refresh'),
    
    #guest
    path("api/guests/list-guests/", views_guest.GuestViewSetGetData.as_view({'get': 'list_guests'}), name='guest-list'),
    path("api/guests/guest-information/<int:id>/", views_guest.GuestViewSetGetData.as_view({'get': 'detail_guest'}), name='guest-information'),
    path("api/guests/register/", views_guest.GuestViewSetCreate.as_view({'post': 'create_guest'}), name='guest-register'),
    path("api/guests/change-information/", views_guest.GuestViewSetChangeInfor.as_view({'put': 'change_infor'}), name='change-information'),
    path("api/guests/change-avatar/", views_guest.ChangeAvatarAPI.as_view({'put': 'change_avatar'}), name='change-avatar'),
    
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/docs", SpectacularSwaggerView.as_view(url_name="schema")),
]
