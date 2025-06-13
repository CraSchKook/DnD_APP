import os

# Укажи путь к папке с проектом
root_dir = r'F:\Prog_pc\Prog\DnD_app\app'  # ← замени на путь к твоему проекту
#root_dir = r'F:\Prog_pc\Prog\shadowstar-telegram-mini-app-master'
output_file = 'project_dump_x.txt'

with open(output_file, 'w', encoding='utf-8') as out_f:
    for foldername, subfolders, filenames in os.walk(root_dir):
        for filename in filenames:
            file_path = os.path.join(foldername, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                content = f"[Ошибка при чтении файла: {e}]"

            out_f.write(f"\n=== ФАЙЛ: {file_path} ===\n")
            out_f.write(content)
            out_f.write("\n\n")
