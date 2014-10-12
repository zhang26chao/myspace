# !-*-coding=utf8-*-
from StringIO import StringIO
import os
from PIL import Image
from ckeditor.fields import RichTextField
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models


# import re
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
    image = models.ImageField('插图', upload_to="article/logo", max_length=1000, null=True, blank=True)
    content = RichTextField('内容')
    create_time = models.DateTimeField('创建日期', auto_now_add=True, auto_now=False)
    tags = models.ManyToManyField(Tag, null=True, verbose_name='标签')
    
    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'
    
    def __unicode__(self):
        return self.title
    
    def getCommentCount(self):
        return self.comment_set.all().count()
    
#     def save(self):
#         imgs = re.compile('.*<img.*src="(.*?)"', re.M).findall(self.content)
#         self.img = imgs[0] if imgs else ''
#         super(Article, self).save()
    
class Comment(models.Model):
    email = models.CharField('电子邮箱', max_length=100)
    nickname = models.CharField('昵称', max_length=100)
    content = RichTextField('内容')
    create_time = models.DateTimeField('创建日期', auto_now_add=True, auto_now=False)
    article = models.ForeignKey(Article, verbose_name='文章')
    
    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
    
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
    
    def __unicode__(self):
        return self.title
    
    def save(self):
        image = Image.open(self.image)
        if image.mode not in ('L', 'RGB'):
            image = image.convert('RGB')
        # save the original size
        ori_w, ori_h = image.size
        if ori_w <= 120 and ori_h <= 85:
            self.thumbnail.save(self.image.name + '.png', self.image, save=False)
            super(Photo, self).save(False, False)
            return
        width = 120
        height = (120 * ori_h) / ori_w
        if height > 85:
            height = 85
            width = height * ori_w / ori_h
        image.thumbnail((width, height), Image.ANTIALIAS)
        # save the thumbnail to memory
        temp_handle = StringIO()
        image.save(temp_handle, 'png')
        temp_handle.seek(0)  # rewind the file
        # save to the thumbnail field
        suf = SimpleUploadedFile(os.path.splitext(self.image.name)[0],
                                 temp_handle.read(),
                                 content_type='image/png')
        self.thumbnail.save(suf.name + '.png', suf, save=False)
        super(Photo, self).save(False, False)
