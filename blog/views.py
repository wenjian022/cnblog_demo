import json
import os

from bs4 import BeautifulSoup
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect

from blog import MyForms
from blog.models import *
from blog.utils import validCode
from cnblog import settings


# Create your views here.
# 登录
def login(request):
    if request.method == 'POST':
        response = {'user': None, 'mgs': None}
        user = request.POST.get('user')
        pwd = request.POST.get('pwd')
        valid_code = request.POST.get('valid_code')
        # 取出session值 来判断验证码 验证码改成大写
        if valid_code.upper() == request.session.get('valid_code_str').upper():
            user = auth.authenticate(username=user, password=pwd)
            if user:
                auth.login(request, user)  # request.user == 当前登录的对象
                response['user'] = user.username
            else:
                response['msg'] = '用户名或者密码错误'
        else:
            response['msg'] = '验证码错误'
        # from django.http import JsonResponse 可以也json的方式返回
        return JsonResponse(response)
    return render(request, 'login.html')


# 注册
def registered(request):
    if request.is_ajax():
        form = MyForms.UserForm(request.POST)
        response = {'user': None, 'msg': None}
        if form.is_valid():
            user = form.cleaned_data.get('user')
            pwd = form.cleaned_data.get('pwd')
            email = form.cleaned_data.get('email')
            # 不用手动下载 django会自动下载到指定目录 如果没有指定就下载到项目根目录
            avatar_obj = request.FILES.get('avatar')
            # 如果用户传的是一个空值，就不能传avatar值 而是让它走默认值
            extra = {}
            if avatar_obj:
                extra['avatar'] = avatar_obj
            # 生成用户记录 这里avatar存的是文件在项目中的相对路径
            UserInfo.objects.create_user(username=user, password=pwd, email=email, **extra)
            # 生成用户后需要创建对应的blog信息
            Blog.objects.create(title="%s的博客" % (user), site_name=user, theme='index.css')
            # 返回给ajax的信息
            response['user'] = form.cleaned_data.get('user')
        else:
            response['msg'] = form.errors
        return JsonResponse(response)

    form = MyForms.UserForm()
    return render(request, 'registered.html', locals())


# 注销
def logout(request):
    auth.logout(request)
    return redirect('/index/')


# 首页
def index(request):
    article_list = Article.objects.all().order_by('-create_time')
    return render(request, 'index.html', locals())


# 图片验证码
def get_validCorde_img(request):
    '''
        基于PIL模块 生成随机数
    '''
    data = validCode.get_valid_code_img(request)
    return HttpResponse(data)


def get_query_data(username):
    ''' 个人站点数据复用函数 '''
    ''' 已废弃 cate_list，tag_list，date_list 这3个变量 改为了自定义标签'''
    user = UserInfo.objects.filter(username=username).first()
    # 查询当前站点对象
    blog = user.blog
    #  查询每一个分类名称以及对应的文章数
    ret = Category.objects.values('pk').annotate(c=Count('article__title')).values("title", 'c')
    # 查询当前站点的每一个分类名以及对应的文章数
    cate_list = Category.objects.filter(blog=blog).annotate(c=Count('article__title')).values_list("title", 'c')
    # 查询当前站点的每一个标签名称以及对应的文章数
    tag_list = Tag.objects.filter(blog=blog).values('pk').annotate(c=Count('article__title')).values_list('title', 'c')
    # 查询当前站点每一个年月的名称以及对应的文章数
    # 方式1
    # extra函数可以自定义sql extra(select={'参数的名字(自定义)':'sql命令'})
    date_list = Article.objects.filter(user=user).extra(select={'y_m_date': 'date_format(create_time,"%%Y-%%m")'}) \
        .values('y_m_date').annotate(c=Count('nid')).values_list('y_m_date', 'c')
    # 方式2
    '''
    #  使用django的orm方法
        from django.db.models.functions import TruncMonth
        res = Article.objects.filter(user=user).annotate(month=TruncMonth('create_time')).values('month').annotate(c=Count('nid')).values('month','c')
    '''
    # return user, blog, cate_list, tag_list, date_list
    return user, blog


def home_site(request, username, **kwargs):
    ''' 个人站点视图函数 '''
    user, blog = get_query_data(username)
    if not user:
        return render(request, '404.html')

    article_list = Article.objects.filter(user=user)
    # 区分访问的个人站点页面还是跳转下的页面
    if kwargs:
        condition = kwargs.get('condition')
        param = kwargs.get('param')

        if condition == 'category':
            article_list = Article.objects.filter(user=user).filter(category__title=param)

        elif condition == 'tag':
            article_list = Article.objects.filter(user=user).filter(tags__title=param)

        elif condition == 'archive':
            year, month = param.split("-")
            article_list = Article.objects.filter(user=user).filter(create_time__year=year, create_time__month=month)

        else:
            return render(request, '404.html')

    return render(request, 'home_site.html', locals())


def article_detail(request, username, articles_id):
    ''' 文章渲染函数 '''
    user, blog = get_query_data(username)
    article_obj = Article.objects.filter(user__username=user, nid=articles_id).first()
    if article_obj:
        comment_list = Comment.objects.filter(article_id=articles_id)
    else:
        return render(request, '404.html')
    return render(request, 'article_detail.html', locals())


