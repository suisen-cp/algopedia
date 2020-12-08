from django.contrib import admin
from cms.models import *

# Register your models here.


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('article_id', 'title', 'fav_num', 'created_at', 'updated_at')
    list_display_links = ('title',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'article')


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('article', 'user')


class ReadingHistoryAdmin(admin.ModelAdmin):
    list_display = ('article', 'user', 'updated_at')


class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ('article', 'category')


class ArticleTagsAdmin(admin.ModelAdmin):
    list_display = ('article', 'tag')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category', 'article_num')


class TagAdmin(admin.ModelAdmin):
    list_display = ('tag', 'article_num')


admin.site.register(Article, ArticleAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(ReadingHistory, ReadingHistoryAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(ArticleCategory, ArticleCategoryAdmin)
admin.site.register(ArticleTags, ArticleTagsAdmin)
