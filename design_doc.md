# 自転車ショップ予約システム「renv」詳細設計書

## 1. モデル設計

### 1.1. ServiceMenu (修理・整備メニュー)
- `name`: メニュー名 (例: ホイール組み)
- `description`: 説明
- `estimated_duration`: 想定作業時間 (分)
- `price_estimate`: 料金目安 (数値)
- `price_display`: 表示用料金テキスト (例: "¥5,000〜")
- `is_active`: 有効フラグ

### 1.2. BikeInfo (自転車情報)
- `reservation`: ReservationへのOneToOneField
- `manufacturer`: メーカー名
- `model_name`: モデル名
- `details`: 修理・整備箇所の詳細 (TextField)
- `has_parts_brought_in`: パーツ持ち込み有無 (BooleanField)

### 1.3. BikeImage (不具合箇所の写真)
- `bike_info`: BikeInfoへのForeignKey
- `image`: 画像ファイル (ImageField)

### 1.4. TimeSlot (予約可能枠)
- `start_time`: 開始時間
- `end_time`: 終了時間
- `capacity`: 同時対応可能数 (デフォルト1)

### 1.5. BusinessDay / Holiday (営業日・休日)
- `date`: 日付
- `is_holiday`: 休日フラグ
- `note`: 備考 (例: "臨時休業")

### 1.6. WorkHistory (作業履歴・見積もり)
- `reservation`: ReservationへのOneToOneField
- `estimated_amount`: 見積金額
- `actual_amount`: 確定金額
- `completion_photo`: 完了写真
- `admin_comment`: 管理者コメント
- `status`: ステータス (予約中/作業中/完了)

## 2. 画面遷移設計

### 2.1. ユーザー側
1. **トップ/マイページ**: 予約一覧、新規予約ボタン
2. **予約フォーム**:
   - ステップ1: メニュー選択、日時選択 (TimeSlotベース)
   - ステップ2: 自転車情報入力、写真アップロード
   - ステップ3: 確認・完了
3. **予約詳細**: 作業履歴、見積金額の確認

### 2.2. 管理者側 (Dashboardアプリ)
1. **ダッシュボード**: 本日の予約一覧、ステータス別集計
2. **予約管理**: 予約一覧(フィルタ付)、詳細編集
3. **作業管理**: 見積入力、完了報告(写真・コメント)
4. **設定**: メニュー管理、休日設定、タイムスロット設定

## 3. 技術スタック・ライブラリ
- **画像処理**: Pillow (ImageField用)
- **非同期処理/タスク**: Django-crontab (リマインダー用、SQLite環境を考慮)
- **UI**: Tailwind CSS (管理者ダッシュボード用)
