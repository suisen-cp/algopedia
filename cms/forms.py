from django import forms

from cms.models import Tag, Category, Article
from users.models import User


class SignUpForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    model = User

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('このユーザー名は既に使用されています')
        return username

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password is None or \
                len(password) < 10 or \
                password.isupper() or \
                password.islower() or \
                password.isdecimal() or \
                password.isalpha():
            raise forms.ValidationError('パスワードは大文字・小文字・数字を含んだ 10 文字以上の英数字にしてください')
        if not password.isalnum():
            raise forms.ValidationError('英数字以外の文字は使用できません')
        return password

    def clean(self):
        super(SignUpForm, self).clean()
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and (password1 != password2):
            self.add_error('password2', '入力された 2 つのパスワードが一致していません')

    def save(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password1')
        new_user = User.objects.create_user(username=username)
        new_user.set_password(password)
        new_user.save()


class ArticleForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput)
    content = forms.CharField(widget=forms.Textarea)
    model = Article

    def clean_title(self):
        title = self.cleaned_data.get('title').strip()
        if len(title) == 0:
            raise forms.ValidationError('タイトルは必須です')
        if len(title) > 50:
            raise forms.ValidationError('タイトルは 50 文字以下にしてください')
        return title

    def clean_content(self):
        content = self.cleaned_data.get('content').strip()
        if len(content) == 0:
            raise forms.ValidationError('内容は必須です')
        return content

    def save(self):
        title = self.cleaned_data.get('title')
        content = self.cleaned_data.get('content')
        Article(title=title, content=content).save()


class TagForm(forms.Form):
    tag = forms.CharField(widget=forms.TextInput)
    model = Tag

    def clean_tag(self):
        tag = self.cleaned_data.get('tag').strip()
        if len(tag) > 15:
            raise forms.ValidationError('タグ名は 15 文字以下にして下さい')
        if Tag.exists(tag=tag):
            raise forms.ValidationError('このタグは既に存在します．')
        return tag

    def save(self):
        Tag(tag=self.cleaned_data.get('tag')).save()


class CategoryForm(forms.Form):
    category = forms.CharField(widget=forms.TextInput)
    model = Category

    def clean_category(self):
        category = self.cleaned_data.get('category').strip()
        if len(category) > 15:
            raise forms.ValidationError('タグ名は 15 文字以下にして下さい')
        if Category.exists(category=category):
            raise forms.ValidationError('このカテゴリは既に存在します')
        return category

    def save(self):
        Category(category=self.cleaned_data.get('category')).save()
