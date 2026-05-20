#!/bin/bash

# Имя файла, куда всё сохранится
OUTPUT_FILE="project_export.txt"

# Очищаем старый файл или создаём новый пустой
> "$OUTPUT_FILE"

# Заголовок для структуры
echo "=== ДЕРЕВО ПРОЕКТА (только .py, .html, .css, .js файлы) ===" >> "$OUTPUT_FILE"

# Рисуем структуру, исключая venv и показывая .py, .html, .css, .js файлы
# -P поддерживает несколько расширений через "|"
tree -I "__pycache__|*.pyc|.venv|venv|env|.git|*.log|*.tmp|*.swp|*.DS_Store|*.egg-info" -P "*.py|*.html|*.css|*.js" --prune >> "$OUTPUT_FILE"

# Пустые строки для разделения
echo -e "\n\n" >> "$OUTPUT_FILE"

echo "=== СОДЕРЖИМОЕ .py, .html, .css И .js ФАЙЛОВ ===" >> "$OUTPUT_FILE"

# Ищем .py, .html, .css, .js файлы, полностью исключая venv и мусор
find . -type f \( -name "*.py" -o -name "*.html" -o -name "*.css" -o -name "*.js" \) \
    -not -path "*/__pycache__/*" \
    -not -path "*/.venv/*" \
    -not -path "*/venv/*" \
    -not -path "*/.git/*" \
    -not -name "*.pyc" \
    | sort \
    | while IFS= read -r file; do
        # Рисуем разделитель
        echo "--------------------------------------------------" >> "$OUTPUT_FILE"
        # Пишем путь к файлу
        echo "ФАЙЛ: $file" >> "$OUTPUT_FILE"
        echo "--------------------------------------------------" >> "$OUTPUT_FILE"
        # Выводим содержимое файла
        cat "$file" >> "$OUTPUT_FILE"
        # Добавляем пустую строку после содержимого
        echo -e "\n" >> "$OUTPUT_FILE"
    done

echo "Готово! .py, .html, .css, .js файлы (исключая venv) сохранены в: $OUTPUT_FILE"
