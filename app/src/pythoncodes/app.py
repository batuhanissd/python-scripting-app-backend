import sys
import json
import os

def main():
    if len(sys.argv) < 3:
        print("Error: Missing arguments. Usage: python script.py <json_file_path> <output_file_name>")
        return

    json_file_path = sys.argv[1]
    output_file_name = sys.argv[2]

    # JSON dosyasını oku
    try:
        with open(json_file_path, "r", encoding="utf-8") as file:
            bios_ids = json.load(file)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return

    # Çıktı dosyasının tam yolunu belirleyelim
    output_file_path = os.path.join(os.path.dirname(json_file_path), output_file_name+'.txt')

    # Dosyaya yazalım
    try:
        with open(output_file_path, "w", encoding="utf-8") as file:
            for bios_id in bios_ids:
                file.write(f"{bios_id}\n")
        print(f"Successfully wrote to {output_file_path}")
    except Exception as e:
        print(f"Error writing to file: {e}")

if __name__ == "__main__":
    main()
