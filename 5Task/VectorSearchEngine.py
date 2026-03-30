import os
import math
from collections import Counter


class VectorSearchEngine:
    def __init__(self, docs_folder):
        self.docs_folder = docs_folder
        self.documents = {}   # doc_id -> {term: tfidf}
        self.idf_map = {}     # term -> idf

    def load_documents(self):
        if not os.path.exists(self.docs_folder):
            raise FileNotFoundError(f"Папка не найдена: {self.docs_folder}")

        for filename in sorted(os.listdir(self.docs_folder), key=self._file_sort_key):
            if not filename.endswith(".txt"):
                continue

            doc_id = filename.replace(".txt", "")
            file_path = os.path.join(self.docs_folder, filename)
            term_weights = {}

            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) != 3:
                        continue

                    term = parts[0]

                    try:
                        idf = float(parts[1])
                        tfidf = float(parts[2])
                    except ValueError:
                        continue

                    term_weights[term] = tfidf
                    self.idf_map[term] = idf

            self.documents[doc_id] = term_weights

    def _file_sort_key(self, filename):
        name = filename.replace(".txt", "")
        return int(name) if name.isdigit() else name

    def build_query_vector(self, query):
        words = query.lower().split()
        tf_counter = Counter(words)
        total_words = sum(tf_counter.values())

        if total_words == 0:
            return {}

        query_vector = {}

        for word, count in tf_counter.items():
            tf = count / total_words
            idf = self.idf_map.get(word, 0.0)
            query_vector[word] = tf * idf

        return query_vector

    def cosine_similarity(self, query_vector, doc_vector):
        dot_product = 0.0

        for term, q_weight in query_vector.items():
            dot_product += q_weight * doc_vector.get(term, 0.0)

        query_norm = math.sqrt(sum(weight ** 2 for weight in query_vector.values()))
        doc_norm = math.sqrt(sum(weight ** 2 for weight in doc_vector.values()))

        if query_norm == 0 or doc_norm == 0:
            return 0.0

        return dot_product / (query_norm * doc_norm)

    def search(self, query, top_k=10):
        query_vector = self.build_query_vector(query)
        results = []

        for doc_id, doc_vector in self.documents.items():
            score = self.cosine_similarity(query_vector, doc_vector)
            if score > 0:
                results.append((doc_id, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]


def choose_search_folder():
        print("Выбери режим поиска:")
        print("1 - по терминам (out/result_tokens)")
        print("2 - по леммам (out/result_lemmas)")
        choice = input("Ввод: ").strip()

        if choice == "1":
            return "out/result_tokens"
        return "out/result_lemmas"


if __name__ == "__main__":
    folder = choose_search_folder()

    engine = VectorSearchEngine(folder)
    engine.load_documents()

    print(f"\nЗагружено документов: {len(engine.documents)}")
    print(f"Поиск выполняется по папке: {folder}")

    while True:
        query = input("\nВведите запрос: ").strip()

        if query.lower() in {"exit", "quit", "выход"}:
            print("Поиск завершен.")
            break

        results = engine.search(query, top_k=5)

        if not results:
            print("Ничего не найдено.")
            continue

        print("\nРезультаты поиска:")
        for doc_id, score in results:
            print(f"Документ {doc_id}.txt -> similarity = {score:.6f}")