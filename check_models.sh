#!/bin/bash

# Gemini利用可能モデル確認スクリプト

unset DOCKER_HOST
docker context use desktop-linux > /dev/null 2>&1

echo "==============================="
echo " Gemini 利用可能モデル一覧確認"
echo "==============================="
echo " ※ GEMINI_API_KEYで使用できる"
echo "   モデルの一覧を表示します"
echo " ※ generateContentに対応した"
echo "   モデルには ✅ を表示します"
echo "==============================="
echo ""

docker compose exec -T backend python3 - <<'EOF'
import google.genai as genai, os

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
models = list(client.models.list())

print(f"取得モデル数: {len(models)}件\n")

for m in sorted(models, key=lambda x: x.name):
    actions = getattr(m, "supported_actions", []) or []
    supports_generate = "generateContent" in actions
    mark = "✅" if supports_generate else "  "
    print(f"{mark} {m.name}")

print("\n✅ = generateContent対応（チャットに使用可能）")
EOF

echo ""
echo "==============================="
