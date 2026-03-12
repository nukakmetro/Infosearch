import json
import os
from collections import defaultdict

DIR = "../Task3/out/lemmas/"


def build_inverted_index(folder_path: str) -> bool:
    inverted_index = defaultdict(list)

    lemma_files = [
        filename for filename in os.listdir(folder_path)
        if filename.endswith(".txt")
    ]

    for filename in lemma_files:
        name_without_ext = os.path.splitext(filename)[0]

        if not name_without_ext.isdigit():
            continue

        document_id = int(name_without_ext)
        file_path = os.path.join(folder_path, filename)

        with open(file_path, "r", encoding="utf-8") as file:
            for raw_line in file:
                parts = raw_line.split()
                if not parts:
                    continue

                term = parts[0].rstrip(":")
                inverted_index[term].append(document_id)

    for term in inverted_index:
        inverted_index[term] = sorted(set(inverted_index[term]))

    try:
        with open("invert_list.json", "w", encoding="utf-8") as output_file:
            json.dump(inverted_index, output_file, ensure_ascii=False, indent=4)
        return True
    except Exception as error:
        print(error)
        return False


if __name__ == "__main__":
    build_inverted_index(DIR)