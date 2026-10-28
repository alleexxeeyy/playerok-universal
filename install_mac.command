#!/bin/bash

chmod +x "$0" 2>/dev/null

cd "$(dirname "$0")"

echo ""
echo "📦 Установка зависимостей Playerok Universal..."
echo ""

python3 -m pip install -r requirements.txt
STATUS=$?

echo ""
if [ $STATUS -eq 0 ]; then
  echo "✅ Установка завершена!"
else
  echo "❌ Ошибка установки. Проверьте, что Python 3 установлен."
  echo "   Установить: brew install python@3.12"
fi
echo ""
read -n 1 -s -r -p "Нажмите любую клавишу для выхода..."
