# -*- coding: utf-8 -*-
"""Unit tests for Module 1 generic Roman Urdu normalization.

Synthetic examples only. No U001–U040, no K001–K040, no Phase 12 strings.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.roman_urdu_normalization import (  # noqa: E402
    NormalizationConfig,
    explain_roman_urdu_normalization,
    normalize_roman_urdu,
)


class TestBasicNormalization(unittest.TestCase):
    def test_lowercase(self) -> None:
        self.assertEqual(normalize_roman_urdu("MERA Dost"), "mera dost")

    def test_extra_spaces(self) -> None:
        self.assertEqual(normalize_roman_urdu("mera    dost"), "mera dost")

    def test_leading_trailing_space(self) -> None:
        self.assertEqual(normalize_roman_urdu("  mera dost  "), "mera dost")

    def test_punctuation_to_space(self) -> None:
        self.assertEqual(normalize_roman_urdu("mera,dost!"), "mera dost")

    def test_empty_string(self) -> None:
        self.assertEqual(normalize_roman_urdu(""), "")

    def test_none_follows_repo_convention(self) -> None:
        self.assertEqual(normalize_roman_urdu(None), "")


class TestRepetition(unittest.TestCase):
    def setUp(self) -> None:
        self.on = NormalizationConfig(repeated_character_normalization=True)
        self.off = NormalizationConfig(repeated_character_normalization=False)

    def test_elongated_letters_collapse_to_two(self) -> None:
        # 3+ identical ASCII letters → 2. "boooht" is synthetic, not a Phase 12 query.
        self.assertEqual(normalize_roman_urdu("boooht", self.on), "booht")

    def test_normal_double_letters_not_damaged(self) -> None:
        self.assertEqual(normalize_roman_urdu("good book", self.on), "good book")

    def test_see_unchanged(self) -> None:
        self.assertEqual(normalize_roman_urdu("see", self.on), "see")

    def test_off_by_default(self) -> None:
        self.assertEqual(normalize_roman_urdu("soooo", self.off), "soooo")
        self.assertEqual(normalize_roman_urdu("boooht"), "boooht")

    def test_digits_not_collapsed(self) -> None:
        self.assertEqual(normalize_roman_urdu("111860", self.on), "111860")


class TestMixedContent(unittest.TestCase):
    def test_roman_and_english(self) -> None:
        self.assertEqual(normalize_roman_urdu("mera cricket match"), "mera cricket match")

    def test_roman_and_numbers(self) -> None:
        self.assertEqual(normalize_roman_urdu("match 2024"), "match 2024")

    def test_name_only_lowercased(self) -> None:
        self.assertEqual(normalize_roman_urdu("Nadia Khan"), "nadia khan")

    def test_urdu_letters_preserved(self) -> None:
        self.assertEqual(normalize_roman_urdu("میرا dost"), "میرا dost")

    def test_hyphenated_identifier(self) -> None:
        self.assertEqual(normalize_roman_urdu("COVID-19"), "covid-19")

    def test_abbreviation_lowercased_not_split(self) -> None:
        self.assertEqual(normalize_roman_urdu("CPEC"), "cpec")


class TestSafety(unittest.TestCase):
    def test_url_not_corrupted(self) -> None:
        url = "https://example.com/Path?x=1"
        out = normalize_roman_urdu("see " + url)
        self.assertIn("https://example.com/Path?x=1", out)
        self.assertTrue(out.startswith("see "))

    def test_email_not_corrupted(self) -> None:
        mail = "user@example.com"
        out = normalize_roman_urdu("contact " + mail)
        self.assertIn(mail, out)

    def test_multiple_urls_restored(self) -> None:
        a = "https://example.com/A"
        b = "https://example.org/B"
        out = normalize_roman_urdu("see " + a + " and " + b)
        self.assertIn(a, out)
        self.assertIn(b, out)

    def test_www_url_not_corrupted(self) -> None:
        url = "www.example.org/News"
        out = normalize_roman_urdu("open " + url)
        self.assertIn(url, out)

    def test_apostrophe_kept(self) -> None:
        self.assertEqual(normalize_roman_urdu("don't go"), "don't go")

    def test_zwnj_treated_as_space(self) -> None:
        self.assertEqual(normalize_roman_urdu("mera\u200c dost"), "mera dost")

    def test_numeric_string(self) -> None:
        self.assertEqual(normalize_roman_urdu("111860"), "111860")

    def test_english_tokens_not_mapped(self) -> None:
        # No dictionary and no vowel stripping: English stays English (aside from case/ws).
        self.assertEqual(normalize_roman_urdu("The Court"), "the court")


class TestIdempotence(unittest.TestCase):
    def test_default_idempotent(self) -> None:
        samples = [
            "MERA   dost!!",
            "good book",
            "match 2024",
            "https://example.com/X",
            "",
        ]
        for s in samples:
            once = normalize_roman_urdu(s)
            twice = normalize_roman_urdu(once)
            self.assertEqual(once, twice, msg=repr(s))

    def test_repeat_layer_idempotent(self) -> None:
        cfg = NormalizationConfig(repeated_character_normalization=True)
        s = "soooo boooht good"
        once = normalize_roman_urdu(s, cfg)
        twice = normalize_roman_urdu(once, cfg)
        self.assertEqual(once, twice)


class TestConfigAndTrace(unittest.TestCase):
    def test_can_disable_lowercase(self) -> None:
        cfg = NormalizationConfig(lowercase=False, punctuation_spacing=False)
        self.assertEqual(normalize_roman_urdu("Mera  Dost", cfg), "Mera Dost")

    def test_vowel_flag_is_noop(self) -> None:
        cfg = NormalizationConfig(vowel_normalization=True)
        text = "mera dost"
        result = explain_roman_urdu_normalization(text, cfg)
        self.assertEqual(result.normalized, "mera dost")
        self.assertIn("vowel_normalization_skipped_unimplemented", result.transformations)

    def test_explain_lists_whitespace(self) -> None:
        result = explain_roman_urdu_normalization("mera   dost")
        self.assertEqual(result.normalized, "mera dost")
        self.assertIn("whitespace", result.transformations)

    def test_deterministic(self) -> None:
        a = normalize_roman_urdu("MERA, dost")
        b = normalize_roman_urdu("MERA, dost")
        self.assertEqual(a, b)


class TestDoesNotUseDictionary(unittest.TestCase):
    def test_unknown_token_unchanged_except_case(self) -> None:
        # A made-up token must not be rewritten via roman_urdu_dict_expanded.json.
        self.assertEqual(normalize_roman_urdu("zqxtpl"), "zqxtpl")


if __name__ == "__main__":
    unittest.main()
