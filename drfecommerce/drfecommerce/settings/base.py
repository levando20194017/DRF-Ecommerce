from pathlib import Path
from dotenv import load_dotenv
import os
from datetime import timedelta

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = True


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # External Packages
    "rest_framework",
    "drf_spectacular",
    "mptt",
    "rest_framework_simplejwt",
    "drf_yasg",
    
    # Internal Apps
    # "drfecommerce.product",
    "drfecommerce.apps.guest",
    "drfecommerce.apps.blog",
    "drfecommerce.apps.blog_tag",
    "drfecommerce.apps.catalog",
    "drfecommerce.apps.category",
    "drfecommerce.apps.my_admin",
    "drfecommerce.apps.cart",
    "drfecommerce.apps.order",
    "drfecommerce.apps.order_detail",
    "drfecommerce.apps.payment",
    "drfecommerce.apps.product",
    "drfecommerce.apps.review",
    "drfecommerce.apps.notification",
    "drfecommerce.apps.product_store",
    "drfecommerce.apps.product_incoming",
    "drfecommerce.apps.product_sale",
    "drfecommerce.apps.promotion",
    "drfecommerce.apps.setting",
    "drfecommerce.apps.shipping",
    "drfecommerce.apps.store",
    "drfecommerce.apps.tag",
    "drfecommerce.apps.transaction",
]

CORS_ALLOW_CREDENTIALS = True # to accept cookies via ajax request
CORS_ORIGIN_WHITELIST = [
    '*' # the domain for front-end app(you can add more than 1) 
]

# Đường dẫn cục bộ cho việc lưu trữ ảnh
ECOMMERCE_IMAGES_DIR = os.path.join(BASE_DIR, 'C:/Users/Mine/Documents/document/PROJECT/DATN/Ecommerce_Images')

# Cấu hình storage mặc định để lưu trữ file cục bộ
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
MEDIA_ROOT = ECOMMERCE_IMAGES_DIR
MEDIA_URL = '/media/'  # Nếu bạn cần phục vụ ảnh từ URL

#config storage to save image in the future
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# # Thông tin kết nối AWS S3
# AWS_ACCESS_KEY_ID = 'your-access-key-id'
# AWS_SECRET_ACCESS_KEY = 'your-secret-access-key'
# AWS_STORAGE_BUCKET_NAME = 'your-bucket-name'

# # Region của S3 (nếu có)
# AWS_S3_REGION_NAME = 'your-region'

# # URL sẽ được sử dụng để truy cập file từ S3
# AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
# MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "drfecommerce.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, 'templates')],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "drfecommerce.wsgi.application"


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

TIME_ZONE = 'Asia/Ho_Chi_Minh'  # Thiết lập múi giờ Việt Nam
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=500),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'drfecommerce.apps.guest.authentication.GuestSafeJWTAuthentication',
        'drfecommerce.apps.my_admin.authentication.AdminSafeJWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),

    # 'DEFAULT_AUTHENTICATION_CLASSES': [
    #     'rest_framework_simplejwt.authentication.JWTAuthentication',
    # ],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Django DRF Ecommerce",
}

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587  # hoặc 465 nếu cần SSL
# EMAIL_USE_TLS = False  # hoặc False nếu không cần TLS
# EMAIL_HOST_USER = os.environ.get("EMAIL")
# EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASSWORD")

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Use SMTP backend
EMAIL_HOST = 'smtp.gmail.com'  # e.g., smtp.gmail.com for Gmail
EMAIL_PORT = 587  # or 465 for SSL
EMAIL_USE_TLS = True  # Set to True for TLS; False for SSL
EMAIL_USE_SSL = False  # Set to True for TLS; False for SSL
EMAIL_HOST_USER = os.environ.get("EMAIL")  # Your email address
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASSWORD")  # Your email password
DEFAULT_FROM_EMAIL = 'VIVAFLOWER <no-reply@yourdomain.com>'
ADMIN_EMAIL = 'levando20194017@gmail.com'  # Admin email for notifications
