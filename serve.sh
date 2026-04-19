#!/bin/bash
# iPhoneからアクセスできるローカルサーバーを起動します
PORT=8080

# ローカルIPアドレスを取得
IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "IPが取得できませんでした")

echo ""
echo "======================================="
echo "  テトリス サーバー起動中"
echo "======================================="
echo ""
echo "  Mac で開く:"
echo "  http://localhost:$PORT"
echo ""
echo "  iPhone (同じWi-Fi) で開く:"
echo "  http://$IP:$PORT"
echo ""
echo "  Ctrl+C で停止"
echo "======================================="
echo ""

# スクリプトのあるディレクトリへ移動
cd "$(dirname "$0")"
python3 -m http.server $PORT
