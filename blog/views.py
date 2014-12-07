# !-*-coding=utf8-*-
from django.shortcuts import render_to_response
from blog.models import Article
from blog.models import Comment
from blog.models import Tag
from blog.models import Message
from blog.models import PhotoTag
from blog.models import Photo
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.http import Http404
from django.db import connection
from django.core.paginator import Paginator
from django.conf import settings
import re
from DjangoCaptcha import Captcha
# Create your views here.
def index(request):
    dataMap = __paginator(request, Article.objects.order_by('-create_time').all())
    __cleanContent(dataMap["list"])
    return render_to_response('index.html', __buildResponse(dataMap, request), context_instance=RequestContext(request))

def blog(request, aid):
    try:
        article = Article.objects.get(id=aid)
    except Article.DoesNotExist:
        raise Http404
    result = __paginator(request, article.comment_set.order_by('-create_time').all())
    result['article'] = article
    result['anchor'] = '#comment'
    return render_to_response('blog.html', __buildResponse(result, request), context_instance=RequestContext(request))

def comment(request):
    _code = request.POST['code'] or ''
    if not _code:
        raise Http404
    ca = Captcha(request)
    if ca.check(_code):
        article = Article.objects.get(id=request.POST["articleId"])
        email = request.POST["email"]
        nickname = request.POST["nickname"]
        content = request.POST["content"]
        comment = Comment(email=email, nickname=nickname, content=content, article=article)
        comment.save()
        return HttpResponseRedirect('/blog/' + request.POST["articleId"] + '#comment')
    else:
        raise Http404
    
def about(request):
    result = __paginator(request, Message.objects.order_by('-create_time').all())
    result['anchor'] = '#message'
    return render_to_response('about.html', __buildResponse(result, request), context_instance=RequestContext(request))

def tag(request, tagId):
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
    if (tagId):
        try:
            tag = Tag.objects.get(id=tagId)
        except Tag.DoesNotExist:
            raise Http404
        result = __paginator(request, tag.article_set.order_by('-create_time').all())
        result["tagList"] = tagList
        result["curTag"] = tag
        result['anchor'] = '#tags'
        __cleanContent(result["list"])
        return render_to_response('tag.html', __buildResponse(result, request), context_instance=RequestContext(request))
    return render_to_response('tag.html', __buildResponse({'tagList':tagList}, request), context_instance=RequestContext(request))
    
def message(request):
    _code = request.POST['code'] or ''
    if not _code:
        raise Http404
    ca = Captcha(request)
    if ca.check(_code):
        email = request.POST["email"]
        nickname = request.POST["nickname"]
        content = request.POST["content"]
        message = Message(email=email, nickname=nickname, content=content)
        message.save()
        return HttpResponseRedirect('/about' + '#message')
    else:
        raise Http404

def gallery(request, tagId):
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
    if (tagId):
        tag = None
        result = None
        if tagId == '0':
            tag = PhotoTag()
            tag.id = 0
            tag.name = '全部'
            result = __paginator(request, Photo.objects.order_by('-create_time').all())
        else:
            try:
                tag = PhotoTag.objects.get(id=tagId)
            except PhotoTag.DoesNotExist:
                raise Http404
            result = __paginator(request, tag.photo_set.order_by('-create_time').all())
        result["tagList"] = tagList
        result["curTag"] = tag
        result['anchor'] = '#gallery'
        return render_to_response('gallery.html', __buildResponse(result, request), context_instance=RequestContext(request))
    return render_to_response('gallery.html', __buildResponse({'tagList':tagList}, request), context_instance=RequestContext(request))

def code(request):
    ca = Captcha(request)
    return ca.display()

def __getPopularTags():
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

def __getPopularArticles():
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

def __getLastestComments():
    return Comment.objects.order_by('-create_time')[0:10]

def __getLastestPhoto():
    return Photo.objects.order_by('-create_time')[0:6]
    
def __buildResponse(data=None, request=None):
    if data is None:data = {}
    data['popularTagList'] = __getPopularTags()
    data['popularArticleList'] = __getPopularArticles()
    data['lastestCommentList'] = __getLastestComments()
    # 该功能暂时不启用   
#     data['lastestPhotoList'] = __getLastestPhoto()
    if request:
        if request.path == '/':
            data['requestPath'] = 'blog'
        else:
            data['requestPath'] = request.path.split('/')[1]
    return data

def __paginator(request, dataList):
    paginator = Paginator(dataList, settings.DEFAULT_PAGE_SIZE)
    curPage = request.GET.get("page", None)
    if curPage is None:
        curPage = 1
    else:
        try:
            curPage = max(min(int(curPage), paginator.num_pages), 1)
        except:
            raise Http404
    page = paginator.page(curPage)
    page_range = paginator.page_range
    # 当分页数超过5页，则显示一部分，避免全部显示
    if paginator.num_pages > 5:
        # 开始页索引
        start = (curPage - 2) if (curPage - 2 > 1) else 1
        # 结束页索引
        end = start + 4
        # 如果结束页索引超出了页面总数，重新计算开始页索引
        if end > paginator.num_pages:
            start -= (end - paginator.num_pages)
#         paginator.page_range不允许set，只能自定义一个range了
#         paginator.page_range = range(start, start + 5)
        page_range = range(start, start + 5)
    return {'paginator':paginator, 'page':page, 'page_range':page_range, 'list':page.object_list}

def __cleanContent(articleList):
    for article in articleList:
        codePattern = re.compile('<pre class="(.*?)">.*</pre>', re.M | re.S)
        imgPattern = re.compile('<img.*src="(.*?)".*/>')
        article.content = codePattern.sub('[code]', article.content)
        article.content = imgPattern.sub('[img!' + settings.SERVER_NAME + r'\1]', article.content)
