from django.urls import path
from django.contrib.auth import views as auth_views
from cms import views

app_name = 'cms'

urlpatterns = [
    # ホーム
    path('', views.index, name='index'),
    # ユーザー
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name="cms/pages/login.html"), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page="cms:index"), name='logout'),
    path('user/<int:user_id>', views.user_page, name='user_page'),
    # 記事
    path('article/<int:article_id>', views.article_view, name='article_view'),
    path('article/add/', views.article_edit, name='article_add'),
    path('article/edit/<int:article_id>/', views.article_edit, name='article_edit'),
    path('article/del/<int:article_id>/', views.article_del, name='article_del'),
    # カテゴリ
    path('category/create', views.category_create, name='category_create'),
    # タグ
    path('tag/create', views.tag_create, name='tag_create'),
    # Ajax
    path('ajax/tag/add/<str:additional_tag>', views.tag_add_ajax, name='tag_add_ajax'),
    path('ajax/search/<int:page>', views.search_ajax, name='search_ajax'),
    path('ajax/fav/<int:article_id>/', views.fav_ajax, name='fav_ajax'),
    path('ajax/user_page/<int:user_id>/<int:page>', views.user_page_ajax, name='user_page_ajax'),
]
