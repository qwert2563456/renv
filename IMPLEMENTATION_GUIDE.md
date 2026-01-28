# renv - 自転車ショップ予約システム 実装ガイド

## プロジェクト概要

本プロジェクトは、既存のDjangoベースの来店予約システム「renv」を、自転車ショップ向けの高度な予約・管理システムへと拡張したものです。

## 実装済み機能

### 1. メニュー詳細化とバイク情報の管理

**新規モデル:**
- `ServiceMenu`: 修理・整備メニュー（ホイール組み、フレーム塗装、メンテナンス、フィッティング、カスタムオーダー相談）
- `BikeInfo`: 自転車情報（メーカー、モデル名、詳細情報）
- `BikeImage`: 不具合箇所の写真（複数アップロード対応）

**特徴:**
- 各メニューに想定作業時間と料金目安を設定
- 予約時に自転車情報と写真を事前入力可能
- 管理者がメニューを自由に追加・編集可能

### 2. 柔軟な予約枠管理

**新規モデル:**
- `TimeSlot`: 予約可能な時間枠（10:00-12:00、14:00-16:00など）
- `BusinessDay`: 営業日管理
- `Holiday`: 定休日・臨時休業日の設定

**特徴:**
- AM/PMの固定枠から、自由な時間枠へ移行
- 同時対応可能数を設定可能
- 定休日・臨時休業日を柔軟に管理

### 3. 作業履歴・見積もり機能

**新規モデル:**
- `WorkHistory`: 作業履歴・見積もり情報

**特徴:**
- 見積金額と確定金額を別途管理
- 完了写真と管理者コメントを保存
- ステータス遷移（予約中 → 作業中 → 完了）

### 4. 管理者専用ダッシュボード

**ビュー:**
- `dashboard_home`: ダッシュボード（本日の予約、今後の予約、ステータス別集計）
- `reservation_list`: 予約一覧（フィルタ機能付）
- `reservation_detail`: 予約詳細・編集
- `work_history_edit`: 作業履歴・見積もり編集
- `service_menu_list/form`: メニュー管理
- `holiday_list/form`: 休日管理

**特徴:**
- スタッフ向けの直感的なUI
- Django標準adminを使用しない独立した管理画面
- 日本語表記で操作しやすい設計

### 5. 通知機能（メール送信）

**ユーティリティ:**
- `email_utils.py`: メール送信関数
  - `send_reservation_confirmation_email()`: 予約完了メール
  - `send_reminder_email()`: 予約前日リマインダーメール
  - `send_work_completion_email()`: 作業完了メール

**Management Command:**
- `send_reminders`: 予約前日のリマインダーメールを一括送信

## ディレクトリ構造

```
karenda_final/
├── reservation_project/
│   ├── settings.py          # メール設定を追加
│   ├── urls.py              # ダッシュボードのURL設定を追加
│   └── ...
├── reservations/
│   ├── models.py            # ServiceMenu, BikeInfo, TimeSlot, Holiday, WorkHistoryを追加
│   ├── forms.py             # BikeInfoForm, ServiceMenuFormを追加
│   ├── views.py             # 既存のビューを保持
│   ├── email_utils.py       # メール送信ユーティリティ（新規）
│   ├── management/
│   │   └── commands/
│   │       └── send_reminders.py  # リマインダーメール送信コマンド（新規）
│   ├── templates/
│   │   └── reservations/    # 既存のテンプレート
│   ├── static/css/          # 既存のCSS
│   └── migrations/          # マイグレーションファイル
├── dashboard/               # 新規アプリ
│   ├── views.py             # 管理者ダッシュボードのビュー
│   ├── urls.py              # ダッシュボードのURL設定
│   ├── templates/
│   │   └── dashboard/       # 管理者ダッシュボードのテンプレート
│   └── ...
└── media/                   # アップロード画像の保存先
```

## セットアップ手順

### 1. 依存パッケージのインストール

```bash
pip install django pillow
```

### 2. マイグレーションの実行

```bash
python manage.py migrate
```

### 3. スーパーユーザーの作成（初回のみ）

```bash
python manage.py createsuperuser
```

### 4. 開発サーバーの起動

```bash
python manage.py runserver
```

### 5. 管理画面へのアクセス

- **ユーザー向け予約画面**: `http://localhost:8000/`
- **管理者ダッシュボード**: `http://localhost:8000/dashboard/`
- **Django Admin**: `http://localhost:8000/admin/`

## 使用方法

### ユーザー側

1. **新規登録**: トップページから新規登録
2. **予約作成**: 「新しい予約を作成」ボタンからメニュー・日時・自転車情報を入力
3. **予約確認**: マイページで予約一覧を確認
4. **予約キャンセル**: マイページからキャンセル可能

### 管理者側

1. **ダッシュボードアクセス**: `/dashboard/` にアクセス（スタッフユーザーで自動認証）
2. **本日の予約確認**: ダッシュボードホームで本日の予約を一目で確認
3. **予約管理**: 「予約管理」から予約を検索・編集
4. **作業履歴入力**: 予約詳細から見積金額・完了写真・コメントを入力
5. **メニュー設定**: 「メニュー設定」から修理・整備メニューを追加・編集
6. **休日設定**: 「休日設定」から定休日・臨時休業日を管理

## メール送信の設定

### 開発環境

デフォルトではコンソール出力（`EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'`）に設定されています。

### 本番環境

`settings.py`のメール設定を以下のように変更してください：

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # または使用するSMTPサーバー
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')  # 環境変数から取得
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')  # 環境変数から取得
DEFAULT_FROM_EMAIL = 'noreply@renv.local'
```

### リマインダーメールの定期実行

`django-crontab`を使用して、毎日午前9時にリマインダーメールを送信するよう設定できます：

```bash
pip install django-crontab
```

`settings.py`に以下を追加：

```python
CRONJOBS = [
    ('0 9 * * *', 'reservations.management.commands.send_reminders'),
]
```

その後、以下を実行：

```bash
python manage.py crontab add
```

## 今後の拡張案

1. **支払い機能**: Stripe/PayPalなどの決済ゲートウェイ統合
2. **顧客管理**: 顧客情報の一元管理、来店履歴の追跡
3. **レポート機能**: 売上レポート、予約状況の分析
4. **SMS通知**: メール以外のSMS通知オプション
5. **API**: 外部システムとの連携用REST API
6. **多言語対応**: 英語など複数言語への対応
7. **モバイルアプリ**: ネイティブモバイルアプリの開発

## トラブルシューティング

### マイグレーションエラー

```bash
# マイグレーションの状況を確認
python manage.py showmigrations

# 特定のマイグレーションを再実行
python manage.py migrate reservations 0005
```

### 画像アップロードが機能しない

1. `MEDIA_ROOT`と`MEDIA_URL`が正しく設定されているか確認
2. `media/`ディレクトリが存在し、書き込み権限があるか確認
3. Pillow がインストールされているか確認：`pip install pillow`

### メール送信が失敗する

1. `EMAIL_BACKEND`が正しく設定されているか確認
2. SMTP認証情報が正しいか確認
3. ファイアウォール/プロキシの設定を確認

## セキュリティに関する注意

- **本番環境では必ず`DEBUG = False`に設定**
- **SECRET_KEYを環境変数から取得**
- **メール認証情報を環境変数から取得**
- **ALLOWED_HOSTSを適切に設定**
- **HTTPSを使用**
- **CSRF保護を有効化**

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## サポート

問題が発生した場合は、GitHubのIssueを作成してください。
