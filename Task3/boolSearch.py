import json
from pprint import pprint

INDEX_FILE = "invert_list.json"
SERVICE_TOKENS = {"(", ")", "and", "or", "not"}
DOCUMENTS = set(range(1, 101))


class QuerySyntaxError(Exception):
    pass


class SearchEngine:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index_data = self._read_index()

    def _read_index(self):
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _docs_for_word(self, word):
        values = self.index_data.get(word)
        return set(values) if values else set()

    def _apply_and(self, left, right):
        return left & right

    def _apply_or(self, left, right):
        return left | right

    def _apply_not(self, value):
        return DOCUMENTS - value

    def _to_postfix(self):
        priority = {"not": 3, "and": 2, "or": 1}
        result = []
        operators = []

        for pos, token in enumerate(self.tokens):
            if token not in SERVICE_TOKENS:
                result.append(token)
                continue

            if token == "(":
                operators.append(token)
                continue

            if token == ")":
                while operators and operators[-1] != "(":
                    result.append(operators.pop())

                if not operators:
                    raise QuerySyntaxError("Ошибка скобок")

                operators.pop()
                continue

            while (
                operators
                and operators[-1] != "("
                and priority.get(operators[-1], 0) >= priority.get(token, 0)
            ):
                result.append(operators.pop())

            operators.append(token)

        while operators:
            result.append(operators.pop())

        return result

    def search(self):
        postfix = self._to_postfix()
        stack = []

        for token in postfix:
            if token not in SERVICE_TOKENS:
                stack.append(self._docs_for_word(token))
            elif token == "not":
                stack.append(self._apply_not(stack.pop()))
            else:
                right = stack.pop()
                left = stack.pop()

                if token == "and":
                    stack.append(self._apply_and(left, right))
                elif token == "or":
                    stack.append(self._apply_or(left, right))

        return sorted(stack[0])


def normalize_query(text):
    prepared = (
        text.replace("(", " ( ")
        .replace(")", " ) ")
        .replace("AND", " and ")
        .replace("OR", " or ")
        .replace("NOT", " not ")
        .lower()
    )
    return prepared.split()


def main():
    query = input("Введите поисковый запрос: ")

    tokens = normalize_query(query)
    engine = SearchEngine(tokens)

    result = engine.search()
    pprint(result)


if __name__ == "__main__":
    main()