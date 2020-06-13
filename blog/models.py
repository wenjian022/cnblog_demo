from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


# 继承了auth_user 表 使用的接口变成了 UserInfo django在数据库迁移时不会创建auth_user了，并且把UserInfo表中多余的字段加到到原auth_user中，形成UserInfo表
# 必须继承AbstractUser类 注意:AbstractUser类 就是auth_user表
# 需要在全局变量中添加 AUTH_USER_MODEL = 'blog.UserInfo' 这个地址是项目中的类
class UserInfo(AbstractUser):
    """
    用户信息
    """
    nid = models.AutoField(primary_key=True)
    telephone = models.CharField(max_length=11, null=True, unique=True)
    # 存储头像文件 upload_to=文件存储的路径(如果没有这个文件夹会自动创建) 如果不写会存放到django项目的根目录
    # default=默认的文件路径
    # FileField 可以存储任何文件包括(图片。视频，音频)
    avatar = models.FileField(upload_to='avatars/', default="/avatars/default.png")
    # 创建时间 verbose_name 注释 auto_now_add=True 在创建时自动添加当前时间
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    # 一对一 个人站点表
    blog = models.OneToOneField(to='Blog', to_field='nid', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.username


class Blog(models.Model):
    """
    博客信息 (个人站点表)
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='个人博客标题', max_length=64)
    site_name = models.CharField(verbose_name='站点名称', max_length=64)
    theme = models.CharField(verbose_name='博客主题', max_length=32)

    def __str__(self):
        return self.title


class Category(models.Model):
    """
    博主个人文章分类表
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='分类标题', max_length=32)
    # 一对多 博客信息
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Tag(models.Model):
    '''
    标签表
    '''
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='标签名称', max_length=32)
    # 一对多 博客信息
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Article(models.Model):
    '''
    文章
    '''
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50, verbose_name='文章标题')
    desc = models.CharField(max_length=255, verbose_name='文章描述')
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    # 文章内容 TextField()
    content = models.TextField()

    # 文章评论数 自增
    comment_count = models.IntegerField(default=0)
    # 文章点赞数 自增
    up_count = models.IntegerField(default=0)
    # 文章反对数 自增
    down_count = models.IntegerField(default=0)

    # 一对多 用户表
    user = models.ForeignKey(verbose_name='作者', to='UserInfo',
                             to_field='nid', on_delete=models.CASCADE)
    # 一对多 分类表
    category = models.ForeignKey(to='Category', to_field='nid', null=True, on_delete=models.CASCADE)

    # 多对多关系 through='Article2Tag' 手动生成
    tags = models.ManyToManyField(
        to="Tag",
        through='Article2Tag',
        through_fields=('article', 'tag'),
    )

    def __str__(self):
        return self.title


class Article2Tag(models.Model):
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(verbose_name='文章', to="Article", to_field='nid', on_delete=models.CASCADE)
    tag = models.ForeignKey(verbose_name='标签', to="Tag", to_field='nid', on_delete=models.CASCADE)

    class Meta:
        unique_together = [
            ('article', 'tag'),
        ]

    def __str__(self):
        v = self.article.title + "---" + self.tag.title
        return v


class ArticleUpDown(models.Model):
    """
    点赞表
    """

    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey('UserInfo', null=True, on_delete=models.CASCADE)
    article = models.ForeignKey("Article", null=True, on_delete=models.CASCADE)
    is_up = models.BooleanField(default=True)

    class Meta:
        unique_together = [
            ('article', 'user'),
        ]


class Comment(models.Model):
    """

    评论表

    """
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(verbose_name='评论文章', to='Article', to_field='nid', on_delete=models.CASCADE)
    user = models.ForeignKey(verbose_name='评论者', to='UserInfo', to_field='nid', on_delete=models.CASCADE)
    content = models.CharField(verbose_name='评论内容', max_length=255)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    # 子评论 null=True 可以为空  self 自己关联自己
    parent_comment = models.ForeignKey('self', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.content