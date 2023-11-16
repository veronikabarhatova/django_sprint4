from django.shortcuts import get_object_or_404
from django.db.models import Count
from .models import Post


def get_post(post_id):
    return get_object_or_404(
        Post.published_objects.all(),
        pk=post_id
    )


def count_comments(model, field):
    return model.annotate(count=Count(field))
