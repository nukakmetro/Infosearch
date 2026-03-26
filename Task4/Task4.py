import os
import math
from collections import Counter

TOKENS_DIR = "out/tokens"
LEMMAS_DIR = "out/lemmas"

TOKENS_RESULT_DIR = "out/result_tokens"
LEMMAS_RESULT_DIR = "out/result_lemmas"


def load_documents(folder):
    documents = {}

    for filename in os.listdir(folder):
        if filename.endswith(".txt"):
            doc_id = int(filename.replace(".txt", ""))
            path = os.path.join(folder, filename)

            with open(path, "r", encoding="utf-8") as file:
                documents[doc_id] = file.read().split()

    return dict(sorted(documents.items()))


def build_vocabulary(documents):
    vocabulary = set()
    for words in documents.values():
        vocabulary.update(words)
    return sorted(vocabulary)


def calculate_idf(documents, vocabulary):
    total_docs = len(documents)
    idf = {}

    for term in vocabulary:
        docs_with_term = 0
        for words in documents.values():
            if term in words:
                docs_with_term += 1

        idf[term] = math.log(total_docs / docs_with_term) if docs_with_term > 0 else 0.0

    return idf


def save_tfidf_files(documents, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    vocabulary = build_vocabulary(documents)
    idf = calculate_idf(documents, vocabulary)

    for doc_id, words in documents.items():
        total_words = len(words)
        counts = Counter(words)

        output_path = os.path.join(output_folder, f"{doc_id}.txt")

        with open(output_path, "w", encoding="utf-8") as out_file:
            for term, count in sorted(counts.items()):
                tf = count / total_words if total_words > 0 else 0.0
                tf_idf = tf * idf[term]
                out_file.write(f"{term} {idf[term]:.6f} {tf_idf:.6f}\n")


def main():
    token_documents = load_documents(TOKENS_DIR)
    lemma_documents = load_documents(LEMMAS_DIR)

    save_tfidf_files(token_documents, TOKENS_RESULT_DIR)
    save_tfidf_files(lemma_documents, LEMMAS_RESULT_DIR)

    print("Готово.")
    print(f"Файлы для токенов сохранены в: {TOKENS_RESULT_DIR}")
    print(f"Файлы для лемм сохранены в: {LEMMAS_RESULT_DIR}")


if __name__ == "__main__":
    main()