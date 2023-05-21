from rest_framework import serializers
from .models import Blog, Like
from django.urls import reverse

class LikeSerializer(serializers.ModelSerializer):
    blog = serializers.StringRelatedField(read_only=True)
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
            model = Like
            fields = "__all__"


class BlogSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    likes = serializers.SerializerMethodField()
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Blog
        fields = "__all__"

    def get_likes(self, obj):
        likes = Like.objects.filter(blog=obj)[:3]
        likes_count = Like.objects.filter(blog=obj).count()
        request = self.context.get('request')
        return {
            "likes": LikeSerializer(likes, many=True).data,
            "count": likes_count
        }
