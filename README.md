# コストコ フードセーフティー 模擬試験 — PWA 化キット

iPhone のホーム画面に「アプリ」として置けるようにするためのファイル一式です。

リポジトリ: <https://github.com/Cloud9-MK/food-safety-exam>

---

## 1. 同梱ファイル

```
food-safety-pwa/
├── manifest.json          ← PWA マニフェスト
├── sw.js                  ← Service Worker（オフライン対応）
├── index.html             ← トップメニュー（Vol.1〜5 を選ぶ画面）
├── pwa_snippet.html       ← vol1〜5 の <head> に貼り付けるスニペット
├── inject_pwa.py          ← vol1〜5 に自動でスニペットを差し込む Python スクリプト
├── _build_icons.py        ← アイコンを再生成したい時用（実行は任意）
├── icons/
│   ├── icon-64.png
│   ├── icon-180.png            ← Apple Touch Icon
│   ├── icon-192.png
│   ├── icon-512.png
│   ├── icon-192-maskable.png
│   └── icon-512-maskable.png
└── README.md              ← このファイル
```

---

## 2. 全体の流れ（最短ルート）

1. ローカルの GitHub リポジトリ `food-safety-exam` をクローン（または `git pull`）
2. このフォルダ内のファイルを **リポジトリ直下** にコピー  
   （`food_safety_exam_vol1.html` 〜 `vol5.html` と同じ階層）
3. `python3 inject_pwa.py` を実行して、vol1〜5 の `<head>` に PWA 設定を追加
4. `git add .` → `git commit -m "Add PWA support"` → `git push`
5. GitHub Pages が更新されたら、iPhone の Safari で
   <https://cloud9-mk.github.io/food-safety-exam/> を開く
6. 共有ボタン → 「ホーム画面に追加」

---

## 3. ステップ詳細

### 3-1. ファイル配置

リポジトリ直下に、以下のように配置してください（既存ファイルは触らない）。

```
food-safety-exam/
├── food_safety_exam_vol1.html      ← 既存
├── food_safety_exam_vol2.html      ← 既存
├── food_safety_exam_vol3.html      ← 既存
├── food_safety_exam_vol4.html      ← 既存
├── food_safety_exam_vol5.html      ← 既存
├── index.html                      ← 新規（このフォルダから）
├── manifest.json                   ← 新規
├── sw.js                           ← 新規
├── icons/                          ← 新規（フォルダごと）
│   └── ...
└── inject_pwa.py                   ← 新規（あとで実行）
```

### 3-2. vol1〜5 の HTML に PWA 設定を追加

**方法 A：自動（推奨）**

```bash
cd <food-safety-exam リポジトリのフォルダ>
python3 inject_pwa.py
```

実行すると、vol1〜5 の `</head>` 直前に必要なタグが入ります。
元ファイルは `food_safety_exam_vol1.html.bak` などにバックアップされます。

**方法 B：手作業（GitHub の Web 編集画面で直接やる場合）**

`pwa_snippet.html` の中の **「↓↓↓ ここから ↓↓↓」と「↑↑↑ ここまで ↑↑↑」の間**
を、vol1〜5 の `<head>` 内（`<title>` の下あたり）にコピペしてください。
5ファイルすべてに同じものを入れます。

### 3-3. Git へコミット & プッシュ

```bash
git add .
git commit -m "Add PWA support (manifest, service worker, icons, menu)"
git push
```

GitHub Pages は通常 1〜2 分で反映されます。

### 3-4. iPhone でホーム画面に追加

1. **Safari** で <https://cloud9-mk.github.io/food-safety-exam/> を開く  
   （`index.html` は省略可）
2. 画面下の **共有ボタン**（□に↑のアイコン）をタップ
3. 「**ホーム画面に追加**」を選ぶ
4. 名前を確認して「追加」

これで、iPhone のホーム画面にコストコ赤×青のアイコンが追加され、
タップすると Safari の UI が出ない **スタンドアロンアプリ** として開きます。

---

## 4. 動作確認のポイント

- ホーム画面アイコンをタップしたとき、Safari のアドレスバーが出ない（= スタンドアロン）  
- 一度開いたあとに機内モードにしても、Vol.1〜5 が表示できる（= オフライン対応）  
- アイコンが赤×青のコストコカラーで表示されている

うまくいかない時は、Safari の **設定 → Safari → 履歴と Web サイトデータを消去** で
キャッシュを消してから再度ホーム画面に追加してください。

---

## 5. 内容を更新したいとき

HTML を更新したあとに **アプリ側で最新版を取りに行かせる** には、
`sw.js` の冒頭の

```js
const CACHE_VERSION = 'v1.0.0';
```

を `v1.0.1` などに上げて、コミット & プッシュしてください。
次回起動時に古いキャッシュが破棄されます。

---

## 6. よくあるトラブル

| 症状 | 対処 |
|---|---|
| ホーム画面に追加してもアイコンが汎用のものになる | `icons/icon-180.png` がリポジトリにアップされているか確認 |
| `manifest.json` が読み込まれない | ブラウザの開発者ツールでネットワークタブを開き、404 が出ていないか確認 |
| 内容を変えても古いまま | `sw.js` の `CACHE_VERSION` を上げる、または iPhone でアプリを一度削除してから再追加 |
| Safari ではなく Chrome から追加した | iOS では PWA インストールは **Safari からのみ** 可能 |

---

ご不明点があれば、何でも聞いてください！
