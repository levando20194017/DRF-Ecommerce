from .base import *
# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases


# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }


#local
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'EcommerceDjango',  # Tên database
#         'USER': 'postgres',  # Tên người dùng của DB
#         'PASSWORD': '123456',  # Mật khẩu của DB
#         'HOST': 'localhost',  # Hostname, thường là localhost
#         'PORT': '5432',  # Cổng mặc định của PostgreSQL là 5432
#     }
# }

#supabase
#postgresql://postgres:[YOUR-PASSWORD]@db.xdgoxqscdzswkdvengoi.supabase.co:5432/postgres
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',  # Tên database
        'USER': 'postgres.xdgoxqscdzswkdvengoi',  # Tên người dùng của DB
        'PASSWORD': os.environ.get("DB_PASSWORD"),  # Mật khẩu của DB
        'HOST': 'aws-0-ap-southeast-1.pooler.supabase.com',  # Hostname, thường là localhost
        'PORT': '5432',  # Cổng mặc định của PostgreSQL là 5432
    }
}
