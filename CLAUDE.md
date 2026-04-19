# Claude Code 作業メモ

## 環境情報
- Mac ユーザー名: `okazakikazuhiro`
- Mac ローカルIP: `192.168.150.104`（変わる可能性あり）
- このLinux環境からMacへの直接SSHは不可（別ネットワーク）

## セッション開始時にMacでやること

### 1. ngrok起動（外部→Mac接続のトンネル）
```
ngrok http 8080
```
起動後に表示される `https://xxxx.ngrok-free.dev` のURLをClaudeに伝える。

### 2. ローカルHTTPサーバー起動（別タブ）
```
cd ~/Downloads
python3 -m http.server 8080
```

## ファイル転送方法（URLコピペ問題の回避）

このチャット上のURLをコピペするとzshで `<>` が付いてエラーになる。  
URLを使わずにファイルを転送するには **base64+gzip方式** を使う。

### このLinux環境でコマンド生成
```bash
gzip -c ファイル名 | base64 -w 0
```
↓ 出力をPythonコマンドに埋め込んでMacで実行：
```bash
python3 -c "import base64,gzip,os;open(os.path.expanduser('~/Downloads/ファイル名'),'wb').write(gzip.decompress(base64.b64decode('BASE64文字列')))"
```

## コマンド渡しの注意点
- **1行ずつ**渡す（複数行の一括コピペはzshがパースエラー）
- URLは絶対にコードブロック外に書かない（`<>`が自動付与される）
- `https://` を含む文字列はすべてbase64経由か、手入力を促す

## SSH設定（将来用）
MacのSSHは有効済み。ただし直接SSH接続は不可。  
ngrok TCPトンネル経由なら可能：
```
ngrok tcp 22
```
→ 表示された `tcp://x.tcp.ngrok.io:XXXXX` をClaudeに伝える。

## 作成済みファイル
- `tetris.html` - iPhoneで動くテトリスゲーム
- `serve.sh` - ローカルサーバー起動スクリプト（Mac用）
- `gh-pages` ブランチ - GitHub Pages用（要: リポジトリ設定で有効化）

## iOS Native アプリ開発（次回の続き）
- Xcode 26.2 インストール済み（/Volumes/Macintosh HD/Applications/Xcode.app）
- Apple Developer アカウント未設定（次回やること）
- 次のステップ:
  1. developer.apple.com でDeveloper登録（$99/年）
  2. Xcode → Settings → Accounts にApple IDを追加
  3. TestFlight配布に向けてアプリ開発スタート
