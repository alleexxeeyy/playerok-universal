#!/bin/bash

chmod +x "$0" 2>/dev/null

cd "$(dirname "$0")"

echo ""
echo "🚀 Запуск Playerok Universal..."
echo ""

python3 bot.py
STATUS=$?

echo ""
if [ $STATUS -ne 0 ]; then
  read -n 1 -s -r -p "Нажмите любую клавишу для выхода..."
fi
