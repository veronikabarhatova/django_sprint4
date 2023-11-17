from django.db.models import Count


def count_comments(queryset):
    return queryset.annotate(comment_count=Count('comments', distinct=True))
