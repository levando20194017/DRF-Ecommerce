from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Blog
from .serializers import BlogSerializer
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from rest_framework.permissions import IsAuthenticated, AllowAny
from drfecommerce.apps.my_admin.authentication import AdminSafeJWTAuthentication
from drfecommerce.apps.my_admin.models import MyAdmin
from drfecommerce.apps.category.models import Category
from drfecommerce.apps.blog_tag.models import BlogTag
from drfecommerce.apps.tag.models import Tag
from rest_framework.decorators import action, permission_classes, authentication_classes
from django.db.models import Prefetch
# Create your views here.
class BlogViewSet(viewsets.ViewSet):
    authentication_classes = [AdminSafeJWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path="create-new-blog")
    def create_blog(self, request):
        """
        Create a new category: body data
        - admin_id: int
        - category_id: int
        - title: string
        - slug: string
        - short_description: string
        - content: string
        - image: string
        - tag_ids: string (chuỗi nối với nhau bởi dấu phẩy)
        """
        admin_id = request.data.get('admin_id')
        category_id = request.data.get('category_id')
        title = request.data.get('title')
        slug = request.data.get('slug')
        short_description = request.data.get('short_description')
        content = request.data.get('content')
        image = request.data.get('image')
        tag_ids = request.data.get('tag_ids')
        
        # Kiểm tra xem `title` đã tồn tại hay chưa
        if Blog.objects.filter(title=title).exists():
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Blog name already exists."
            })

        # Kiểm tra xem `slug` đã tồn tại hay chưa
        if Blog.objects.filter(slug=slug).exists():
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Blog slug already exists."
            })
        
        try:
            admin = MyAdmin.objects.get(id=admin_id)
            category = Category.objects.get(id=category_id)
        except Exception as e:
            return Response({
                "status": 400,
                "message": f"Error: {str(e)}"
            })
        try:
            blog = Blog.objects.create(
                admin=admin,
                category = category,
                title = title,
                slug = slug,
                short_description = short_description,
                content = content,
                image = image
            )
            blog.save()
            #xử lí nối vào bảng BlogTag nếu tag_ids tồn tại
            if tag_ids and isinstance(tag_ids, list):
                for tag_id in tag_ids:
                    tag = Tag.objects.filter(id=tag_id).first()  # Kiểm tra tag có tồn tại
                    if tag:
                        BlogTag.objects.create(blog=blog, tag=tag)
            
            return Response({
                "status": 200,
                "message": "category created successfully!",
                "data": {
                    "id": blog.id,
                    "name": blog.title,
                }
            })
        except Exception as e:
            return Response({
                "status":400,
                "message": str(e)
            })

    @action(detail=False, methods=['put'], url_path="update-blog")
    def update_blog(self, request):
        """
        Update an existing blog: body data
        - blog_id: int
        - admin_id: int
        - category_id: int
        - title: string
        - slug: string
        - short_description: string
        - content: string
        - image: string
        - tag_ids: string (chuỗi nối với nhau bởi dấu phẩy)
        """
        # x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        # if x_forwarded_for:
        #     # Trường hợp có nhiều proxy, IP thực sẽ là cái đầu tiên trong chuỗi
        #     ip = x_forwarded_for.split(',')[0].strip()
        # else:
        #     # Nếu không qua proxy, lấy IP trực tiếp từ REMOTE_ADDR
        #     ip = request.META.get('REMOTE_ADDR')
        # print(ip)
        
        blog_id = request.data.get('blog_id')
        admin_id = request.data.get('admin_id')
        category_id = request.data.get('category_id')
        title = request.data.get('title')
        slug = request.data.get('slug')
        short_description = request.data.get('short_description')
        content = request.data.get('content')
        image = request.data.get('image')
        tag_ids = request.data.get('tag_ids')
        
        if not blog_id:
            return Response({
                "status": 400,
                "message": "Blog ID is required."
            })
            
        # Kiểm tra xem title đã tồn tại trên các blog khác chưa
        if Blog.objects.filter(title=title).exclude(id=blog_id).exists():
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Blog title already exists."
            })

        # Kiểm tra xem slug đã tồn tại trên các blog khác chưa
        if Blog.objects.filter(slug=slug).exclude(id=blog_id).exists():
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Blog slug already exists."
            })

        try:
            blog = Blog.objects.get(id=blog_id)
            # admin = MyAdmin.objects.get(id=admin_id)
            category = Category.objects.get(id=category_id)

            # Cập nhật các trường của blog'
            blog.category = category
            blog.title = title
            blog.slug = slug
            blog.short_description = short_description
            blog.content = content
            blog.image = image
            blog.save()

            # Xóa cứng các liên kết trong BlogTag trước khi thêm liên kết mới
            BlogTag.objects.filter(blog=blog).delete()

            # Xử lý nối vào bảng BlogTag nếu tag_ids tồn tại
            if tag_ids and len(tag_ids) > 0:
                for tag_id in tag_ids:
                    tag = Tag.objects.filter(id=tag_id).first()
                    if tag:
                        BlogTag.objects.create(blog=blog, tag=tag)

            return Response({
                "status": 200,
                "message": "Blog updated successfully!",
                "data": {
                    "id": blog.id,
                    "title": blog.title,
                }
            })

        except Blog.DoesNotExist:
            return Response({
                "status": 404,
                "message": "Blog not found."
            })
        except Exception as e:
            return Response({
                "status": 400,
                "message": str(e)
            })

    @action(detail=False, methods=['delete'], url_path="delete-blog")
    def delete_blog(self, request):
        """
        Hard delete a Blog:
        - query_params: blog_id
        """
        blog_id = request.query_params.get('blog_id')
        if not blog_id:
            return Response({
                "status": 400,
                "message": "Blog ID is required."
            })

        try:
            # Xóa tất cả các BlogTag liên kết với Blog
            BlogTag.objects.filter(blog_id=blog_id).delete()
            
            # Xóa cứng Blog
            blog = Blog.objects.get(id=blog_id)
            blog.delete()

            return Response({
                "status": status.HTTP_200_OK,
                "message": "Blog deleted successfully!"
            }, status=status.HTTP_200_OK)

        except Blog.DoesNotExist:
            return Response({
                "status": 404,
                "message": "Blog not found."
            })
        except Exception as e:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            })
        
    @action(detail=False, methods=['put'], url_path="restore-blog")
    def restore_blog(self, request):
        """
        Restore a blog and its child catalogs: body data:
        - id
        """
        blog_id = request.data.get('id')
        
        if not blog_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Blog ID is required."
            })

        try:
            blog = Blog.objects.get(id=blog_id, delete_at__isnull=False)
        except Blog.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Blog not found or already restored."
            })

        blog.delete_at = None
        blog.save()

        return Response({
            "status": status.HTTP_200_OK,
            "message": "Blog restored successfully."
        }, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['get'], url_path="get-detail-blog")
    def get_blog(self, request):
        """
        Get category details: body data:
        - blog_id
        """
        blog_id = request.query_params.get('blog_id')
        if not blog_id:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Blog ID is required."
            })

        try:
            blog = Blog.objects.get(id=blog_id)
            serializer = BlogSerializer(blog)
            
            blog_tags = BlogTag.objects.filter(blog_id = blog_id, delete_at__isnull=True)
            
            tag_ids = blog_tags.values_list('tag__id', flat=True)
            tag_names = blog_tags.values_list('tag__name', flat=True)
            
            # Create comma-separated strings
            tags = ','.join(map(str, tag_ids))
            tag_names_str = ','.join(tag_names)
            
            # Add to response data
            response_data = serializer.data
            response_data['tags'] = tags
            response_data['tag_names'] = tag_names_str

            return Response({
                "status": status.HTTP_200_OK,
                "data": response_data
            }, status=status.HTTP_200_OK)
        
        except Category.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Category not found."
            })
            
    @action(detail=False, methods=['get'], url_path="search-blogs")
    def search_blogs(self, request):
        """
        API to search blogs by name or tag with pagination.
        - page_index (default=1)
        - page_size (default=10)
        - name: blog name to search
        - tag: tag to search for
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))
        name_query = request.GET.get('name', '').strip()
        tag_query = request.GET.get('tag', '').strip()

        # Start with all blogs
        blogs = Blog.objects.all().order_by("-updated_at")
        # Filter by name if provided
        if name_query:
            blogs = blogs.filter(name__icontains=name_query)

        # Filter by tag if provided
        if tag_query:
            blogs = blogs.filter(blogtag__tag__name__icontains=tag_query).distinct()
            
        blogs = blogs.prefetch_related(
                Prefetch('blogtag_set__tag'),
                'category'
            )
        
        paginator = Paginator(blogs, page_size)

        try:
            paginated_blogs = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_blogs = paginator.page(1)
        except EmptyPage:
            paginated_blogs = paginator.page(paginator.num_pages)

        serializer = BlogSerializer(paginated_blogs, many=True)

        return Response({
            "status": status.HTTP_200_OK,
            "message": "OK",
            "data": {
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_index": page_index,
                "page_size": page_size,
                "blogs": serializer.data
            }
        }, status=status.HTTP_200_OK)
            
@authentication_classes([])
@permission_classes([AllowAny]) 
class PublicBlogViewSet(viewsets.ViewSet):     
    @action(detail=False, methods=['get'], url_path="search-blogs")
    def search_blogs(self, request):
        """
        API to search blogs by name or tag with pagination.
        - page_index (default=1)
        - page_size (default=10)
        - name: blog name to search
        - tag: tag to search for
        - order_by_field: 'views' or 'updated_at' (default='updated_at')
        """
        page_index = int(request.GET.get('page_index', 1))
        page_size = int(request.GET.get('page_size', 10))
        name_query = request.GET.get('name', '').strip()
        tag_query = request.GET.get('tag', '').strip()
        order_by_field = request.GET.get('order_by', 'updated_at').strip()  # Default to 'updated_at'

        # Start with all blogs
        blogs = Blog.objects.filter(delete_at__isnull = True)
        blogs = blogs.order_by('-updated_at')
        # Filter by name if provided
        if name_query:
            blogs = blogs.filter(name__icontains=name_query)

        # Filter by tag if provided
        if tag_query:
            blogs = blogs.filter(blogtag__tag__name__icontains=tag_query).distinct()

          # Order by specified field
        if order_by_field == 'views':
            blogs = blogs.order_by('-views')  # Sắp xếp giảm dần theo views
        else:
            blogs = blogs.order_by('-updated_at')  # Sắp xếp giảm dần theo ngày cập nhật (mặc định)
        
        paginator = Paginator(blogs, page_size)

        try:
            paginated_blogs = paginator.page(page_index)
        except PageNotAnInteger:
            paginated_blogs = paginator.page(1)
        except EmptyPage:
            paginated_blogs = paginator.page(paginator.num_pages)

        serializer = BlogSerializer(paginated_blogs, many=True)

        return Response({
            "status": status.HTTP_200_OK,
            "message": "OK",
            "data": {
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_index": page_index,
                "page_size": page_size,
                "blogs": serializer.data
            }
        }, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['get'], url_path="get-detail-blog")
    def get_blog(self, request):
        """
        Get category details: body data:
        - slug: string
        """
        # blog_id = request.query_params.get('blog_id')
        slug = request.query_params.get('slug')
        if not slug:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "slug is required."
            })

        try:
            blog = Blog.objects.get(slug=slug)
            serializer = BlogSerializer(blog)
            
            blog_tags = BlogTag.objects.filter(blog_id = blog.id, delete_at__isnull=True)
            
            tag_ids = blog_tags.values_list('tag__id', flat=True)
            tag_names = blog_tags.values_list('tag__name', flat=True)
            
            # Create comma-separated strings
            tags = ','.join(map(str, tag_ids))
            tag_names_str = ','.join(tag_names)
            
            # Add to response data
            response_data = serializer.data
            response_data['tags'] = tags
            response_data['tag_names'] = tag_names_str
            
            blog.views += 1
            blog.save(update_fields=['views'])

            return Response({
                "status": status.HTTP_200_OK,
                "data": response_data
            }, status=status.HTTP_200_OK)
        
        except Category.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Category not found."
            })