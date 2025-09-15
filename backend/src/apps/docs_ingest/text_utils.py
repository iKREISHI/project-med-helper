from __future__ import annotations

import io
import re
import statistics
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

# Логгер модуля парсинга/чанкинга
logger = logging.getLogger(__name__)

def _import_fitz():
    """Импорт PyMuPDF с поддержкой альтернативного имени пакета.
    Возвращает модуль с API fitz/pymupdf или None, если импорт не удался.
    """
    try:
        import fitz as _f
        if getattr(_f, "open", None):
            return _f
    except Exception:
        pass
    try:
        import pymupdf as _pf
        return _pf
    except Exception:
        return None

try:
    import fitz  # type: ignore
except Exception:
    fitz = _import_fitz()


_HARD_BREAK_PATTERN = re.compile(r"\n\s*\n+")  # параграфные разрывы
_SOFT_BREAK_PATTERN = re.compile(r"(?<!\.)\n(?!\n)")  # мягкие переносы строк внутри абзацев
_HYPHEN_WRAP_PATTERN = re.compile(r"(\w+)-\n(\w+)")   # перенос по дефису
_MULTI_SPACE = re.compile(r"[ \t]{2,}")

_BULLET_LINE = re.compile(r"^\s*([•\-–—]\s+|\d+[.)]\s+)")


def _fix_linebreaks(text: str) -> str:
    """
    Нормализует переносы строк:
    - склеивает слова, разорванные дефисом на конце строки (реальный перенос)
    - мягкие переносы превращает в пробел
    - двойные/тройные переносы оставляет как параграфные
    - чистит лишние пробелы
    """
    if not text:
        return text

    # Сначала восстановим слова, перенесённые по дефису (строка заканчивается -\n)
    text = _HYPHEN_WRAP_PATTERN.sub(r"\1\2", text)

    # Сохраним параграфные разрывы, временно заменив их на маркер
    text = text.replace("\r\n", "\n")
    text = _HARD_BREAK_PATTERN.sub("<<<PARA>>>", text)

    # В списках/маркерах часто важно сохранять переносы строк — оставим их как есть
    # Для остальных одиночных \n превращаем их в пробел
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        if not _BULLET_LINE.match(ln.strip()):
            lines[i] = ln.replace("\n", " ")
    text = "\n".join(lines)

    # Вернём параграфы
    text = text.replace("<<<PARA>>>", "\n\n")

    # Уберём случайные одиночные переводы строк внутри параграфов
    def _softfix(block: str) -> str:
        # внутри одного параграфа одиночные переводы строк -> пробел
        block = _SOFT_BREAK_PATTERN.sub(" ", block)
        # множественные пробелы -> один
        block = _MULTI_SPACE.sub(" ", block)
        return block.strip()

    paragraphs = [p for p in text.split("\n\n") if p.strip()]
    paragraphs = [_softfix(p) for p in paragraphs]
    return "\n\n".join(paragraphs).strip()


@dataclass
class _Span:
    text: str
    size: float
    bold: bool


def _pdf_page_to_text_and_spans(page) -> Tuple[str, List[_Span]]:
    """
    Возвращает текст страницы и список span'ов (для детекции заголовков).
    """
    d = page.get_text("dict")
    spans: List[_Span] = []
    lines_text: List[str] = []

    for block in d.get("blocks", []):
        for line in block.get("lines", []):
            line_text_parts = []
            for span in line.get("spans", []):
                t = span.get("text", "")
                if not t:
                    continue
                size = float(span.get("size", 0.0) or 0.0)
                flags = int(span.get("flags", 0) or 0)
                bold = bool(flags & 2)  # у PyMuPDF 2 обычно соответствует bold
                spans.append(_Span(text=t, size=size, bold=bold))
                line_text_parts.append(t)
            if line_text_parts:
                lines_text.append("".join(line_text_parts))
        # пустая строка между блоками
        lines_text.append("")

    raw = "\n".join(lines_text)
    return _fix_linebreaks(raw), spans

# ===== Новая логика конвертации PDF -> Markdown (упрощённая интеграция) =====
# Часть функций перенесена из предоставленного скрипта и адаптирована под наш интерфейс

BULLET_CHARS = {"•", "◦", "▪", "‣", "–", "—", "-", "∙"}
NUMERIC_HIER_RE = re.compile(r"^\s*((?:\d+)(?:\.\d+)*)(?:[\.\)])?\s+(.*)$")
WHITESPACE_RE = re.compile(r"\s+")
HYPHEN_CHARS = "-\u2011\u00ad"

