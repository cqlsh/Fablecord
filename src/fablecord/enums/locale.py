"""
The MIT License (MIT)

Copyright (c) 2026-present cqlsh

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from .base import Enum

class Locale(Enum):
    """
    A language the Discord client can be set to.

    Interactions carry the locale of the user and of the guild, and
    command names and descriptions can be translated per locale. The
    values are Discord's own codes, most of them without a region.
    :attr:`language_code` gives the full tag for formatting libraries,
    :attr:`language` just the language for picking a translation.
    """

    american_english = "en-US"
    """
    English, US.
    """

    british_english = "en-GB"
    """
    English, UK.
    """

    bulgarian = "bg"
    """
    Bulgarian, shown as български.
    """

    chinese = "zh-CN"
    """
    Chinese, China, shown as 中文.
    """

    taiwan_chinese = "zh-TW"
    """
    Chinese, Taiwan, shown as 繁體中文.
    """

    croatian = "hr"
    """
    Croatian, shown as Hrvatski.
    """

    czech = "cs"
    """
    Czech, shown as Čeština.
    """

    indonesian = "id"
    """
    Indonesian, shown as Bahasa Indonesia.
    """

    danish = "da"
    """
    Danish, shown as Dansk.
    """

    dutch = "nl"
    """
    Dutch, shown as Nederlands.
    """

    finnish = "fi"
    """
    Finnish, shown as Suomi.
    """

    french = "fr"
    """
    French, shown as Français.
    """

    german = "de"
    """
    German, shown as Deutsch.
    """

    greek = "el"
    """
    Greek, shown as Ελληνικά.
    """

    hindi = "hi"
    """
    Hindi, shown as हिन्दी.
    """

    hungarian = "hu"
    """
    Hungarian, shown as Magyar.
    """

    italian = "it"
    """
    Italian, shown as Italiano.
    """

    japanese = "ja"
    """
    Japanese, shown as 日本語.
    """

    korean = "ko"
    """
    Korean, shown as 한국어.
    """

    latin_american_spanish = "es-419"
    """
    Spanish, Latin America, shown as Español, LATAM.
    """

    lithuanian = "lt"
    """
    Lithuanian, shown as Lietuviškai.
    """

    norwegian = "no"
    """
    Norwegian, shown as Norsk.
    """

    polish = "pl"
    """
    Polish, shown as Polski.
    """

    brazil_portuguese = "pt-BR"
    """
    Portuguese, Brazil, shown as Português do Brasil.
    """

    romanian = "ro"
    """
    Romanian, shown as Română.
    """

    russian = "ru"
    """
    Russian, shown as Pусский.
    """

    spain_spanish = "es-ES"
    """
    Spanish, Spain, shown as Español.
    """

    swedish = "sv-SE"
    """
    Swedish, shown as Svenska.
    """

    thai = "th"
    """
    Thai, shown as ไทย.
    """

    turkish = "tr"
    """
    Turkish, shown as Türkçe.
    """

    ukrainian = "uk"
    """
    Ukrainian, shown as Українська.
    """

    vietnamese = "vi"
    """
    Vietnamese, shown as Tiếng Việt.
    """

    __regions: dict[str, str] = {
        bulgarian: "bg-BG",
        croatian: "hr-HR",
        czech: "cs-CZ",
        indonesian: "id-ID",
        danish: "da-DK",
        dutch: "nl-NL",
        finnish: "fi-FI",
        french: "fr-FR",
        german: "de-DE",
        greek: "el-GR",
        hindi: "hi-IN",
        hungarian: "hu-HU",
        italian: "it-IT",
        japanese: "ja-JP",
        korean: "ko-KR",
        lithuanian: "lt-LT",
        norwegian: "no-NO",
        polish: "pl-PL",
        romanian: "ro-RO",
        russian: "ru-RU",
        thai: "th-TH",
        turkish: "tr-TR",
        ukrainian: "uk-UA",
        vietnamese: "vi-VN"
    }

    @property
    def language_code(self) -> str:
        """
        :class:`str`: The full BCP 47 tag with a region, ``de-DE`` for
        ``de``. Locales that already carry a region keep their value.
        Formatting libraries usually want this form.
        """
        value: str = self.value

        return self.__regions.get(value, value)

    @property
    def language(self) -> str:
        """
        :class:`str`: The language alone, ``en`` for both English locales
        and ``es`` for both Spanish ones. The key to use when a bot keeps
        one translation per language.
        """
        return self.value.partition("-")[0]

__all__ = ["Locale"]