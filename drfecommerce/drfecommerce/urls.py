from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from drfecommerce.apps.guest import views as views_guest
from drfecommerce.apps.my_admin import views as views_admin
from drfecommerce.apps.catalog import views as views_catalog
from drfecommerce.apps.promotion import views as views_promotion
from drfecommerce.apps.product import views as views_product
from drfecommerce.apps.cart import views as views_cart
from drfecommerce.apps.store import views as views_store
from drfecommerce.apps.order import views as views_order
from drfecommerce.apps.review import views as views_review
from drfecommerce.apps.order_detail import views as views_order_detail
from drfecommerce.apps.product_incoming import views as views_product_incoming
from drfecommerce.apps.product_sale import views as views_product_sale
from drfecommerce.apps.product_store import views as views_product_store
from drfecommerce.apps.notification import views as views_notification
from drfecommerce.settings import base
from django.conf.urls.static import static

router = DefaultRouter()

urlpatterns = [
    #guest
    path('api/guest/login/',  views_guest.GuestViewSetLogin.as_view({'post': 'login'}), name='guest-login'),
    path('api/token/refresh/', views_guest.RefreshTokenView.as_view({'post': 'post'}), name='token_refresh'),
    path("api/guests/list-guests/", views_guest.GuestViewSetGetData.as_view({'get': 'list_guests'}), name='guest-list'),
    path("api/guests/guest-information/<int:id>/", views_guest.GuestViewSetGetData.as_view({'get': 'detail_guest'}), name='guest-information'),
    path("api/guests/register/", views_guest.GuestViewSetCreate.as_view({'post': 'create_guest'}), name='guest-register'),
    path("api/guests/change-information/", views_guest.GuestViewSetChangeInfor.as_view({'put': 'change_infor'}), name='change-information'),
    path("api/guests/change-avatar/", views_guest.ChangeAvatarAPI.as_view({'put': 'change_avatar'}), name='change-avatar'),
    #cart && cartItem
    path("api/cart/guests/add-to-cart/", views_cart.CartViewSet.as_view({'post': 'add_to_cart'}), name='add-to-cart'),
    path("api/cart/guests/my-cart/", views_cart.CartViewSet.as_view({'get': 'get_cart_items'}), name='get-cart-items'),
    path("api/cart/guests/update-cart-item/", views_cart.CartViewSet.as_view({'post': 'update_cart_item'}), name='update-cart-items'),
    path("api/cart/guests/remove-cart-item/", views_cart.CartViewSet.as_view({'post': 'remove_cart_item'}), name='remove-cart-items'),
    
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
    path("api/catalog/admin/get-list-catalogs/", views_catalog.CatalogViewSetGetData.as_view({'get': 'list_catalogs'}), name='admin-get-list-catalogs'),
    path("api/catalog/admin/create-new-catalog/", views_catalog.CatalogViewSetCreateData.as_view({'post': 'create_catalog'}), name='admin-create-new-catalog'),
    path("api/catalog/admin/delete-catalog/", views_catalog.CatalogViewSetDeleteData.as_view({'delete': 'delete_catalog'}), name='admin-delete-catalog'),
    path("api/catalog/admin/restore-catalog/", views_catalog.CatalogViewSetRestoreData.as_view({'put': 'restore_catalog'}), name='admin-restore-catalog'),
    path("api/catalog/admin/edit-catalog/", views_catalog.CatalogViewSetEditData.as_view({'put': 'edit_catalog'}), name='admin-edit-catalog'),
    path("api/catalog/admin/get-detail-catalog/", views_catalog.CatalogViewSetGetData.as_view({'get': 'get_catalog'}), name='admin-get-detail-catalog'),
    path("api/catalog/admin/search-catalogs/", views_catalog.CatalogViewSetGetData.as_view({'get': 'search_catalogs'}), name='admin-search-catalogs'),
    #---public
    path("api/catalog/get-list-catalogs/", views_catalog.PublicCatalogViewSetGetData.as_view({'get': 'list_catalogs'}), name='get-list-catalogs'),
    path("api/catalog/search-catalogs/", views_catalog.PublicCatalogViewSetGetData.as_view({'get': 'search_catalogs'}), name='search-catalogs'),
    
    #promotion
    #---private
    path("api/promotion/admin/get-list-promotions/", views_promotion.PromotionViewSet.as_view({'get': 'list_promotions'}), name='admin-get-list-promotions'),
    path("api/promotion/admin/create-new-promotion/", views_promotion.PromotionViewSet.as_view({'post': 'create_promotion'}), name='admin-create-new-promotion'),
    path("api/promotion/admin/delete-promotion/", views_promotion.PromotionViewSet.as_view({'delete': 'delete_promotion'}), name='admin-delete-promotion'),
    path("api/promotion/admin/restore-promotion/", views_promotion.PromotionViewSet.as_view({'put': 'restore_promotion'}), name='admin-restore-promotion'),
    path("api/promotion/admin/edit-promotion/", views_promotion.PromotionViewSet.as_view({'put': 'edit_promotion'}), name='admin-edit-promotion'),
    path("api/promotion/admin/get-detail-promotion/", views_promotion.PromotionViewSet.as_view({'get': 'get_promotion'}), name='admin-get-detail-promotion'),
    path("api/promotion/admin/search-promotions/", views_promotion.PromotionViewSet.as_view({'get': 'search_promotions'}), name='admin-search-promotions'),
    #---public
    path("api/promotion/get-list-promotions/", views_promotion.PublicPromotionViewSet.as_view({'get': 'list_promotions'}), name='get-list-promotions'),
    path("api/promotion/get-detail-promotion/", views_promotion.PublicPromotionViewSet.as_view({'get': 'get_promotion'}), name='get-detail-promotion'),
    path("api/promotion/search-promotions/", views_promotion.PublicPromotionViewSet.as_view({'get': 'search_promotions'}), name='search-promotions'),
    
    #product
    #--public route
    path("api/product/get-list-products/", views_product.PublicProductViewset.as_view({'get': 'list_products'}), name='get-list-products'),
    path("api/product/get-detail-product/", views_product.PublicProductViewset.as_view({'get': 'get_product'}), name='get-detail-product'),
    path("api/product/get-list-products-by-catalog/", views_product.PublicProductViewset.as_view({'get': 'list_products_by_catalog'}), name='get-list-products-by-catalog'),
    path("api/product/get-list-products-by-promotion/", views_product.PublicProductViewset.as_view({'get': 'list_products_by_promotion'}), name='get-list-products-by-promotion'),
    path("api/product/search-products/", views_product.PublicProductViewset.as_view({'get': 'search_products'}), name='search-products'),
    #--private route
    path("api/product/admin/get-list-products/", views_product.ProductViewSet.as_view({'get': 'list_products'}), name='admin-get-list-products'),
    path("api/product/admin/create-new-product/", views_product.ProductViewSet.as_view({'post': 'create_product'}), name='admin-create-new-product'),
    path("api/product/admin/delete-product/", views_product.ProductViewSet.as_view({'delete': 'delete_product'}), name='admin-delete-product'),
    path("api/product/admin/restore-product/", views_product.ProductViewSet.as_view({'put': 'restore_product'}), name='admin-restore-product'),
    path("api/product/admin/edit-product/", views_product.ProductViewSet.as_view({'put': 'edit_product'}), name='admin-edit-product'),
    path("api/product/admin/upload-gallery/", views_product.ProductViewSet.as_view({'post': 'upload_gallery'}), name='admin-upload-images'),
    path("api/product/admin/search-products/", views_product.ProductViewSet.as_view({'get': 'search_products'}), name='admin-search-products'),
    
    #product_incoming (liên quan đến sản phẩm nhập vào)
    path("api/product_incoming/admin/list-product-incomings/", views_product_incoming.ProductIncomingViewSet.as_view({'get': 'list_product_incomings'}), name='admin-get-list-product-incomings'),
    path("api/product_incoming/admin/create-product-incoming/", views_product_incoming.ProductIncomingViewSet.as_view({'post': 'add_product_incoming'}), name='admin-create-new-product-incoming'),
    path("api/product_incoming/admin/delete-product-incoming/", views_product_incoming.ProductIncomingViewSet.as_view({'delete': 'delete_product_incoming'}), name='admin-delete-product-incoming'),
    path("api/product_incoming/admin/detail-product-incoming/", views_product_incoming.ProductIncomingViewSet.as_view({'get': 'detail_product_incoming'}), name='admin-get-detail-product-incomings'),
    path("api/product_incoming/admin/search_product_incomings/", views_product_incoming.ProductIncomingViewSet.as_view({'get': 'search_product_incomings'}), name='admin-search-product-incomings'),
    path("api/product_incoming/admin/expenditure-statistics/", views_product_incoming.ProductIncomingViewSet.as_view({'get': 'expenditure_statistics'}), name='admin-get-expenditure-statistics'),
    
    #product_sale (Liên quan đến sản phẩm đã bán, thống kê nó)
    #thống kê của cửa hàng theo ngày. các số lượng đã bán
    path("api/product_sale/admin/get-all-products-sale/", views_product_sale.AdminProductSaleViewSet.as_view({'get': 'get_all_products_sale'}), name='admin-get-all-products-sale'),
    path("api/product_sale/admin/get-total-report/", views_product_sale.AdminProductSaleViewSet.as_view({'get': 'get_total_report'}), name='get-total-report'),
    #thống kê sản phẩm đã bán (số lượng đã bán trên mỗi sản phẩm)
    path("api/product_sale/admin/get-list-sold-products-filter/", views_product_sale.AdminProductSaleViewSet.as_view({'get': 'list_sold_products_filter'}), name='admin-get-list-sold-product-filter'),
    
    #store
    #--private route
    path("api/store/admin/get-list-stores/", views_store.StoreViewSet.as_view({'get': 'list_stores'}), name='admin-get-list-stores'),
    path("api/store/admin/search-stores/", views_store.StoreViewSet.as_view({'get': 'search_stores'}), name='admin-search-stores'),
    path("api/store/admin/create-new-store/", views_store.StoreViewSet.as_view({'post': 'create_store'}), name='admin-create-new-store'),
    path("api/store/admin/delete-store/", views_store.StoreViewSet.as_view({'delete': 'delete_store'}), name='admin-delete-store'),
    path("api/store/admin/restore-store/", views_store.StoreViewSet.as_view({'put': 'restore_store'}), name='admin-restore-store'),
    path("api/store/admin/edit-store/", views_store.StoreViewSet.as_view({'put': 'edit_store'}), name='admin-edit-store'),
    path("api/store/admin/get-detail-store/", views_store.StoreViewSet.as_view({'get': 'get_store'}), name='admin-get-detail-store'),

    #product_store
    #--private route
    path("api/product_store/admin/search-products-in-store/", views_product_store.ProductStoreViewSet.as_view({'get': 'search_products_in_store'}), name='admin-search-products-in-store'),
    path("api/product_store/admin/soft-delete-product-of-store/", views_product_store.ProductStoreViewSet.as_view({'delete': 'soft_delete'}), name='admin-delet-product-in-store'),
    #--public route
    #api hiển thị các cửa hàng chứa product
    path("api/product_store/search-stores-has-product/", views_product_store.PublicProductStoreViewSet.as_view({'get': 'search_stores_by_product'}), name='search-stores-has-product'),
    #api hiển thị thông tin chi tiết bao gồm product và store
    path("api/product_store/detail-of-product-and-store/", views_product_store.PublicProductStoreViewSet.as_view({'get': 'detail_product_store'}), name='detail-product-and-store'),
    
    #order
    #--private route
    path("api/order/create-new-order/", views_order.OrderViewSet.as_view({'post': 'create_new_order'}), name='create-new-order'),
    path("api/order/cancel-order/", views_order.OrderViewSet.as_view({'put': 'cancel_order'}), name='cancel-order'),
    path("api/order/get-list-orders/", views_order.OrderViewSet.as_view({'get': 'list_orders'}), name='get-list-orders'),
    path("api/order/get-order-detail/", views_order_detail.OrderDetailViewSet.as_view({'get': 'get_order_detail'}), name='get-order-detail'),
    path("api/order/admin/get-list-orders/", views_order.AdminOrderViewSet.as_view({'get': 'list_orders'}), name='admin-get-list-orders'),
    path("api/order/admin/update-order-status/", views_order.AdminOrderViewSet.as_view({'put': 'update_order_status'}), name='admin-update-order-status'),
    path("api/order/admin/update-payment-status/", views_order.AdminOrderViewSet.as_view({'put': 'update_payment_status'}), name='admin-update-payment-status'),
    
    #rating
    path("api/review/guest-review/", views_review.ReviewViewSet.as_view({'post': 'guest_review'}), name='guest-review'),
    path("api/review/admin-reply-review/", views_review.AdminReviewViewset.as_view({'post': 'admin_reply_review'}), name='admin-reply-review'),
    path("api/review/update-review/", views_review.ReviewViewSet.as_view({'put': 'update_review'}), name='update-review'),
    path("api/review/delete-review/", views_review.ReviewViewSet.as_view({'delete': 'delete_review'}), name='delete-review'),
    #---public route
    path("api/review/get-list-reviews/", views_review.PublicReviewViewset.as_view({'get': 'get_list_reviews'}), name='get-list-reviews'),
    
    #notifications
    path("api/notification/get-list-notifications/", views_notification.NotificationViewSet.as_view({'get': 'list_notifications'}), name='get-list-notifications'),
    path("api/notification/read-notification/", views_notification.NotificationViewSet.as_view({'put': 'read_notification'}), name='read-notification'),
    
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/docs", SpectacularSwaggerView.as_view(url_name="schema")),
]+ static(base.MEDIA_URL, document_root=base.MEDIA_ROOT)