@dataclass
class _Seg:
    text: str
    bold: bool = False
    italic: bool = False


def _normalize_keep_edge_spaces(s: str) -> str:
    """Сжимает внутренние пробелы, сохраняя по одному ведущему/замыкающему при их наличии."""
    if not s:
        return s
    lead = s[0].isspace()
    tail = s[-1].isspace()
    core = WHITESPACE_RE.sub(" ", s).strip()
    if lead:
        core = " " + core
    if tail:
        core = core + " "
    return core


def _is_word_char(ch: Optional[str]) -> bool:
    return bool(ch) and (ch.isalnum() or ch in "ЁёА-яA-Za-z")


def _needs_space_between(a: str, b: str) -> bool:
    if not a or not b:
        return False
    la, fb = a[-1], b[0]
    if la in HYPHEN_CHARS:
        return False
    if la.isspace() or fb.isspace():
        return False
    if la in "([{/\\'\"«" or fb in ")] }\\'\"».,;:!?":
        return False
    return _is_word_char(la) and _is_word_char(fb)


def _add_missing_spaces(segs: List[_Seg]) -> List[_Seg]:
    """Вставляет недостающие пробелы между сегментами (даже разностилевыми)."""
    if not segs:
        return segs
    res: List[_Seg] = [
        _Seg(segs[0].text, segs[0].bold, segs[0].italic)
    ]
    for s in segs[1:]:
        prev = res[-1]
        if _needs_space_between(prev.text, s.text):
            prev.text += " "
        res.append(_Seg(s.text, s.bold, s.italic))
    return res


def _combine_adjacent_same_style(segs: List[_Seg]) -> List[_Seg]:
    res: List[_Seg] = []
    for s in segs:
        if not s.text:
            continue
        if res and res[-1].bold == s.bold and res[-1].italic == s.italic:
            if _needs_space_between(res[-1].text, s.text):
                res[-1].text += " "
            res[-1].text += s.text
        else:
            res.append(_Seg(s.text, s.bold, s.italic))
    return res


def _last_visible_char(segs: List[_Seg]) -> Optional[str]:
    for s in reversed(segs):
        if s.text:
            return s.text[-1]
    return None


def _first_visible_char(segs: List[_Seg]) -> Optional[str]:
    for s in segs:
        if s.text:
            return s.text[0]
    return None


def _join_line_segments(cur: List[_Seg], new: List[_Seg]) -> List[_Seg]:
    """Склейка строк в абзац: переносы по дефису, пробелы, схлопывание стиля."""
    if not cur:
        return new[:]
    if not new:
        return cur[:]

    lv = _last_visible_char(cur)
    hyphen_re = re.compile(rf"[{HYPHEN_CHARS}]\s*$")
    if lv and lv in HYPHEN_CHARS:
        # убрать дефис переноса
        for i in range(len(cur) - 1, -1, -1):
            if not cur[i].text:
                continue
            cur[i].text = hyphen_re.sub("", cur[i].text)
            if cur[i].text:
                break
        # без пробела
    else:
        fv = _first_visible_char(new)
        need_space = True
        if not cur[-1].text or cur[-1].text.endswith(" "):
            need_space = False
        if fv and fv in " .,;:!?)]—–":
            need_space = False
        if need_space:
            cur.append(_Seg(" "))

    if cur and new and cur[-1].bold == new[0].bold and cur[-1].italic == new[0].italic:
        if _needs_space_between(cur[-1].text, new[0].text):
            cur[-1].text += " "
        cur[-1].text += new[0].text
        new = new[1:]

    cur.extend(new)
    cur = _add_missing_spaces(cur)
    return _combine_adjacent_same_style(cur)


def _escape_md(text: str) -> str:
    return (
        text.replace("\\", "\\\\").replace("*", "\\*")
        .replace("_", "\\_").replace("`", "\\`")
    )


def _segments_to_markdown(segs: List[_Seg]) -> str:
    segs = _combine_adjacent_same_style(segs)
    out: List[str] = []
    for s in segs:
        t = _escape_md(s.text)
        if s.bold and s.italic:
            out.append(f"***{t}***")
        elif s.bold:
            out.append(f"**{t}**")
        elif s.italic:
            out.append(f"*{t}*")
        else:
            out.append(t)
    s = "".join(out)
    s = re.sub(r"[ \t]+", " ", s).strip()
    return s


