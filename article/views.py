from django.shortcuts import render,redirect
from .forms import ArticlePostForm
from .models import AtrticlePost
from .models import ArticleColumn
from django.http import HttpResponse
import markdown
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
# Create your views here.


def article_list(request):
    search = request.GET.get('search')
    order = request.GET.get('order')

    if search:
        if order == 'total_views':
            article_list = AtrticlePost.objects.filter(
                Q(title__icontains=search) |
                Q(body__icontains=search)
            ).order_by('-total_views')
        else:
            article_list = AtrticlePost.objects.filter(
                Q(title__icontains=search) |
                Q(body__icontains=search)
            )
    else:
        search = ''
        if order == 'total_views':
            article_list = AtrticlePost.objects.all().order_by('-total_views')
        else:
            article_list = AtrticlePost.objects.all()

    paginator = Paginator(article_list, 5)
    page = request.GET.get('page')
    articles = paginator.get_page(page)

    context = {'articles': articles, 'order': order, 'search':search}
    return render(request, 'article/list.html', context)

def article_detail(request, id):
    article = AtrticlePost.objects.get(id=id)

    article.total_views += 1
    article.save(update_fields=['total_views'])

    article.body = markdown.markdown(article.body, extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
        ])
    context = {'article': article}
    # print(article)
    return render(request, 'article/detail.html', context)

@login_required(login_url='/userprofile/login/')
def article_create(request):
    if request.method == "POST":
        article_post_form = ArticlePostForm(data=request.POST)

        if article_post_form.is_valid():
            new_article = article_post_form.save(commit=False)
            new_article.author = User.objects.get(id=request.user.id)

            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            new_article.save()
            return redirect("article:article_list")
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    else:
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        context = {'article_post_form': article_post_form, 'columns': columns}
        return render(request, 'article/create.html',context)

@login_required(login_url='/userprofile/login/')
def article_delete(request, id):
    article = AtrticlePost.objects.get(id=id)
    # 过滤非作者用户
    if request.user != article.author:
        return HttpResponse("抱歉，你无权删除这篇文章。")
    article.delete()
    return redirect("article:article_list")


@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    article = AtrticlePost.objects.get(id=id)

    # 过滤非作者的用户
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")

    if request.method == "POST":
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            article.title = request.POST['title']
            article.body = request.POST['body']
            if request.POST['column'] != 'none':
                article.column = ArticleColumn.objects.get(id=request.POST['column'])
            else:
                article.column = None
            article.save()
            return redirect('article:article_detail', id=id)
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    else:
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        context = {'article': article,
                   'article_post_form': article_post_form,
                   'columns': columns,
                   }
        return render(request, 'article/update.html', context)
