#!/bin/bash

# Gemini生成モデル切り替えスクリプト

# ==============================
# モデル候補リスト（追加・編集はここ）
# ==============================
MODELS=(
  "models/gemini-2.0-flash"
  "models/gemini-2.0-flash-lite"
  "models/gemini-2.0-flash-lite-001"
  "models/gemini-2.5-flash"
  "models/gemini-2.5-flash-lite"
  "models/gemini-3.1-flash-lite"
)
# ==============================

unset DOCKER_HOST
docker context use desktop-linux > /dev/null 2>&1

RAG_FILE="src/backend/app/rag.py"

echo "==============================="
echo " Gemini 生成モデル切り替え"
echo "==============================="
echo ""

# 現在のモデルを表示
CURRENT=$(grep 'GENERATION_MODEL = ' $RAG_FILE | head -1 | sed 's/.*"\(.*\)"/\1/')
echo " 現在のモデル: $CURRENT"
echo ""

# ==============================
# 各モデルのクォータ状態を確認
# ==============================
echo " モデルの使用可否を確認中..."
echo ""

# ステータスを配列で管理
STATUS=()
for model in "${MODELS[@]}"; do
  result=$(docker compose exec -T backend python3 - << EOF
import google.genai as genai, os
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
try:
    r = client.models.generate_content(model="$model", contents="hi")
    print("OK")
except Exception as e:
    err = str(e)
    if "429" in err:
        print("QUOTA")
    elif "404" in err:
        print("NOTFOUND")
    else:
        print("ERROR")
EOF
)
  STATUS+=("$result")
done

# ==============================
# モデル候補を表示
# ==============================
echo " 切替先を選択してください:"
echo "   0) キャンセル（中断）"
for i in "${!MODELS[@]}"; do
  model="${MODELS[$i]}"
  status="${STATUS[$i]}"

  case "$status" in
    OK)       mark="✅ 使用可能" ;;
    QUOTA)    mark="❌ クォータ超過" ;;
    NOTFOUND) mark="⚠️  使用不可" ;;
    *)        mark="⚠️  エラー" ;;
  esac

  if [ "$model" = "$CURRENT" ]; then
    echo "   $((i+1))) $model  ← 現在  $mark"
  else
    echo "   $((i+1))) $model  $mark"
  fi
done
echo ""

# 番号入力
read -p " 番号を入力 [0-${#MODELS[@]}]: " SELECT
echo ""

# 0を選択した場合は中断
if [ "$SELECT" = "0" ]; then
  echo " ⏹️  キャンセルしました。モデルは変更されていません。"
  exit 0
fi

# 入力値チェック
if ! [[ "$SELECT" =~ ^[0-9]+$ ]] || [ "$SELECT" -lt 1 ] || [ "$SELECT" -gt "${#MODELS[@]}" ]; then
  echo " ❌ 無効な番号です。終了します。"
  exit 1
fi

TARGET_MODEL="${MODELS[$((SELECT-1))]}"

# 同じモデルを選んだ場合
if [ "$TARGET_MODEL" = "$CURRENT" ]; then
  echo " ⏭️  既に $TARGET_MODEL が設定されています。変更不要です。"
  exit 0
fi

# モデルを切り替え
sed -i '' "s|GENERATION_MODEL = \"models/.*\"|GENERATION_MODEL = \"$TARGET_MODEL\"|" $RAG_FILE

# 確認
AFTER=$(grep 'GENERATION_MODEL = ' $RAG_FILE | head -1 | sed 's/.*"\(.*\)"/\1/')
echo " ✅ 変更完了: $CURRENT → $AFTER"
echo ""

# 再ビルド＆再起動
echo " バックエンドを再ビルド中..."
docker compose up -d --build backend

echo ""
echo "==============================="
echo " 切り替え完了"
echo "==============================="
