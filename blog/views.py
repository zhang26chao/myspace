# !-*-coding=utf8-*-
from django.shortcuts import render_to_response
from blog.models import Article
from blog.models import Comment
from blog.models import Tag
from blog.models import Message
from blog.models import PhotoTag
from blog.models import Photo
from blog.forms import ContactForm
from blog.page import MyPaginator
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.http import Http404
from django.db import connection
from django.conf import settings
import re
from DjangoCaptcha import Captcha
# Create your views here.
def index(request):
    '''首页'''
    dataMap = __paginator(request, Article.objects)
    __clean_content(dataMap["list"])
    return render_to_response('index.html', __build_response(dataMap, request), context_instance=RequestContext(request))

def blog(request, aid):
    '''博客文章详情页'''
    if request.method == 'GET':
        if aid:
            return __to_blog_view(request, __get_article(aid), ContactForm())
        return HttpResponseRedirect('/index')
    else:
        # 保存文章评论
        article = __get_article(request.POST.get("articleId"))
        form = ContactForm(request.POST, request)
        if form.is_valid():
            email = form.cleaned_data["email"]
            nickname = form.cleaned_data["nickname"]
            content = form.cleaned_data["content"]
            comment = Comment(email=email, nickname=nickname, content=content, article=article)
            comment.save()
            return HttpResponseRedirect('/blog/' + request.POST["articleId"] + '#comment')
        else:
            return __to_blog_view(request, article, form)

def __to_blog_view(request, article, form):
    result = __paginator(request, article.comment_set)
    result['article'] = article
    result['anchor'] = '#comment'
    result['form'] = form
    return render_to_response('blog.html', __build_response(result, request), context_instance=RequestContext(request))
    
def about(request):
    '''关于我'''
    if request.method == 'GET':
        result = __paginator(request, Message.objects)
        result['anchor'] = '#message'
        result['form'] = ContactForm()
        return render_to_response('about.html', __build_response(result, request), context_instance=RequestContext(request))
    # 接受留言
    form = ContactForm(request.POST, request)
    if form.is_valid():
        email = form.cleaned_data["email"]
        nickname = form.cleaned_data["nickname"]
        content = form.cleaned_data["content"]
        message = Message(email=email, nickname=nickname, content=content)
        message.save()
        return HttpResponseRedirect('/about#message')
    else:
        result = __paginator(request, Message.objects)
        result['form'] = form
        result['anchor'] = '#message'
        return render_to_response('about.html', __build_response(result, request), context_instance=RequestContext(request))        

def tag(request, tagId):
    if tagId:
        try:
            tag = Tag.objects.get(id=tagId)
        except Tag.DoesNotExist:
            raise Http404
        result = __paginator(request, tag.article_set)
        result["curTag"] = tag
        result['anchor'] = '#tags'
        __clean_content(result["list"])
        return render_to_response('tag.html', __build_response(result, request), context_instance=RequestContext(request))
    else:
        cursor = connection.cursor()
        cursor.execute("""
            select a.id,a.name,ifnull(b.count,0) from blog_tag a left join
            (SELECT 
                tag_id,count(*) count
            FROM 
                blog_article_tags
            group by tag_id) b 
            on a.id = b.tag_id 
            ORDER BY b.count desc,a.id""")
        tagList = cursor.fetchall()
        cursor.close()
        return render_to_response('tag.html', __build_response({'tagList':tagList}, request), context_instance=RequestContext(request))

def gallery(request, tagId):
    if tagId:
        tag = None
        result = None
        if tagId == '0':
            tag = PhotoTag()
            tag.id = 0
            tag.name = '全部'
            result = __paginator(request, Photo.objects)
        else:
            try:
                tag = PhotoTag.objects.get(id=tagId)
            except PhotoTag.DoesNotExist:
                raise Http404
            result = __paginator(request, tag.photo_set)
        result["curTag"] = tag
        result['anchor'] = '#gallery'
        return render_to_response('gallery.html', __build_response(result, request), context_instance=RequestContext(request))
    else:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT 0, '全部', count(*)
              FROM blog_photo
            UNION
            (select a.id,a.name,ifnull(b.count,0) from blog_phototag a left join
            (SELECT 
                phototag_id,count(*) count
            FROM 
                blog_photo_tags
            group by phototag_id) b 
            on a.id = b.phototag_id 
            ORDER BY b.count desc,a.id)""")
        tagList = cursor.fetchall()
        cursor.close()
        # 如果没有照片则不显示'全部'
        if len(tagList) == 1:
            tagList = []
        return render_to_response('gallery.html', __build_response({'tagList':tagList}, request), context_instance=RequestContext(request))

def code(request):
    '''生成验证码'''
    ca = Captcha(request)
    return ca.display()

def __get_article(aid):
    '''根据文章id获取文章'''
    try:
        article = Article.objects.get(id=aid)
    except Article.DoesNotExist:
        raise Http404
    return article

def __get_popular_tags():
    '''获得文章最多的标签'''
    cursor = connection.cursor()
    cursor.execute("""
        select a.id,a.name,b.count from blog_tag a,
            (SELECT 
                tag_id,count(*) count
            FROM 
                blog_article_tags
            group by tag_id) b 
            where a.id = b.tag_id 
            ORDER BY b.count desc,a.id desc limit 10""")
    tagList = cursor.fetchall()
    cursor.close()
    return tagList

def __get_popular_articles():
    '''获取评论最多的文章'''
    cursor = connection.cursor()
    cursor.execute("""
        select a.id,a.title,a.micro,a.create_time from blog_article a,
            (SELECT 
                article_id,count(*) count
            FROM 
                blog_comment
            group by article_id) b 
            where a.id = b.article_id 
            ORDER BY b.count desc,a.id desc limit 5""")
    articleList = cursor.fetchall()
    cursor.close()
    return articleList

def __get_lastest_comments():
    '''获取最近发布的10个评论'''
    return Comment.objects.all()[0:10]

def __get_lastest_photo():
    '''获取最近发表的6张相片'''
    return Photo.objects.all()[0:6]
    
def __build_response(data=None, request=None):
    if data is None:data = {}
    data['popularTagList'] = __get_popular_tags()
    data['popularArticleList'] = __get_popular_articles()
    data['lastestCommentList'] = __get_lastest_comments()
    # 该功能暂时不启用   
#     data['lastestPhotoList'] = __get_lastest_photo()
    if request:
        if request.path == '/':
            data['requestPath'] = 'blog'
        else:
            data['requestPath'] = request.path.split('/')[1]
    return data

def __paginator(request, objects):
    '''分页'''
    curPage = request.GET.get("page")
    paginator = MyPaginator(objects, curPage)
    page = paginator.page()
    page_range = paginator.mini_page_range
    return {'paginator':paginator, 'page':page, 'page_range':page_range, 'list':page.object_list}

def __clean_content(articleList):
    '''将文章中的代码和图片转义'''
    for article in articleList:
        codePattern = re.compile('<pre class="(.*?)">.*</pre>', re.M | re.S)
        imgPattern = re.compile('<img.*src="(.*?)".*/>')
        article.content = codePattern.sub('[code]', article.content)
        article.content = imgPattern.sub('[img!' + settings.SERVER_NAME + r'\1]', article.content)
