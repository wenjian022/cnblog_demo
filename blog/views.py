
from django.contrib import auth

from django.http import JsonResponse
from django.shortcuts import render, HttpResponse

from blog.utils import validCode
from blog import MyForms
from blog.models import *
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
        print(request.POST)
        form = MyForms.UserForm(request.POST)
        response = {'user':None,'msg':None}

        if form.is_valid():
            user = form.cleaned_data.get('user')
            pwd = form.cleaned_data.get('pwd')
            email = form.cleaned_data.get('email')
            # 不用手动下载 django会自动下载到指定目录 如果没有指定就下载到项目根目录
            avatar_obj = request.FILES.get('avatar')
            # 生成用户记录 这里avatar存的是文件在项目中的相对路径
            UserInfo.objects.create_user(username=user,password=pwd,email=email,avatar=avatar_obj)
            # 返回给ajax的信息
            response['user'] = form.cleaned_data.get('user')
        else:
            response['msg'] = form.errors
        return JsonResponse(response)

    form = MyForms.UserForm()
    return render(request, 'registered.html', locals())


# 首页
def index(request):
    return render(request, 'index.html')


# 图片验证码
def get_validCorde_img(request):
    '''
        基于PIL模块 生成随机数
    '''
    data = validCode.get_valid_code_img(request)
    return HttpResponse(data)
