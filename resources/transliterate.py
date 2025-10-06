# -*- coding: utf-8 -*-

# --- Serbian Cyrillic <-> Latin Transliteration ---

_cyr_to_lat = {
    "А": "A", "а": "a",
    "Б": "B", "б": "b",
    "В": "V", "в": "v",
    "Г": "G", "г": "g",
    "Д": "D", "д": "d",
    "Ђ": "Đ", "ђ": "đ",
    "Е": "E", "е": "e",
    "Ж": "Ž", "ж": "ž",
    "З": "Z", "з": "z",
    "И": "I", "и": "i",
    "Ј": "J", "ј": "j",
    "К": "K", "к": "k",
    "Л": "L", "л": "l",
    "Љ": "Lj", "љ": "lj",
    "М": "M", "м": "m",
    "Н": "N", "н": "n",
    "Њ": "Nj", "њ": "nj",
    "О": "O", "о": "o",
    "П": "P", "п": "p",
    "Р": "R", "р": "r",
    "С": "S", "с": "s",
    "Т": "T", "т": "t",
    "Ћ": "Ć", "ћ": "ć",
    "У": "U", "у": "u",
    "Ф": "F", "ф": "f",
    "Х": "H", "х": "h",
    "Ц": "C", "ц": "c",
    "Ч": "Č", "ч": "č",
    "Џ": "Dž", "џ": "dž",
    "Ш": "Š", "ш": "š",
}

# reverse dictionary for Latin -> Cyrillic
_lat_to_cyr = {v: k for k, v in _cyr_to_lat.items()}


def cyr_to_lat(text: str) -> str:
    return "".join(_cyr_to_lat.get(ch, ch) for ch in text)


def lat_to_cyr(text: str) -> str:
    # handle digraphs first
    for digraph in ("Dž", "dž", "Lj", "lj", "Nj", "nj"):
        if digraph in text:
            text = text.replace(digraph, _lat_to_cyr[digraph])
    # then single letters
    for lat, cyr in _lat_to_cyr.items():
        text = text.replace(lat, cyr)
    return text
