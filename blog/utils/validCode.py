import random
import string
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont


def get_valid_code_img(request):
    # 方式一
    '''
    # 图像处理模块: pip install pillow
    # 导入 from PIL import Image
    # Image.new('颜色的模式',(图片的长,图片的高),color='颜色的单词也可以是一个元组(255,255,255)')
    img_obj = Image.new('RGB', (270, 45), color='red')
    # 注意这里只是生成了一个图片里面还没有验证码
    with open('/validCode.png', 'wb') as f:
        # img_obj.save(f, 后缀名)
        img_obj.save(f, 'png')

    with open('/validCode.png', 'rb') as f:
        data = f.read()
    '''
    '''
    # 方式二:
    \'''
    from io import BytesIO 内存模块
        通过内存的方式生成
    \'''
    img_obj = Image.new('RGB', (200, 45), (255, 255, 255))
    f = BytesIO()
    img_obj.save(f, 'png')
    # 通过f.getvalue() 取出数据
    data = f.getvalue()
    '''

    # 方式三:
    '''
        通过
        from PIL import ImageDraw 模块 生成验证码
    '''
    # 生成背景图片
    img_obj = Image.new('RGB', (200, 45), (171, 178, 185))
    draw = ImageDraw.Draw(img_obj)

    # 生成随机的验证码
    char_str = string.digits + string.ascii_letters  # 拼接所有的数字和字母大小写
    char = ''.join(random.sample(char_str, 5))  # random 获取的是一个列表需要转成字符串

    # 将字符串写到图片中
    # ImageFont.truetype(字体样式的路径,size=字体大小)
    kumo_font = ImageFont.truetype('static/blog/font/BRADHITC.TTF', size=30)

    # 写入文本内容
    # draw.text((坐标),'内容','字体颜色',font=字体样式)
    draw.text((50, 0), char, 'red', font=kumo_font)

    # 添加噪点噪线 直接套用就可以了
    '''
        # 宽
        width=270
        # 高
        height=40
        # 噪线 range(10) 多少个
        for i in range(10):
            x1=random.randint(0,width)
            x2=random.randint(0,width)
            y1=random.randint(0,height)
            y2=random.randint(0,height)
            draw.line((x1,y1,x2,y2),fill=get_random_color())
        # 噪点  range(10) 多少个
        for i in range(100):
            draw.point([random.randint(0, width), random.randint(0, height)], fill=get_random_color())
            x = random.randint(0, width)
            y = random.randint(0, height)
            draw.arc((x, y, x + 4, y + 4), 0, 90, fill=get_random_color())
    '''
    # 将图片生成到内存中
    f = BytesIO()
    img_obj.save(f, 'png')
    # 取出内存中的图片，一旦图片取出 系统会自动清理掉
    data = f.getvalue()

    # 通过session保存这次的验证码的值
    request.session['valid_code_str'] = char

    return data
