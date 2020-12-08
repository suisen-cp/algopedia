# Algopedia

アルゴリズムに関する記事を扱う Web システム.

## 環境

- OS : Windows 10 Home
- 使用言語 : Python 3.6.12
- フレームワーク : django 2.2
- ブラウザ : Google Chrome 87.0.4280.66 (Official Build) (64 bit)

## 動作方法

### 準備

[依存パッケージ](/requirements.txt) をインストール

### 開始

```shell
python manage.py runserver
```

正しく動作すれば, 例えば以下のような出力が得られる.

```shell
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
(0.001)
            SELECT name, type FROM sqlite_master
            WHERE type in ('table', 'view') AND NOT name='sqlite_sequence'
            ORDER BY name; args=None
(0.000) SELECT "django_migrations"."app", "django_migrations"."name" FROM "django_migrations"; args=()
November 24, 2020 - 23:16:03
Django version 2.2, using settings 'algopedia.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

<http://127.0.0.1:8000/> にアクセス.

### 動作時

アプリケーションを動かしている間, ターミナルには走っている SQL 文が表示される.

### 終了

ターミナル上で `Ctrl+C` を入力すると終了する.