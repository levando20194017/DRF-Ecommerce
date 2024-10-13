from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from drfecommerce.apps.guest import views as views_guest
from drfecommerce.apps.my_admin import views as views_admin
from drfecommerce.apps.catalog import views as views_catalog
from drfecommerce.apps.promotion import views as views_promotion
from drfecommerce.apps.product import views as views_product
from drfecommerce.settings import base
from django.conf.urls.static import static

router = DefaultRouter()

urlpatterns = [
    #guest
    path('api/login/',  views_guest.GuestViewSetLogin.as_view({'post': 'login'}), name='guest-login'),
    path('api/token/refresh/', views_guest.RefreshTokenView.as_view({'post': 'post'}), name='token_refresh'),
    path("api/guests/list-guests/", views_guest.GuestViewSetGetData.as_view({'get': 'list_guests'}), name='guest-list'),
    path("api/guests/guest-information/<int:id>/", views_guest.GuestViewSetGetData.as_view({'get': 'detail_guest'}), name='guest-information'),
    path("api/guests/register/", views_guest.GuestViewSetCreate.as_view({'post': 'create_guest'}), name='guest-register'),
    path("api/guests/change-information/", views_guest.GuestViewSetChangeInfor.as_view({'put': 'change_infor'}), name='change-information'),
    path("api/guests/change-avatar/", views_guest.ChangeAvatarAPI.as_view({'put': 'change_avatar'}), name='change-avatar'),
    
    #admin
    path("admin/", admin.site.urls),
    path('api/admin/login/',  views_admin.AdminViewSetLogin.as_view({'post': 'login'}), name='admin-login'),
    path('api/admin/token/refresh/', views_admin.RefreshTokenView.as_view({'post': 'post'}), name='admin_token_refresh'),
    path("api/admin/list-admins/", views_admin.AdminViewSetGetData.as_view({'get': 'list_admins'}), name='admin-list'),
    path("api/admin/admin-information/<int:id>/", views_admin.AdminViewSetGetData.as_view({'get': 'detail_admin'}), name='admin-information'),
    path("api/admin/get-list-guests/", views_admin.GuestViewSetGetData.as_view({'get': 'list_guests'}), name='admin-get-list-guests'),
    path("api/admin/upload-image/", views_admin.AdminViewsetUploadImage.as_view({'post': 'upload_image'}), name='admin-upload-image'),
    #catalog
    #---private
    path("api/admin/get-list-catalogs/", views_catalog.CatalogViewSetGetData.as_view({'get': 'list_catalogs'}), name='admin-get-list-catalogs'),
    path("api/admin/create-new-catalog/", views_catalog.CatalogViewSetCreateData.as_view({'post': 'create_catalog'}), name='admin-create-new-catalog'),
    path("api/admin/delete-catalog/", views_catalog.CatalogViewSetDeleteData.as_view({'delete': 'delete_catalog'}), name='admin-delete-catalog'),
    path("api/admin/restore-catalog/", views_catalog.CatalogViewSetRestoreData.as_view({'put': 'restore_catalog'}), name='admin-restore-catalog'),
    path("api/admin/edit-catalog/", views_catalog.CatalogViewSetEditData.as_view({'put': 'edit_catalog'}), name='admin-edit-catalog'),
    path("api/admin/get-detail-catalog/", views_catalog.CatalogViewSetGetData.as_view({'get': 'get_catalog'}), name='admin-get-detail-catalog'),
    path("api/admin/search-catalogs/", views_catalog.CatalogViewSetGetData.as_view({'get': 'search_catalogs'}), name='admin-search-catalogs'),
    #---public
    path("api/get-list-catalogs/", views_catalog.PublicCatalogViewSetGetData.as_view({'get': 'list_catalogs'}), name='get-list-catalogs'),
    path("api/search-catalogs/", views_catalog.PublicCatalogViewSetGetData.as_view({'get': 'search_catalogs'}), name='search-catalogs'),
    
    #promotion
    #---private
    path("api/admin/get-list-promotions/", views_promotion.PromotionViewSet.as_view({'get': 'list_promotions'}), name='admin-get-list-promotions'),
    path("api/admin/create-new-promotion/", views_promotion.PromotionViewSet.as_view({'post': 'create_promotion'}), name='admin-create-new-promotion'),
    path("api/admin/delete-promotion/", views_promotion.PromotionViewSet.as_view({'delete': 'delete_promotion'}), name='admin-delete-promotion'),
    path("api/admin/restore-promotion/", views_promotion.PromotionViewSet.as_view({'put': 'restore_promotion'}), name='admin-restore-promotion'),
    path("api/admin/edit-promotion/", views_promotion.PromotionViewSet.as_view({'put': 'edit_promotion'}), name='admin-edit-promotion'),
    path("api/admin/get-detail-promotion/", views_promotion.PromotionViewSet.as_view({'get': 'get_promotion'}), name='admin-get-detail-promotion'),
    path("api/admin/search-promotions/", views_promotion.PromotionViewSet.as_view({'get': 'search_promotions'}), name='admin-search-promotions'),
    #---public
    path("api/get-list-promotions/", views_promotion.PublicPromotionViewSet.as_view({'get': 'list_promotions'}), name='get-list-promotions'),
    path("api/get-detail-promotion/", views_promotion.PublicPromotionViewSet.as_view({'get': 'get_promotion'}), name='get-detail-promotion'),
    path("api/search-promotions/", views_promotion.PublicPromotionViewSet.as_view({'get': 'search_promotions'}), name='search-promotions'),
    
    #product
    #--public route
    path("api/get-list-products/", views_product.PublicProductViewset.as_view({'get': 'list_products'}), name='get-list-products'),
    path("api/get-detail-product/", views_product.PublicProductViewset.as_view({'get': 'get_product'}), name='get-detail-product'),
    path("api/get-list-products-by-catalog/", views_product.PublicProductViewset.as_view({'get': 'list_products_by_catalog'}), name='get-list-products-by-catalog'),
    path("api/get-list-products-by-promotion/", views_product.PublicProductViewset.as_view({'get': 'list_products_by_promotion'}), name='get-list-products-by-promotion'),
    path("api/search-products/", views_product.PublicProductViewset.as_view({'get': 'search_products'}), name='search-products'),
    #--private route
    path("api/admin/get-list-products/", views_product.ProductViewSet.as_view({'get': 'list_products'}), name='admin-get-list-products'),
    path("api/admin/create-new-product/", views_product.ProductViewSet.as_view({'post': 'create_product'}), name='admin-create-new-product'),
    path("api/admin/delete-product/", views_product.ProductViewSet.as_view({'delete': 'delete_product'}), name='admin-delete-product'),
    path("api/admin/restore-product/", views_product.ProductViewSet.as_view({'put': 'restore_product'}), name='admin-restore-product'),
    path("api/admin/edit-product/", views_product.ProductViewSet.as_view({'put': 'edit_product'}), name='admin-edit-product'),
    path("api/admin/upload-gallery/", views_product.ProductViewSet.as_view({'post': 'upload_gallery'}), name='admin-upload-images'),
    path("api/admin/search-products/", views_product.ProductViewSet.as_view({'get': 'search_products'}), name='admin-search-products'),
    
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/docs", SpectacularSwaggerView.as_view(url_name="schema")),
]+ static(base.MEDIA_URL, document_root=base.MEDIA_ROOT)