import json
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader

# Create your views here.
from cms.forms import SignUpForm, TagForm, CategoryForm, ArticleForm
from cms.models import Article, Category, Tag, ArticleCategory, ArticleTags, Author, Favorite, ReadingHistory
from users.models import User


# ユーザー登録
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cms:index')
    else:
        form = SignUpForm()
    return render(request, 'cms/pages/signup.html', dict(form=form))


# 記事のページ
def article_view(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    user: User = request.user
    # ログイン中かどうか
    if user.is_authenticated:
        # 閲覧履歴の更新 (なければ挿入)
        ReadingHistory.objects.update_or_create(article=article, user=user)
        # 既にお気に入りに設定しているか
        fav = Favorite.exists(article=article, user=user)
    else:
        fav = False
    context = {
        'article': article,
        'fav': fav,
    }
    return render(request, 'cms/pages/article.html', context)


# お気に入り登録 / 解除のトグルスイッチ
@login_required
def fav_ajax(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    has_created = Favorite.create_or_delete(article=article, user=request.user)
    article = get_object_or_404(Article, pk=article_id)
    return render(request, "cms/components/fav.html", dict(fav=has_created, article=article))


# 記事の新規作成 or 編集. article_id が None なら新規作成
@login_required
def article_edit(request, article_id=None):
    if article_id:
        article = get_object_or_404(Article, pk=article_id)
        # 記事の執筆者とログイン中のユーザーが異なる場合はログインページに飛ぶ
        if request.user != article.author.user:
            errors = ["編集権限がありません．記事作成者のアカウントにログインして下さい"]
            return render(request, "cms/pages/login.html", dict(errors=errors))
    if request.method == 'POST':
        # エラーメッセージ
        err = dict(title="", content="", category="", tag={})
        err_tpl = "cms/components/field_errors.html"
        forms = []

        # 入力内容
        title = request.POST.get("title")
        content = request.POST.get("content")
        category_name = request.POST.get('category')
        tag_names = request.POST.getlist('selected_tags')

        article_form = ArticleForm(data=dict(title=title, content=content))
        if article_form.is_valid():
            title = article_form.cleaned_data.get('title')
            content = article_form.cleaned_data.get('content')
        else:
            # エラーメッセージ
            err_title = "title" in article_form.errors and article_form.errors["title"]
            err_content = "content" in article_form.errors and article_form.errors["content"]
            err["title"] = loader.render_to_string(err_tpl, dict(errors=err_title))
            err["content"] = loader.render_to_string(err_tpl, dict(errors=err_content))

        category = Category.get_or_none(category=category_name)
        # カテゴリが存在しない場合は新規作成する
        if category is None:
            category_form = CategoryForm(data=dict(category=category_name))
            if category_form.is_valid():
                category_name = category_form.cleaned_data.get('category')
                category = Category(category=category_name)
            else:
                # エラーメッセージ
                err_category = "category" in category_form.errors and category_form.errors["category"]
                err["category"] = loader.render_to_string(err_tpl, dict(errors=err_category))
            forms.append(category_form)

        tags = []
        for tag_name in tag_names:
            tag = Tag.get_or_none(tag=tag_name)
            # タグが存在しない場合は新規作成する
            if tag is None:
                tag_form = TagForm(data=dict(tag=tag_name))
                if tag_form.is_valid():
                    tag_name = tag_form.cleaned_data.get('tag')
                    tag = Tag(tag=tag_name)
                else:
                    # エラーメッセージ
                    err_tag = "tag" in tag_form.errors and tag_form.errors['tag']
                    err["tag"][tag_name] = loader.render_to_string(err_tpl, dict(errors=err_tag))
                forms.append(tag_form)
            tags.append(tag)

        # 入力に何らかの不備があった場合 (status=1)
        if err["title"] or err["content"] or err["category"] or err["tag"]:
            err["tag"] = loader.render_to_string("cms/components/tag_errors.html", dict(errors=err["tag"]))
            return HttpResponse(
                json.dumps(dict(status=1, err=err)),
                content_type="text/javascript")

        for form in forms:
            form.save()

        # add
        if article_id is None:
            article = Article(title=title, content=content)
            article.save()
            ArticleCategory(article=article, category=category).save()
            for tag in tags:
                tag.save()
                ArticleTags(article=article, tag=tag).save()
            Author(article=article, user=request.user).save()
        # edit
        else:
            article = Article.objects.get(pk=article_id)
            article_category = article.articlecategory
            old_category = article_category.category
            new_category = Category.objects.get(category=category_name)

            # カテゴリが変更された場合はつじつま合わせをする必要がある
            if old_category != new_category:
                old_category.article_num -= 1
                old_category.save()
                article_category.category = new_category
                article_category.save()

            # タグ付けの更新
            for old_tag in ArticleTags.objects.filter(article=article).exclude(tag__in=tags):
                old_tag.delete()

            # 新しいタグ付け
            for new_tag in tags:
                if not ArticleTags.exists(article, new_tag):
                    ArticleTags(article=article, tag=new_tag).save()

            # 記事の情報を更新
            article.title = title
            article.content = content
            article.updated_at = datetime.now()
            article.save()

        # 入力が valid だったので status=0
        return HttpResponse(
            json.dumps(dict(status=0)),
            content_type="text/javascript")
    return init_article_form(request, article_id=article_id)


# 記事 form の初期化
def init_article_form(request, article_id=None):
    context = {
        "categories": Category.objects.all(),
        "tags": Tag.objects.all(),
    }
    if article_id is not None:
        context["article"] = get_object_or_404(Article, pk=article_id)
    return render(request, 'cms/pages/article_edit.html', context)


@login_required
def article_del(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    # 記事作成者でなければログイン画面へと遷移する
    if request.user != article.author.user:
        errors = ["削除権限がありません．記事作成者のアカウントにログインして下さい"]
        return render(request, "cms/pages/login.html", dict(errors=errors))
    article.delete()
    return redirect('cms:user_page', user_id=request.user.id)


def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            category = request.POST["category"]
            return render(request, 'cms/pages/create_category.html', dict(form=form, new_category=category))
    else:
        form = CategoryForm()
    return render(request, 'cms/pages/create_category.html', dict(form=form))


def tag_create(request):
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            tag = request.POST["tag"]
            return render(request, 'cms/pages/create_tag.html', dict(form=form, new_tag=tag))
    else:
        form = TagForm()
    return render(request, 'cms/pages/create_tag.html', dict(form=form))


# ページング
def paginate_queryset(queryset, count, page=1):
    paginator = Paginator(queryset, count)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj


# トップ画面
def index(request):
    # デフォルトでは新着順に記事を表示
    post_list = Article.objects.all().order_by('-updated_at')
    page_obj = paginate_queryset(post_list, 10)
    context = {
        'post_list': page_obj.object_list,
        'page_obj': page_obj,
        'categories': Category.objects.all(),
        'tags': Tag.objects.all(),
    }
    return render(request, 'cms/pages/index.html', context)


# Ajax でタグを追加する (db への insert とは別)
def tag_add_ajax(request, additional_tag):
    return render(request, "cms/components/tag.html", dict(tag=additional_tag))


# Ajax で記事検索 or 並べ替えクエリを処理する
def search_ajax(request, page):
    # 検索結果を格納する QuerySet
    post_list = Article.objects.all()

    # 検索パラメータ取得
    username = request.GET.get("username")
    title = request.GET.get("title")
    category = request.GET.get("category")

    # 選択されたタグのリスト
    selected_tags = request.GET.getlist("selected_tags")

    # チェックボックスの入力 (リスト)
    checks = request.GET.getlist('check')

    # 検索 or 並び替え
    search_or_order = request.GET.get("search_or_order")

    if username:
        # 指定したユーザーが執筆した記事
        post_list = post_list.filter(author__user__username=username)

    if title:
        # 指定した文字列を連続部分文字列として含むタイトルを持つ記事 (LIKE)
        post_list = post_list.filter(title__icontains=title)

    if category:
        # 指定したカテゴリを持つ記事
        post_list = post_list.filter(articlecategory__category=category)

    if selected_tags:
        # 指定したいずれかのタグを持つ記事
        post_list = post_list.filter(articletags__tag__in=selected_tags)

    for check_val in checks:
        # ログイン中のユーザー
        user: User = request.user

        if not user:
            break

        if check_val == 'author':
            # 書いた記事
            post_list = post_list.filter(author__user=user)

        if check_val == 'fav':
            # お気に入りした記事
            post_list = post_list.filter(favorite__user=user)

        if check_val == 'read':
            # 閲覧した記事
            post_list = post_list.filter(readinghistory__user=user)

    # 検索結果の並び替え
    if search_or_order != "search":
        # 例えば, "fav_num" ならお気に入り数の昇順, "-fav_num" なら降順
        post_list = post_list.order_by(search_or_order)
    else:
        # デフォルトではお気に入り数の降順
        post_list = post_list.order_by('-fav_num')

    # 検索結果を distinct にする
    post_list = post_list.distinct()

    # ページング
    page_obj = paginate_queryset(queryset=post_list, count=10, page=page)

    context = {
        'post_list': page_obj.object_list,
        'page_obj': page_obj,
        'search_or_order': search_or_order,
    }
    return render(request, 'cms/components/article_list.html', context)


# ユーザーページ
def user_page(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    # ページ主の書いた記事だけを取得
    post_list = user.author_articles()
    # ページング
    page_obj = paginate_queryset(post_list, count=10)
    context = {
        'skip_author': True,
        'has_authority': user == request.user,
        'user': user,
        'post_list': page_obj.object_list,
        'page_obj': page_obj,
    }
    return render(request, 'cms/pages/user_page.html', context)


# ユーザーページでの記事の並び替え/ページング処理
def user_page_ajax(request, user_id, page):
    user = get_object_or_404(User, pk=user_id)
    # ページ主の書いた記事だけを取得
    post_list = user.author_articles()
    # 並び替え
    search_or_order = request.GET.get("search_or_order") or "search"
    if search_or_order != "search":
        post_list = post_list.order_by(search_or_order)
    page_obj = paginate_queryset(post_list, count=10, page=page)
    context = {
        'skip_author': True,
        'has_authority': user == request.user,
        'post_list': page_obj.object_list,
        'page_obj': page_obj,
        'search_or_order': search_or_order,
    }
    return render(request, 'cms/components/article_list.html', context)