def _spans_to_segments(spans: List[dict]) -> Tuple[List[_Seg], float]:
    segs: List[_Seg] = []
    max_size = 0.0
    for sp in spans:
        txt = sp.get("text", "")
        if not txt:
            continue
        flags = int(sp.get("flags", 0))
        is_bold = bool(flags & 2)
        is_italic = bool(flags & 1)
        max_size = max(max_size, float(sp.get("size", 0.0)))
        t = _normalize_keep_edge_spaces(txt)
        if t:
            segs.append(_Seg(t, is_bold, is_italic))
    segs = _add_missing_spaces(segs)
    return segs, max_size


def _lines_from_page_dict(page_dict: dict) -> List[Tuple[int, dict, List[dict]]]:
    res = []
    for bi, block in enumerate(page_dict.get("blocks", [])):
        if block.get("type", 0) != 0:
            continue
        for line in block.get("lines", []):
            res.append((bi, line, line.get("spans", [])))
    return res


def _gather_font_stats(doc, pages_idx: List[int]) -> Dict[str, float]:
    sizes: List[float] = []
    for pi in pages_idx:
        page = doc.load_page(pi)
        data = page.get_text("dict")
        for block in data.get("blocks", []):
            if block.get("type", 0) != 0:
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    sz = float(span.get("size", 0))
                    if sz > 0:
                        sizes.append(sz)
    if not sizes:
        stats = {"median": 10.0, "max": 12.0}
        logger.debug("[parse] Не удалось собрать статистику шрифтов, используем значения по умолчанию: %s", stats)
        return stats
    sizes.sort(); n = len(sizes)
    median = sizes[n // 2] if n % 2 else 0.5 * (sizes[n // 2 - 1] + sizes[n // 2])
    stats = {"median": float(median), "max": float(sizes[-1])}
    logger.debug("[parse] Статистика шрифтов: median=%.2f, max=%.2f, samples=%s", stats["median"], stats["max"], len(sizes))
    return stats


def _heading_level_for_size(size: float, median: float, max_sz: float) -> int:
    if size >= max_sz * 0.97 and size > median * 1.6:
        return 1
    if size >= median * 1.8:
        return 1
    if size >= median * 1.45:
        return 2
    if size >= median * 1.3:
        return 3
    return 0


def _is_bullet_line_from_plain(plain: str) -> bool:
    stripped = plain.lstrip()
    if not stripped:
        return False
    if stripped[0] in BULLET_CHARS:
        if stripped.startswith("— ") or stripped.startswith("– "):
            return False
        return True
    return False


def _convert_page_to_markdown(page, font_stats: Dict[str, float]) -> str:
    """Конвертация одной страницы в Markdown (заголовки, списки, абзацы)."""
    pd = page.get_text("dict")
    median = font_stats["median"]; max_sz = font_stats["max"]

    md_lines: List[str] = []
    paragraph: List[_Seg] = []

    page_lines = _lines_from_page_dict(pd)
    found_headings = 0
    bullet_lines = 0
    numbered_lines = 0
    i = 0
    while i < len(page_lines):
        block_idx, line_meta, spans = page_lines[i]
        segs, max_span_size = _spans_to_segments(spans)
        plain_for_logic = re.sub(r"\s+", " ", "".join(s.text for s in segs)).strip()

        # пустая строка -> закрываем абзац
        if not plain_for_logic:
            if paragraph:
                md_lines.append(_segments_to_markdown(paragraph))
                paragraph = []
            md_lines.append("")
            i += 1
            continue

        # проверка заголовка
        h_level = _heading_level_for_size(max_span_size, median, max_sz)
        if h_level > 0 and len(plain_for_logic) <= 200:
            heading_segs = segs[:]
            base_size = max_span_size
            j = i + 1
            while j < len(page_lines):
                block_idx2, _, spans2 = page_lines[j]
                if block_idx2 != block_idx:
                    break
                segs2, size2 = _spans_to_segments(spans2)
                plain2 = re.sub(r"\s+", " ", "".join(s.text for s in segs2)).strip()
                if not plain2:
                    break
                if _heading_level_for_size(size2, median, max_sz) > 0 or size2 >= base_size * 0.9:
                    if NUMERIC_HIER_RE.match(plain2) or _is_bullet_line_from_plain(plain2):
                        break
                    heading_segs = _join_line_segments(heading_segs, segs2)
                    j += 1
                    continue
                break

            if paragraph:
                md_lines.append(_segments_to_markdown(paragraph))
                paragraph = []
            md_lines.append(("#" * h_level) + " " + _segments_to_markdown(heading_segs))
            found_headings += 1
            i = j
            continue

        # многоуровневая нумерация
        m = NUMERIC_HIER_RE.match(plain_for_logic)
        if m:
            if paragraph:
                md_lines.append(_segments_to_markdown(paragraph))
                paragraph = []
            num = m.group(1)
            rest = m.group(2)
            level = num.count(".")
            indent = "  " * level
            md_lines.append(f"{indent}- {num} {rest}")
            numbered_lines += 1
            i += 1
            continue

        # буллет-строки
        if _is_bullet_line_from_plain(plain_for_logic):
            if paragraph:
                md_lines.append(_segments_to_markdown(paragraph))
                paragraph = []
            stripped = plain_for_logic.lstrip()
            if stripped and stripped[0] in BULLET_CHARS:
                md_lines.append("- " + stripped[1:].lstrip())
            else:
                md_lines.append("- " + stripped)
            bullet_lines += 1
            i += 1
            continue

        # обычная строка -> в абзац
        if paragraph:
            paragraph = _join_line_segments(paragraph, segs)
        else:
            paragraph = _combine_adjacent_same_style(segs)
        i += 1

    if paragraph:
        md_lines.append(_segments_to_markdown(paragraph))

    # убрать двойные пустые строки
    cleaned: List[str] = []
    for ln in md_lines:
        if ln == "":
            if cleaned and cleaned[-1] == "":
                continue
        cleaned.append(ln)
    md = "\n".join(cleaned).strip() + "\n"
    logger.debug("[parse] Сводка страницы: заголовков=%s, буллетов=%s, нумерованных=%s, длина=%s", found_headings, bullet_lines, numbered_lines, len(md))
    return md


def _guess_headings_from_spans(spans: List[_Span]) -> List[str]:
    """
    Эвристика: заголовки — это короткие строки с размером шрифта значительно
    больше медианного либо помеченные bold и короткие.
    """
    if not spans:
        return []

    sizes = [s.size for s in spans if s.size > 0]
    if not sizes:
        return []

    med = statistics.median(sizes)
    big = med * 1.25

    # Соберём из span'ов приблизительные строки (упрощённо)
    lines: List[str] = []
    cur: List[_Span] = []
    last_size = None
    for s in spans:
        if last_size is not None and abs(s.size - last_size) > 0.1:
            if cur:
                lines.append("".join(x.text for x in cur).strip())
                cur = []
        cur.append(s)
        last_size = s.size
    if cur:
        lines.append("".join(x.text for x in cur).strip())

    headings = []
    for ln in lines:
        ln_clean = re.sub(r"\s+", " ", ln).strip()
        if not ln_clean:
            continue
        # короткая строка с БОЛЬШИМ размером (или ВСЕ ЗАГЛАВНЫЕ)
        if len(ln_clean) <= 120 and (any(sp.size >= big for sp in spans) or ln_clean.isupper()):
            # фильтруем шум
            if len(ln_clean) >= 5:
                headings.append(ln_clean)
    # дедуп
    seen = set()
    out = []
    for h in headings:
        if h not in seen:
            out.append(h)
            seen.add(h)
    return out


def _parse_pdf(file_like: io.BytesIO) -> Dict[str, Any]:
    """Парсинг PDF в Markdown‑подобный текст с сохранением структуры списков и заголовков.

    Возвращает словарь совместимый с extract_text_with_layout: plain/pages/title.
    plain и pages[i]["text"] содержат Markdown.
    """
    if fitz is None:
        raise RuntimeError(
            "PyMuPDF не найден. Установите пакет 'pymupdf' (или совместимый fitz)."
        )

    doc = fitz.open(stream=file_like.getvalue(), filetype="pdf")
    try:
        page_indexes = list(range(len(doc)))
        logger.info("[parse] PDF открыт: страниц=%s", len(page_indexes))
        font_stats = _gather_font_stats(doc, page_indexes)

        pages: List[Dict[str, Any]] = []
        md_parts: List[str] = []
        all_headings: List[str] = []

        for i in page_indexes:
            page = doc.load_page(i)
            md = _convert_page_to_markdown(page, font_stats)
            pages.append({"number": i + 1, "text": md})
            md_parts.append(md)
            # Попробуем извлечь потенциальные заголовки из Markdown строк
            page_headings = 0
            for line in md.splitlines():
                if line.startswith("# ") or line.startswith("## ") or line.startswith("### "):
                    txt = line.lstrip("# ") .strip()
                    if txt:
                        all_headings.append(txt)
                        page_headings += 1
            logger.debug("[parse] Страница %s: длина MD=%s симв., заголовков=%s", i + 1, len(md), page_headings)

        plain = ("\n\n".join(md_parts)).strip()
        meta_title = (doc.metadata or {}).get("title") or ""
        title = meta_title or (all_headings[0] if all_headings else "")
        logger.info("[parse] Готово: символов всего=%s, заголовок='%s'", len(plain), (title or ""))
        return {"plain": plain, "pages": pages, "title": title}
    finally:
        try:
            doc.close()
        except Exception:
            pass


def _is_docx_signature(b: bytes) -> bool:
    # DOCX — это zip (PK...), но точно определить можно только попытавшись открыть python-docx.
    return b.startswith(b"PK")


def _parse_docx(file_like: io.BytesIO) -> Dict[str, Any]:
    try:
        import docx  # python-docx
    except Exception:
        raise RuntimeError("Для DOCX установите пакет 'python-docx' или конвертируйте файл в PDF.")

    d = docx.Document(file_like)
    paras = [p.text for p in d.paragraphs]
    plain = _fix_linebreaks("\n\n".join(paras))
    # заголовки: стили Heading 1..3
    headings = []
    for p in d.paragraphs:
        st = (p.style.name or "").lower() if p.style else ""
        if "heading" in st and p.text.strip():
            headings.append(p.text.strip())

    pages = [{"number": 1, "text": plain}]  # у DOCX нет страниц — оставим всё в одной
    title = headings[0] if headings else ""
    return {"plain": plain, "pages": pages, "title": title}


def _sniff_content_type(buf: bytes, content_type: str) -> str:
    if content_type:
        return content_type
    if buf.startswith(b"%PDF"):
        return "application/pdf"
    if _is_docx_signature(buf):
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return "application/octet-stream"


def extract_text_with_layout(file_like: io.BytesIO, content_type: str = "") -> Dict[str, Any]:
    """
    Унифицированный экстрактор.
    Возвращает:
      {
        "plain": "<весь текст>",
        "pages": [{"number": int, "text": str}, ...],
        "title": "<заголовок или пусто>"
      }
    """
    # Прочитаем байты и «обнулим» указатель
    raw = file_like.read()
    file_like.seek(0)

    logger.info("[parse] Старт извлечения текста: входных байт=%s", len(raw))
    ct = _sniff_content_type(raw, content_type)
    logger.info("[parse] Определён content-type: %s", ct or "(unknown)")

    if ct == "application/pdf":
        res = _parse_pdf(io.BytesIO(raw))
        logger.info("[parse] Экстракция PDF завершена: страниц=%s, символов=%s", len(res.get("pages", [])), len(res.get("plain", "")))
        return res
    elif ct == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        res = _parse_docx(io.BytesIO(raw))
        logger.info("[parse] Экстракция DOCX завершена: страниц=%s, символов=%s", len(res.get("pages", [])), len(res.get("plain", "")))
        return res
    else:
        # Фоллбэк: просто как есть
        text = _fix_linebreaks(raw.decode("utf-8", errors="ignore"))
        logger.info("[parse] Экстракция текста по умолчанию: символов=%s", len(text))
        return {"plain": text, "pages": [{"number": 1, "text": text}], "title": ""}


# Простая эвристика для заголовков по тексту (когда нет метаданных шрифтов)
_SECTION_REGEX = re.compile(
    r"(?m)^(?:#{1,6}\s+.+)$|^(?:Глава|Раздел|Приложение|ПРИЛОЖЕНИЕ)\b.*$|^(?:\d+(?:\.\d+){0,3})\s+[^\n]{3,120}$"
)


def _estimate_tokens(s: str) -> int:
    # Грубая оценка: 1 слово ~= 1 токен (для большинства эмбеддингов это ок для контроля размера).
    return max(1, len(re.findall(r"\w+", s, flags=re.UNICODE)))


def _sent_split(p: str) -> List[str]:
    # Примитивный сплиттер предложений, достаточно надёжный для ru/en
    parts = re.split(r"(?<=[\.\!\?…])\s+(?=[A-ZА-ЯЁ0-9])", p.strip())
    return [x.strip() for x in parts if x.strip()]


def split_into_chunks(
    parsed: Dict[str, Any],
    target_tokens: int = 350,
    overlap: int = 50,
) -> List[Dict[str, Any]]:
    """
    Делит parsed-текст на чанки ~target_tokens, удерживая контекст разделов (section)
    и приблизительные номера страниц (page_from/page_to).
    """
    pages = parsed.get("pages", []) or [{"number": 1, "text": parsed.get("plain", "")}]
    title = (parsed.get("title") or "").strip()

    # Сконструируем плоский список (page_no, paragraph)
    para_items: List[Tuple[int, str]] = []
    for pg in pages:
        pg_no = int(pg.get("number", 0) or 0) or None
        text = pg.get("text", "") or ""
        for para in [p for p in text.split("\n\n") if p.strip()]:
            para_items.append((pg_no, para.strip()))

    logger.info(
        "[chunk] Старт чанкинга: target_tokens=%s, overlap=%s, параграфов=%s, страниц=%s",
        target_tokens, overlap, len(para_items), len(pages)
    )

    # Пройдёмся по параграфам, выделяя «текущий раздел» по заголовкам
    chunks: List[Dict[str, Any]] = []
    cur_section = title or ""
    cur_chunk_words: List[str] = []
    cur_pages: List[int] = []

    def flush_chunk() -> None:
        nonlocal cur_chunk_words, cur_pages
        if not cur_chunk_words:
            return
        text = " ".join(cur_chunk_words).strip()
        if not text:
            cur_chunk_words = []
            cur_pages = []
            return
        tokens = _estimate_tokens(text)
        page_from = min(cur_pages) if cur_pages else None
        page_to = max(cur_pages) if cur_pages else None
        section_preview = (cur_section[:120] + "…") if len(cur_section) > 120 else cur_section
        chunks.append(
            {
                "text": text,
                "section": section_preview,
                "page_from": page_from,
                "page_to": page_to,
                "tokens": tokens,
            }
        )
        logger.debug(
            "[chunk] Новый чанк: токенов≈%s, страницы=%s-%s, раздел='%s'",
            tokens, page_from, page_to, (section_preview[:60] + ("…" if len(section_preview) > 60 else ""))
        )
        cur_chunk_words = []
        cur_pages = []

    def push_text(s: str, pg_no: Optional[int]) -> None:
        nonlocal cur_chunk_words, cur_pages
        words = s.split()
        i = 0
        while i < len(words):
            need = target_tokens - _estimate_tokens(" ".join(cur_chunk_words))
            if need <= 0:
                # сделаем overlap
                if overlap > 0:
                    # оставим хвост overlap слов как начало следующего чанка
                    tail = cur_chunk_words[-overlap:]
                    flush_chunk()
                    cur_chunk_words.extend(tail)
                    if cur_pages:
                        cur_pages = [cur_pages[-1]]
                else:
                    flush_chunk()
            take = max(1, min(need, len(words) - i))
            cur_chunk_words.extend(words[i : i + take])
            if pg_no:
                cur_pages.append(pg_no)
            i += take

    for pg_no, para in para_items:
        # если параграф похож на заголовок — закрываем текущий чанк и переименовываем раздел
        is_section = bool(_SECTION_REGEX.match(para.strip())) or (
            len(para) < 120 and para.isupper()
        )
        if is_section:
            flush_chunk()
            # Очистим Markdown-префиксы заголовков (например, "## ") и лишние пробелы
            cleaned = re.sub(r"^\s*#{1,6}\s+", "", para.strip())
            cur_section = cleaned.strip()
            logger.debug("[chunk] Новый раздел: '%s'", (cur_section[:100] + ("…" if len(cur_section) > 100 else "")))
            continue

        # длинные параграфы попробуем предварительно разбить по предложениям,
        # чтобы не рвать их в середине
        sents = _sent_split(para)
        if len(" ".join(sents)) < 1.5 * target_tokens:
            push_text(para, pg_no)
        else:
            for s in sents:
                push_text(s, pg_no)

    flush_chunk()

    # страховка: если ничего не получилось
    if not chunks:
        logger.warning("[chunk] Основной алгоритм не дал чанков — используем страховочный разрез по словам")
        text = parsed.get("plain", "")
        words = text.split()
        i = 0
        while i < len(words):
            part = " ".join(words[i : i + target_tokens])
            if not part:
                break
            chunks.append(
                {
                    "text": part,
                    "section": "",
                    "page_from": None,
                    "page_to": None,
                    "tokens": _estimate_tokens(part),
                }
            )
            i += target_tokens - overlap if overlap > 0 else target_tokens

    logger.info("[chunk] Итог чанкинга: создано чанков=%s", len(chunks))
    return chunks
