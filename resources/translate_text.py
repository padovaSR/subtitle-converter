# -*- coding: utf-8 -*-


import asyncio
try:
    from googletrans import Translator
except ImportError:
    pass


lang_dict = {
    "Srpski": "sr",
    "Engleski": "en",
    "Ruski": "ru",
    "Slovenački": "sl",
    "Hrvatski": "hr",
    "Bosanski": "bs",
    "Makedonski": "mk",
    "Bugarski": "bg",
    "Nemački": "de",
    "Francuski": "fr",
    "Italijanski": "it",
    "Španski": "es",
    "Portugalski": "pt",
    "Holandski": "nl",
    "Grčki": "el",
    "Kineski": "zh",
    "Japanski": "ja",
    "Korejski": "ko",
    "Arapski": "ar",
    "Turski": "tr",
    "Poljski": "pl",
    "Češki": "cs",
    "Slovački": "sk",
    "Mađarski": "hu",
    "Finski": "fi",
    "Švedski": "sv",
    "Norveški": "no",
    "Danski": "da",
    "Hebrejski": "he",
    "Hindi": "hi",
    "Vijetnamski": "vi",
    "Indonezijski": "id",
    "Malezijski": "ms",
}


def translate_sync(text, src=None, dest=None):
    async def _do_translate():
        async with Translator() as translator:
            return await translator.translate(text, src=src, dest=dest)
    return asyncio.run(_do_translate())
