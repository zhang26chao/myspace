# !-*-coding=utf8-*-
from ckeditor.fields import RichTextField
from django.db import models
import util

# Create your models here.
class Tag(models.Model):
    name = models.CharField('名称', max_length=20)
    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'
    
    def __unicode__(self):
        return self.name
    
class Article(models.Model):
    title = models.CharField('标题', max_length=100)
    image = models.ImageField('插图', upload_to="article/origin", max_length=1000, null=True, blank=True)
    thumbnail = models.ImageField(upload_to="article/thumb", null=True, blank=True)
    micro = models.ImageField(upload_to="article/micro", null=True, blank=True)
    content = RichTextField('内容')
    create_time = models.DateTimeField('创建日期', auto_now_add=True, auto_now=False)
    tags = models.ManyToManyField(Tag, null=True, verbose_name='标签')
    
    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'
        ordering = ['-create_time']
    
    def __unicode__(self):
        return self.title
    
    def getCommentCount(self):
        return self.comment_set.all().count()
    
    def save(self):
        if self.image:
            tmp = util.thumbnail(self.image, 120, 120);
            self.thumbnail.save(tmp.name + '.png', tmp, save=False)
            tmp = util.thumbnail(self.image, 58, 42)
            self.micro.save(tmp.name + '.png', tmp, save=False)
        super(Article, self).save(False, False)
    
class Comment(models.Model):
    email = models.CharField('电子邮箱', max_length=100)
    nickname = models.CharField('昵称', max_length=100)
    content = RichTextField('内容')
    create_time = models.DateTimeField('创建日期', auto_now_add=True, auto_now=False)
    article = models.ForeignKey(Article, verbose_name='文章')
    
    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['-create_time']
    
    def __unicode__(self):
        return self.email

class Message(models.Model):
    email = models.CharField('电子邮箱', max_length=100)
    nickname = models.CharField('昵称', max_length=100)
    content = RichTextField('内容')
    create_time = models.DateTimeField('创建日期', auto_now_add=True, auto_now=False)
    
    class Meta:
        verbose_name = '留言'
        verbose_name_plural = '留言'
        ordering = ['-create_time']
    
    def __unicode__(self):
        return self.email

class PhotoTag(models.Model):
    name = models.CharField('名称', max_length=20)
    
    class Meta:
        verbose_name = '照片标签'
        verbose_name_plural = '照片标签'
    
    def __unicode__(self):
        return self.name

class Photo(models.Model):
    title = models.CharField('标题', max_length=100)
    image = models.ImageField('图片', upload_to="photo/original/%Y/%m/%d", max_length=1000)
    thumbnail = models.ImageField(upload_to="photo/thumb/%Y/%m/%d", null=True, blank=True)
    create_time = models.DateTimeField('创建日期', auto_now_add=True, auto_now=False)
    tags = models.ManyToManyField(PhotoTag, verbose_name='标签')
    
    class Meta:
        verbose_name = '照片'
        verbose_name_plural = '照片'
        ordering = ['-create_time']
    
    def __unicode__(self):
        return self.title
    
    def save(self):
        if self.image:
            suf = util.thumbnail(self.image, 120, 85)
            self.thumbnail.save(suf.name + '.png', suf, save=False)
        super(Photo, self).save(False, False)
