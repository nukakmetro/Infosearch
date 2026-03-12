from pathlib import Path
import re
from collections import defaultdict

from bs4 import BeautifulSoup
import pymorphy3


# Стоп-слова (служебные слова)
RU_STOPWORDS = {
    "и","а","но","или","да","же","ли","не","ни","то","это","эта","эти","этот","вот","там","тут",
    "в","во","на","по","к","ко","с","со","у","о","об","обо","от","до","из","за","для","над","под",
    "при","про","через","между","без","после","перед",
    "как","так","что","чтобы","когда","если","потому","поскольку","где","куда","откуда",
    "бы","быть","есть",
    "я","ты","он","она","оно","мы","вы","они","меня","тебя","его","ее","её","нас","вас","их",
    "мой","моя","мое","моё","мои","твой","твоя","твое","ваш","ваша","ваше","их","свой","своя","свои",
}

# Поиск русских слов
WORD_RE = re.compile(r"[А-Яа-яЁё]+(?:-[А-Яа-яЁё]+)*")


def html_to_text(html: str) -> str:
    """Удаление HTML-тегов и получение чистого текста."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=" ")
    return re.sub(r"\s+", " ", text).strip()


def is_trash(token: str) -> bool:
    """Проверка токена на мусор."""
    if len(token) < 2:
        return True
    if token in RU_STOPWORDS:
        return True
    if not re.fullmatch(r"[а-яё]+(?:-[а-яё]+)*", token):
        return True
    return False


def file_key(p: Path):
    """Ключ сортировки файлов (по номеру)."""
    return int(p.stem) if p.stem.isdigit() else p.stem


def main():
    """Обработка всех страниц: токены и леммы по каждой странице."""
    pages_dir = Path("pages")
    if not pages_dir.exists():
        raise SystemExit("Нет папки pages.")

    out_tokens_dir = Path("out/tokens")
    out_lemmas_dir = Path("out/lemmas")
    out_tokens_dir.mkdir(parents=True, exist_ok=True)
    out_lemmas_dir.mkdir(parents=True, exist_ok=True)

    morph = pymorphy3.MorphAnalyzer()

    files = sorted(pages_dir.glob("*.txt"), key=file_key)

    for file_path in files:
        raw = file_path.read_bytes()
        html = raw.decode("utf-8", errors="ignore")

        text = html_to_text(html).lower().replace("ё", "е")

        # Токены страницы
        page_tokens = set()
        for w in WORD_RE.findall(text):
            w = w.lower().replace("ё", "е")
            if not is_trash(w):
                page_tokens.add(w)

        tokens_sorted = sorted(page_tokens)
        out_name = f"{file_path.stem}.txt"

        # Сохранение токенов
        (out_tokens_dir / out_name).write_text(
            "\n".join(tokens_sorted) + "\n", encoding="utf-8"
        )

        # Лемматизация
        lemma_map = defaultdict(list)
        for t in tokens_sorted:
            lemma = morph.parse(t)[0].normal_form
            lemma_map[lemma].append(t)

        lines = []
        for lemma in sorted(lemma_map.keys()):
            lines.append(f"{lemma} " + " ".join(sorted(lemma_map[lemma])))

        # Сохранение лемм
        (out_lemmas_dir / out_name).write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )

        print(f"OK {file_path.name}")

    print("Готово.")


if __name__ == "__main__":
    main()