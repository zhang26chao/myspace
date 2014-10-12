from django.contrib import admin
from blog.models import Article
from blog.models import Tag
from blog.models import Comment
from blog.models import Message
from blog.models import PhotoTag
from blog.models import Photo
# Register your models here.
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'create_time')
    search_fields = ('title',)
    fields = ('title','image','tags', 'content')

class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title','create_time')
    search_fields = ('title',)
    fields = ('title','image','tags')
    
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('email','nickname','content','create_time')
    search_fields = ('email','nickname')

class MessageAdmin(admin.ModelAdmin):
    list_display = ('email','nickname','content','create_time')
    search_fields = ('email','nickname')

admin.site.register(Article,ArticleAdmin)
admin.site.register(Tag,TagAdmin)
admin.site.register(Comment,CommentAdmin)
admin.site.register(Message,MessageAdmin)
admin.site.register(PhotoTag)
admin.site.register(Photo,PhotoAdmin)