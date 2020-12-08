from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.


class Article(models.Model):
    # 記事 ID
    article_id = models.AutoField(primary_key=True)
    # 記事タイトル
    title = models.CharField(max_length=50)
    # 記事の内容
    content = models.TextField()
    # お気に入り数
    fav_num = models.PositiveIntegerField(default=0)
    # 作成日時
    created_at = models.DateTimeField(auto_now_add=True)
    # 更新日時
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "記事"

    def __str__(self):
        return f"{self.article_id} {self.title}"

    def delete(self, **kwargs):
        for article_tag in self.articletags_set.all():
            article_tag.delete()
        self.articlecategory.delete()
        super(Article, self).delete(**kwargs)

    def get_tags(self):
        return Tag.objects.filter(articletags__article=self).distinct()

    def get_tag_names(self):
        return self.get_tags().values_list('tag', flat=True)

    @staticmethod
    def get_or_none(article_id):
        return Article.objects.filter(article_id=article_id).first()

    @staticmethod
    def exists(article_id):
        return Article.get_or_none(article_id) is not None


class Favorite(models.Model):
    # 記事 ID (外部キー)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, db_index=False)
    # ユーザー ID (外部キー)
    user = models.ForeignKey(to='users.User', on_delete=models.CASCADE, db_index=True)

    # お気に入りは重複しない
    class Meta:
        verbose_name_plural = "お気に入り"
        constraints = [
            models.UniqueConstraint(fields=['article', 'user'], name='unique_fav')
        ]

    def __str__(self):
        return f"{self.article} {self.user}"

    def save(self, **kwargs):
        article = Article.objects.get(article_id=self.article.article_id)
        article.fav_num += 1
        article.save()
        super(Favorite, self).save(**kwargs)

    def delete(self, **kwargs):
        article = Article.objects.get(article_id=self.article.article_id)
        article.fav_num -= 1
        article.save()
        super(Favorite, self).delete(**kwargs)

    @staticmethod
    def get_or_none(article, user):
        return Favorite.objects.filter(article=article, user=user).first()

    @staticmethod
    def exists(article, user):
        return Favorite.get_or_none(article=article, user=user) is not None

    @staticmethod
    def create_or_delete(article, user):
        fav = Favorite.get_or_none(article=article, user=user)
        if fav is None:
            Favorite(article=article, user=user).save()
            return True
        else:
            fav.delete()
            return False


class Author(models.Model):
    # 記事 ID (外部キー)
    article = models.OneToOneField(Article, on_delete=models.CASCADE, primary_key=True, db_index=True)
    # ユーザー ID (外部キー)
    user = models.ForeignKey(to='users.User', on_delete=models.DO_NOTHING, db_index=True)

    class Meta:
        verbose_name_plural = "執筆者"

    def __str__(self):
        return f"{self.article} {self.user}"


class ReadingHistory(models.Model):
    # 記事 ID (外部キー)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, db_index=False)
    # ユーザー ID (外部キー)
    user = models.ForeignKey(to='users.User', on_delete=models.DO_NOTHING, db_index=True)
    # 更新日時
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "閲覧履歴"
        constraints = [
            models.UniqueConstraint(fields=['article', 'user'], name='unique_readinghistory')
        ]

    def __str__(self):
        return f"{self.article} {self.user} {self.updated_at}"


class Category(models.Model):
    # 大分類
    category = models.CharField(max_length=15, primary_key=True)
    # 記事数
    article_num = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "カテゴリ"

    def __str__(self):
        return f"{self.category}"

    @staticmethod
    def get_or_none(category):
        return Category.objects.filter(category=category).first()

    @staticmethod
    def exists(category):
        return Category.get_or_none(category=category) is not None


class Tag(models.Model):
    # タグ
    tag = models.CharField(max_length=15, primary_key=True)
    # 記事数
    article_num = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "タグ"

    def __str__(self):
        return f"{self.tag}"

    @staticmethod
    def get_or_none(tag):
        return Tag.objects.filter(tag=tag).first()

    @staticmethod
    def exists(tag):
        return Tag.get_or_none(tag=tag) is not None


class ArticleCategory(models.Model):
    # 記事 ID (外部キー)
    article = models.OneToOneField(Article, on_delete=models.CASCADE, primary_key=True, db_index=True)
    # 大分類 (外部キー)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, db_index=False)

    class Meta:
        verbose_name_plural = "記事分類"

    def __str__(self):
        return f"{self.article} {self.category}"

    def save(self, **kwargs):
        category = self.category
        category.article_num += 1
        category.save()
        super(ArticleCategory, self).save(**kwargs)

    def delete(self, **kwargs):
        category = self.category
        category.article_num -= 1
        category.save()
        super(ArticleCategory, self).delete(**kwargs)


class ArticleTags(models.Model):
    # 記事 ID (外部キー)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, db_index=True)
    # 外部キー (タグ)
    tag = models.ForeignKey(Tag, on_delete=models.DO_NOTHING, db_index=False)

    # タグは重複しない
    class Meta:
        verbose_name_plural = "記事タグ"
        constraints = [
            models.UniqueConstraint(fields=['article', 'tag'], name='unique_tag')
        ]

    def __str__(self):
        return f"{self.article} {self.tag}"

    def save(self, **kwargs):
        tag = self.tag
        tag.article_num += 1
        tag.save()
        super(ArticleTags, self).save(**kwargs)

    def delete(self, **kwargs):
        tag = self.tag
        tag.article_num -= 1
        tag.save()
        super(ArticleTags, self).delete(**kwargs)

    @staticmethod
    def get_or_none(article, tag):
        return article.articletags_set.filter(tag=tag).first()

    @staticmethod
    def exists(article, tag):
        return ArticleTags.get_or_none(article, tag) is not None
