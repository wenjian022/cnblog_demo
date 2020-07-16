from django import template
from django.db.models import Count

from blog.models import *

register = template.Library()

# register.inclusion_tag(‘html文件’) 渲染html文件
@register.inclusion_tag('classification.html')
def get_classification_style(username):
    user = UserInfo.objects.filter(username=username).first()
    blog = user.blog
    cate_list = Category.objects.filter(blog=blog).annotate(c=Count('article__title')).values_list("title", 'c')
    tag_list = Tag.objects.filter(blog=blog).values('pk').annotate(c=Count('article__title')).values_list('title', 'c')
    date_list = Article.objects.filter(user=user).extra(select={'y_m_date': 'date_format(create_time,"%%Y-%%m")'}) \
        .values('y_m_date').annotate(c=Count('nid')).values_list('y_m_date', 'c')

    return {'blog': blog, 'cate_list': cate_list, 'tag_list': tag_list, 'date_list': date_list,'username':username}
