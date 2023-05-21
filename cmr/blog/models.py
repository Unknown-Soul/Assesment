import random
import string
from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

class Blog(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    blog_title = models.CharField(max_length=100)
    blog_description = models.TextField()
    post_date = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)
    slug = models.CharField(max_length=1000, null=True, blank=True)
    likes = models.ManyToManyField(User, related_name="liked_blogs", blank=True)

    def __str__(self):
        return self.blog_title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.blog_title + " " + self.author.username)
            self.slug = base_slug + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))
        super().save(*args, **kwargs)

    def total_likes(self):
        return self.likes.count()


class Like(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    like_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Like by {self.user.username} on {self.blog.blog_title}"
