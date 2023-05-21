from django.urls import path
from . import views

urlpatterns = [
    path("blog_list/", views.BlogListCreateView.as_view(), name="blog_list"),
    path("blog_detail/<int:id>/", views.BlogDetailView.as_view(), name="blog_list"),

    path("blog_like_list/blog/<int:blog_id>/", views.BlogLikeListCreateView.as_view(), name="blog_like_list"),
]
