# -*- coding: utf-8 -*-
"""Query-side Roman treatments derived from frozen M0 tables only.

Does not edit the dictionary file. Does not read TEST. Does not run retrieval.
"""
from __future__ import annotations

from collections import OrderedDict


def alias_tables(fwd: dict) -> tuple[dict[str, str], dict[str, list[str]]]:
    """Map every dictionary key to the reverse-canonical key (first JSON key per Urdu value)."""
    groups: OrderedDict[str, list[str]] = OrderedDict()
    for key, urdu in fwd.items():
        groups.setdefault(urdu, []).append(key)
    canonical: dict[str, str] = {}
    siblings: dict[str, list[str]] = {}
    for keys in groups.values():
        can = keys[0]
        siblings[can] = list(keys)
        for k in keys:
            canonical[k] = can
    return canonical, siblings


def fold_token(tok: str, canonical: dict[str, str], variant_to_dict: dict[str, str]) -> str:
    stepped = variant_to_dict.get(tok, tok)
    return canonical.get(stepped, stepped)


def treatment_b0(qtoks: list[str], **_kwargs) -> list[str]:
    return list(qtoks)


def treatment_r21(
    qtoks: list[str],
    canonical: dict[str, str],
    variant_to_dict: dict[str, str],
    **_kwargs,
) -> list[str]:
    """Known dict/Method-C aliases → reverse-canonical key. All other tokens preserved."""
    return [fold_token(t, canonical, variant_to_dict) for t in qtoks]


def treatment_r23(
    qtoks: list[str],
    canonical: dict[str, str],
    siblings: dict[str, list[str]],
    variant_to_dict: dict[str, str],
    **_kwargs,
) -> list[str]:
    """Bounded expansion: union of sibling dictionary keys for the same Urdu value.

    Tokens with no dictionary family are preserved once. Group size is the existing
    JSON family (typically 2–3 keys), not an open generator.
    """
    out: list[str] = []
    seen: set[str] = set()
    for tok in qtoks:
        folded = fold_token(tok, canonical, variant_to_dict)
        family = siblings.get(folded)
        if family is None:
            pieces = [folded]
        else:
            pieces = list(family)
        for p in pieces:
            if p not in seen:
                seen.add(p)
                out.append(p)
    return out
