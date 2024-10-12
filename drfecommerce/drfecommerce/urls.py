from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from drfecommerce.apps.guest import views as views_guest
from drfecommerce.apps.my_admin import views as views_admin
from drfecommerce.apps.catalog import views as views_catalog
from drfecommerce.apps.promotion import views as views_promotion

router = DefaultRouter()

urlpatterns = [
    #admin
    path("admin/", admin.site.urls),
    path('api/admin/login/',  views_admin.AdminViewSetLogin.as_view({'post': 'login'}), name='admin-login'),
    path('api/admin/token/refresh/', views_admin.RefreshTokenView.as_view({'post': 'post'}), name='admin_token_refresh'),
    path("api/admin/list-admins/", views_admin.AdminViewSetGetData.as_view({'get': 'list_admins'}), name='admin-list'),
    path("api/admin/admin-information/<int:id>/", views_admin.AdminViewSetGetData.as_view({'get': 'detail_admin'}), name='admin-information'),
    path("api/admin/get-list-guests/", views_admin.GuestViewSetGetData.as_view({'get': 'list_guests'}), name='admin-get-list-guests'),
    ###catalog
    path("api/admin/get-list-catalogs/", views_catalog.CatalogViewSetGetData.as_view({'get': 'list_catalogs'}), name='admin-get-list-catalogs'),
    path("api/admin/create-new-catalog/", views_catalog.CatalogViewSetCreateData.as_view({'post': 'create_catalog'}), name='admin-create-new-catalog'),
    path("api/admin/delete-catalog/", views_catalog.CatalogViewSetDeleteData.as_view({'delete': 'delete_catalog'}), name='admin-delete-catalog'),
    path("api/admin/restore-catalog/", views_catalog.CatalogViewSetRestoreData.as_view({'put': 'restore_catalog'}), name='admin-restore-catalog'),
    path("api/admin/edit-catalog/", views_catalog.CatalogViewSetEditData.as_view({'put': 'edit_catalog'}), name='admin-edit-catalog'),
    ####promotion
    path("api/admin/get-list-promotions/", views_promotion.PromotionViewSet.as_view({'get': 'list_promotions'}), name='admin-get-list-promotions'),
    path("api/admin/create-new-promotion/", views_promotion.PromotionViewSet.as_view({'post': 'create_promotion'}), name='admin-create-new-promotion'),
    path("api/admin/delete-promotion/", views_promotion.PromotionViewSet.as_view({'delete': 'delete_promotion'}), name='admin-delete-promotion'),
    path("api/admin/restore-promotion/", views_promotion.PromotionViewSet.as_view({'put': 'restore_promotion'}), name='admin-restore-promotion'),
    path("api/admin/edit-promotion/", views_promotion.PromotionViewSet.as_view({'put': 'edit_promotion'}), name='admin-edit-promotion'),
    path("api/admin/get-detail-promotion/", views_promotion.PromotionViewSet.as_view({'get': 'get_promotion'}), name='admin-get-detail-promotion'),
    #guest
    path('api/login/',  views_guest.GuestViewSetLogin.as_view({'post': 'login'}), name='guest-login'),
    path('api/token/refresh/', views_guest.RefreshTokenView.as_view({'post': 'post'}), name='token_refresh'),
    path("api/guests/list-guests/", views_guest.GuestViewSetGetData.as_view({'get': 'list_guests'}), name='guest-list'),
    path("api/guests/guest-information/<int:id>/", views_guest.GuestViewSetGetData.as_view({'get': 'detail_guest'}), name='guest-information'),
    path("api/guests/register/", views_guest.GuestViewSetCreate.as_view({'post': 'create_guest'}), name='guest-register'),
    path("api/guests/change-information/", views_guest.GuestViewSetChangeInfor.as_view({'put': 'change_infor'}), name='change-information'),
    path("api/guests/change-avatar/", views_guest.ChangeAvatarAPI.as_view({'put': 'change_avatar'}), name='change-avatar'),
    
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/docs", SpectacularSwaggerView.as_view(url_name="schema")),
]
