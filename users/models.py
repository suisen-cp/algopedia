from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.models import Sum, Count, F
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import models


# Create your models here.
from cms.models import Article


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')

        username = self.model.normalize_username(username)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELD = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    # お気に入りに登録した記事
    def favorite_articles(self):
        return Article.objects.filter(favorite__user=self)

    # 自ら執筆した記事
    def author_articles(self):
        return Article.objects.filter(author__user=self)

    # 閲覧したことのある記事
    def readinghistory_articles(self):
        return Article.objects.filter(readinghistory__user=self)

    # 記事についたお気に入りの合計 (SUM)
    def liked_num(self):
        return self.author_articles().aggregate(Sum('fav_num'))['fav_num__sum'] or 0

    # カテゴリ別の記事数 (GROUP BY)
    def category_counts(self):
        return self.author_articles()\
            .annotate(category=F('articlecategory__category'))\
            .values('category')\
            .order_by('category')\
            .annotate(count=Count('category'))

    # タグ別の記事数 (GROUP BY)
    def tag_counts(self):
        return self.author_articles()\
            .annotate(tag=F('articletags__tag'))\
            .values('tag')\
            .order_by('tag')\
            .annotate(count=Count('tag'))

    @staticmethod
    def get_or_none(user_id):
        return User.objects.filter(pk=user_id).first()

    @staticmethod
    def exists(user_id):
        return User.get_or_none(user_id) is not None
