from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, serializers
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Blog, Like
from .serializers import BlogSerializer, LikeSerializer
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadonly
from rest_framework.permissions import IsAuthenticated

class BlogListCreateView(generics.ListCreateAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_public']
    search_fields = ['^blog_title', 'blog_description']

    def create(self, request, *args, **kwargs):
        serializer = BlogSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class BlogDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    lookup_field = 'id'
    permission_classes = [IsOwnerOrReadonly, IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset().filter(Q(is_public=True) | Q(author=user))
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        print(serializer.data)
        if instance:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'Message': 'No blog Found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, *args, **kwargs):
        blog = self.get_object()
        if blog is None:
            return Response({'Message': 'No blog Found Or not belong to you'}, status=status.HTTP_404_NOT_FOUND)
        if blog.author != request.user:
            raise serializers.ValidationError({"Message": "You are not authorized to perform this action"}, status=status.HTTP_401_UNAUTHORIZED)
        return super().delete(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        blog = self.get_object()
        if blog is None:
            return Response({'Message': 'No blog Found Or not belong to you'}, status=status.HTTP_404_NOT_FOUND)
        if blog.author != request.user:
            raise serializers.ValidationError({"Message": "You are not authorized to perform this action"}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(blog, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)



class BlogLikeListCreateView(generics.ListCreateAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        blog_id = self.kwargs.get('blog_id')
        return Blog.objects.filter(id=blog_id)

    def perform_create(self, serializer):
        blog_id = self.kwargs.get('blog_id')
        blog = get_object_or_404(Blog, id=blog_id)
        user = self.request.user
        if Like.objects.filter(blog=blog, author=user).exists():
            existing_like = Like.objects.get(blog=blog, author=user)
            existing_like.delete()  # Delete the existing like
            return;
        serializer.save(author=user, blog=blog)