def digg(request):
    ''' 点赞视图函数'''
    response = {'state': True}
    if request.is_ajax():
        article_id = request.POST.get('article_id')
        is_up = json.loads(request.POST.get('is_up'))  # 转换数据类型 ajax默认发送过来的数据都是字符串类型
        user_id = request.user.pk
        obj = ArticleUpDown.objects.filter(user_id=user_id, article_id=article_id).first()  # 先查询用户是否点赞或者反对过

        if not obj:
            ArticleUpDown.objects.create(user_id=user_id, article_id=article_id, is_up=is_up)  # 生成记录
            if is_up:
                Article.objects.filter(pk=article_id).update(up_count=F("up_count") + 1)
            else:
                Article.objects.filter(pk=article_id).update(down_count=F("down_count") + 1)
        else:
            response['state'] = False
            response['handled'] = obj.is_up

    print(response)

    return JsonResponse(response)


def comment(request):
    ''' 评论列表 '''

    article_id = request.POST.get('article_id')
    content = request.POST.get('content')
    pid = request.POST.get('pid')
    user_id = request.user.pk

    article_name = Article.objects.filter(pk=article_id).first()

    # 模块 from django.db import transaction 功能和mysql的事务一样的功能 同进同退
    with transaction.atomic():
        comment_obj = Comment.objects.create(user_id=user_id, article_id=article_id, content=content,
                                             parent_comment_id=pid)
        # 评论数同步
        Article.objects.filter(pk=article_id).update(comment_count=F('comment_count') + 1)

    response = {}
    response['create_time'] = comment_obj.create_time.strftime("%Y-%m-%d %H:%M")
    response['username'] = request.user.username
    response['content'] = content
    if pid:
        father_obj = Comment.objects.filter(nid=pid).first()
        response['father_content'] = father_obj.content
        response['father_user'] = father_obj.user.username

    # 当评论成功时发送邮件

    # from django.core.mail import send_mail 功能发送邮件
    '''
        格式:
            注意:需要在settings.py配置邮件信息:
                EMAIL_USE_SSL = True
                EMAIL_HOST = 'smtp.qq.com'  # 如果是 163 改成 smtp.163.com
                EMAIL_PORT = 465    # 邮件服务器端口
                EMAIL_HOST_USER = 'xxx@qq.com' # 帐号
                EMAIL_HOST_PASSWORD = 'p@ssw0rd'  # 密码
                DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
            form cnblog import settings
            send_mail(
                "主题",
                "内容",
                settings.EMAIL_HOST_USER,
                ["收件人1","收件人2",....]
            )
    '''

    return JsonResponse(response)


def get_comment_tree(request):
    ''' 评论树的get请求 '''
    article_id = request.GET.get('article_id')
    ret = list(
        Comment.objects.filter(article_id=article_id).order_by('pk').values('pk', 'content', 'parent_comment_id'))

    # safe=False 设置非字典类型的数据发送
    return JsonResponse(ret, safe=False)


@login_required
def cn_backend(request):
    ''' 文章管理后台 '''
    user = UserInfo.objects.filter(username=request.user).first()
    blog = user.blog
    article_list = Article.objects.filter(user__username=request.user)
    tag_list = Tag.objects.filter(blog__nid=blog.nid)
    category_list = Category.objects.filter(blog__nid=blog.nid)

    return render(request, "backend/backstage_admin.html", locals())


@login_required
def add_article(request):
    ''' 添加文章 '''
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        soup = BeautifulSoup(content, "html.parser")

        # 模块防御xss攻击 xss攻击是(通常指的是通过利用网页开发时留下的漏洞，通过巧妙的方法注入恶意指令代码到网页，使用户加载并执行攻击者恶意制造的网页程序)
        # 防止用户提交 js代码
        for tag in soup.find_all():
            if tag.name == "script":
                # 直接删除掉script 标签
                tag.decompose()

        # 使用bs4库来做html标签筛选 BeautifulSoup('HTML标签',‘html解析器’("html.parser"是python只带的解析器))
        # 字符串截取0到150个
        desc = soup.text[0:150] + " ..."
        Article.objects.create(title=title, desc=desc, content=str(content), user=request.user.pk)

    return render(request, 'backend/add_article.html', locals())


@login_required
def upload(request):
    ''' 编辑器文件上传位置 '''
    img = request.FILES.get('upload_img')

    path = os.path.join(settings.MEDIA_ROOT, 'add_artcle_img', img.name)
    with open(path, 'wb') as f:
        for line in img:
            f.write(line)

    response = {
        "error": 0,
        # 返回给文本编辑器一个图片访问路径：注意不是文件路径，而是网站url路径
        "url": "/media/add_artcle_img/%s" % (img.name),
    }
    return JsonResponse(response)


@login_required
def edit(request, condition, id):
    ''' 后台编辑功能 '''
    obj_id = id
    if condition == 'tag':
        # 标签
        pass
    elif condition == 'category':
        # 随笔
        pass
    elif condition == 'archive':
        # 文章
        pass

    return HttpResponse('OK!')