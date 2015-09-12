from django.contrib import admin
from blog.models import Category, Post, Comment, Tag


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

admin.site.register(Category, CategoryAdmin)


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'category', 'title')
    search_fields = ('title', 'content')

admin.site.register(Post, PostAdmin)


admin.site.register(Comment)
admin.site.register(Tag)
