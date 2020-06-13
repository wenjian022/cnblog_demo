from django.contrib import auth
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse,redirect

from blog import MyForms
from blog.models import *
from blog.utils import validCode


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
    article_list = Article.objects.all()
    return render(request, 'index.html',locals())


# 图片验证码
def get_validCorde_img(request):
    '''
        基于PIL模块 生成随机数
    '''
    data = validCode.get_valid_code_img(request)
    return HttpResponse(data)

# 个人站点视图函数
def home_site(request,username):

    user = UserInfo.objects.filter(username=username).first()

    if not user:
        return render(request, '404.html')
    # 查询当前站点对象
    blog = user.blog
    # 取出当前用户或者当前站点对应的所有文件
    article_List = Article.objects.filter(user=user)
    return render(request,'home_site.html',locals())

