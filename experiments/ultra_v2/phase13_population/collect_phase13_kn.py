# -*- coding: utf-8 -*-
"""Phase 13 Step 2 — Roman KN collection (no retrieval).

LLM-drafted candidates against pre-sampled source_doc_id values.
Validates PROTOCOL.md §5 overlap + M0 detect_script. Does not score retrieval.
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments" / "ultra_v2" / "scripts"))
import validate_benchmark as vb  # noqa: E402

ART = Path(__file__).resolve().parent / "artifacts"
SAMPLE_PATH = ART / "sampled_sources_round1.json"
OUT_CSV = ART / "phase13_kn_drafts.csv"
REJECT_LOG = ART / "phase13_rejection_log.csv"
REVIEW_MD = ART / "HASHIM_NATURALNESS_REVIEW.md"
METHOD_NOTE = ART / "METHOD_NOTE.md"
VAL_ROOT = Path(__file__).resolve().parent / "validation_bench"

# Pre-sampled source_doc_id is fixed. Drafts written after reading article text only.
# Format: (source_doc_id, query_text, intent_type, notes)
# Extra candidates beyond ~29 allow reject/redraft margin without new sampling.
DRAFTS: list[tuple[int, str, str, str]] = [
    (38098, "world t20 group b mein zimbabwe aur afghanistan ne dusri jeet kis venue par hasil ki", "event", "WT20 Nagpur stage"),
    (16031, "ankhon ki sehat ke liye age ke sath kaunse foods helpful bataye gaye hain", "topical", "eye nutrition tips"),
    (71914, "imf pakistan representative ne exchange rate flexibility kyun zaroori qaraar di", "explanatory", "SBP vs finance IMF"),
    (22449, "whatsapp par youtube video bina app switch kiye kaise chalegi", "factoid", "in-chat YouTube play"),
    (90343, "sri lanka ne india ke khilaf test series ke liye kitne players naamzad kiye", "factoid", "16-man squad"),
    (17825, "is sadi ki behtareen science fiction films ki list kis audience ke liye banayi gayi", "topical", "SF film listicle"),
    (1296, "chhote dukandaron ke liye sarkari fixed tax scheme kab announce hui", "event", "FBR small trader"),
    (24064, "ufone newspaper ad campaign mein kis Pakistani actor ko phone ke sath dikhaya gaya", "entity_person", "Faisal Qureshi ad"),
    (88253, "sharapova ki olympics appeal ka faisla kis date tak lataya gaya", "event", "CAS doping appeal"),
    (11931, "hania aamir ki doosri film mein leading pair kaun hai", "entity_person", "film cast"),
    (73679, "saudi arab mein doodh chini jaisi items ki qeemat mein kitni percent kami hui", "factoid", "Saudi price cut"),
    (23448, "ek hafte facebook band rakhne se mood aur sleep par kya asar bataya gaya", "explanatory", "social media detox"),
    (45096, "kolkata knight riders ne peshawar zalmi exhibition match ki khabar kyun jhutlai", "event", "KKR denial"),
    (105214, "priyanka chopra ki sports film mary kom ke gaane adhoore ki video kab release hui", "event", "song video"),
    (72411, "petrol aur diesel ki qeemat mein ek rupay ka izafa kis wazir ne announce kiya", "factoid", "Ishaq Dar fuel"),
    (21365, "australia ne great barrier reef bachane ke liye kaunsa starfish killing robot launch kiya", "factoid", "COTSbot"),
    (51809, "psl eliminator mein lahore qalandars ne peshawar zalmi ko kaise haraaya", "event", "PSL5 eliminator"),
    (48848, "sri lanka mein haathi ne bus rok kar khane ka demand kaise kiya", "topical", "elephant viral"),
    (62668, "state bank ne agle do mahine ki monetary policy mein policy rate kitna kam kiya", "factoid", "rate cut"),
    (20610, "pakistan ne facebook se user data maangne ki requests mein kitna izafa dekha", "factoid", "transparency report"),
    (80742, "england ke khilaf teesre test mein pakistan pehli innings mein follow-on kyun khela", "event", "England Test"),
    (51022, "meera ne apne husband hone ke dawaydar atiq ur rehman par kya ilzam lagaya", "entity_person", "publicity claim"),
    (2296, "samsung ne pakistan mein smart phone qeematon mein kami kab announce ki", "event", "local price cut"),
    (19493, "microsoft ne internet explorer support kab permanently band ki", "factoid", "IE retirement"),
    (35735, "najam sethi ne rashid latif ki selection role appointment par ecb ka pressure kyun man liya", "entity_person", "PCB politics"),
    (6103, "nobel laureate women ne gates foundation ko modi award par kya letter likha", "event", "award protest"),
    (64127, "sbp spokesman ne naye currency notes wali social media afwahen kyun kharij keen", "event", "note rumour"),
    (21680, "facebook rumour wale posts ko asal news samajhne se pehle kya check karna chahiye", "explanatory", "rumour literacy"),
    (26893, "sarfaraz ahmed ne shoib akhtar ki tanqeed ko personal attack kyun qaraar diya", "entity_person", "captain response"),
    (108020, "sridevi ki angrezi wala film ke naye songs norah majhi aur main hatun kab release hue", "event", "English Vinglish songs"),
    (72855, "panama case ki sunwai se pehle stock market investors kyun ehtiyat kar rahe the", "explanatory", "PSX caution"),
    (19235, "scientists ne snake venom pehli baar lab mein kaise produce kiya", "factoid", "lab venom"),
    (46170, "west indies ki doosri wt20 trophy ke baad stadium kis captain ke naam par rakha gaya", "event", "Darren Sammy stadium"),
    (4961, "kangana ranaut ki behen ka twitter account muslim-hostile tweet ke baad kyun suspend hua", "event", "Rangoli tweet"),
    (109641, "pm ne real estate mein chhupi daulat ke survey aur tax assessment ki approval kab di", "event", "real estate drive"),
    (24376, "russian scientists ne flu medicine carrot aur matar se kaise banayi", "factoid", "plant pharma"),
    (54835, "pakistan series se pehle australia bowling line mein kaunse star injury ki wajah se nahi khelenge", "factoid", "Cummins Hazlewood"),
    (105983, "bollywood film gunday ke title song ki video kab release hui", "event", "Gunday title"),
    (109728, "is financial year ki pehli quarter mein foreign direct investment kitni percent giri", "factoid", "FDI drop"),
    (60330, "snapchat ne 3d lenses filter feature kab introduce kiya", "factoid", "World Lenses"),
]

WRITER = "LLM1"
TS = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
TARGET_KEEP = 29


def length_bin(text: str) -> str:
    return vb.length_bin_of(text)


def load_existing_texts() -> set[str]:
    texts: set[str] = set()
    build = (ROOT / "experiments/ultra_v2/scripts/build_collected_benchmark.py").read_text(
        encoding="utf-8"
    )
    for m in re.finditer(r'"([^"\\]*(?:\\.[^"\\]*)*)"', build):
        t = m.group(1)
        if len(t) >= 15 and re.search(r"[A-Za-z\u0600-\u06FF]", t):
            texts.add(vb.norm_text(t))
    for split in ("train", "dev"):
        for name in ("queries_kn.csv", "queries_nl.csv"):
            path = ROOT / "experiments/ultra_v2/benchmark" / split / name
            with path.open(encoding="utf-8-sig", newline="") as f:
                for r in csv.DictReader(f):
                    texts.add(vb.norm_text(r["query_text"]))
    return texts


def load_headlines_for(ids: set[int]) -> dict[int, str]:
    out: dict[int, str] = {}
    with open(ROOT / "data/clean_articles.csv", encoding="utf-8-sig", newline="") as f:
        for i, row in enumerate(csv.DictReader(f)):
            raw = (row.get("Index") or "").strip()
            try:
                idx = int(float(raw)) if raw else i
            except ValueError:
                idx = i
            if idx in ids:
                out[idx] = row.get("Headline") or ""
            if len(out) == len(ids):
                break
    return out


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    sample = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    sampled_ids = [s["source_doc_id"] for s in sample["sources"]]
    assert all(d[0] in sampled_ids for d in DRAFTS), "draft source not in pre-sample"

    existing_texts = load_existing_texts()
    hist = vb.historical_query_texts()
    headlines = load_headlines_for({d[0] for d in DRAFTS})

    rejects: list[dict] = []
    accepted: list[dict] = []
    next_id = 91  # KN001–KN090 already used in v0 (incl. sealed split via build list)

    for sid, qtext, intent, notes in DRAFTS:
        if len(accepted) >= TARGET_KEEP:
            break
        qtext = qtext.strip()
        reason = None
        ov = vb.headline_overlap(qtext, headlines.get(sid, ""))
        det = vb.detect_script(qtext)
        nt = vb.norm_text(qtext)
        if not vb.m0_tokens(qtext):
            reason = "empty_tokens"
        elif ov >= 0.50:
            reason = "headline_overlap>=0.50"
        elif det != "ROMAN":
            reason = "detect_script=%s" % det
        elif nt in existing_texts:
            reason = "duplicate_v2_or_build_text"
        elif nt in hist or qtext in hist:
            reason = "historical_qtrn_k_u_h_copy"
        elif intent not in vb.INTENTS:
            reason = "bad_intent"
        if reason:
            rejects.append(
                {
                    "source_doc_id": sid,
                    "query_text": qtext,
                    "intent_type": intent,
                    "headline_overlap": "%.6f" % ov,
                    "detect_script": det,
                    "reason": reason,
                }
            )
            continue
        split = "train" if len(accepted) < 19 else "dev"
        qid = "KN%03d" % next_id
        next_id += 1
        row = {
            "query_id": qid,
            "track": "KN",
            "script": "ROMAN",
            "intent_type": intent,
            "length_bin": length_bin(qtext),
            "ambiguous": "0",
            "query_text": qtext,
            "source_doc_id": str(sid),
            "source_article_hash_or_identifier": "index:%s" % sid,
            "headline_overlap": "%.6f" % ov,
            "writer_id": WRITER,
            "creation_timestamp": TS,
            "split": split,
            "status": "accepted",
            "notes": "phase13 LLM-drafted pending Hashim naturalness review; " + notes,
            "interpretation_notes": "",
        }
        accepted.append(row)
        existing_texts.add(nt)

    fields = list(vb.KN_REQUIRED)
    with OUT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in accepted:
            w.writerow(r)

    with REJECT_LOG.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "source_doc_id",
                "query_text",
                "intent_type",
                "headline_overlap",
                "detect_script",
                "reason",
            ],
        )
        w.writeheader()
        for r in rejects:
            w.writerow(r)

    METHOD_NOTE.write_text(
        "\n".join(
            [
                "# Phase 13 method note (mandatory disclosure)",
                "",
                "These Phase 13 Roman KN drafts are **LLM-drafted, human-reviewed**",
                "(naturalness review by Hashim). They are **not** part of the original",
                "human-written n=51 Roman KN TRAIN+DEV set (writer_id W1, 2026-09-09).",
                "",
                "Do not blur this authorship distinction in reports or papers.",
                "",
                "Collection followed PROTOCOL.md §5: source_doc_id sampled before drafting,",
                "ExactSource gold fixed at creation, headline_overlap < 0.50, detect_script=ROMAN,",
                "no retrieval/ranking consulted during drafting.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    lines = [
        "# Hashim naturalness-only review — Phase 13 Roman KN drafts",
        "",
        "**Review task:** Do these read like something a real bilingual Pakistani news user",
        "might type? Flag awkward, title-paste, or attack-string wording.",
        "",
        "**Do not** score retrieval quality. **Do not** ask whether BM25/Dense would find the gold.",
        "",
        "Authorship: LLM-drafted (`writer_id=LLM1`); distinct from original human-written KN001–KN054 Roman set.",
        "",
        "| ID | intent_type | source_doc_id | split | query_text |",
        "|---|---|---|---|---|",
    ]
    for r in accepted:
        lines.append(
            "| %s | %s | %s | %s | %s |"
            % (r["query_id"], r["intent_type"], r["source_doc_id"], r["split"], r["query_text"])
        )
    lines.extend(
        [
            "",
            "## Rejection log summary",
            "",
            "n_rejected = %d (see `phase13_rejection_log.csv`)" % len(rejects),
            "",
        ]
    )
    if rejects:
        lines.append("| source_doc_id | reason | overlap | script | draft |")
        lines.append("|---|---|---|---|---|")
        for r in rejects:
            lines.append(
                "| %s | %s | %s | %s | %s |"
                % (r["source_doc_id"], r["reason"], r["headline_overlap"], r["detect_script"], r["query_text"][:80])
            )
    REVIEW_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Validation bench: existing TRAIN+DEV KN/NL + new drafts; no TEST folder.
    for split in ("train", "dev"):
        d = VAL_ROOT / split
        d.mkdir(parents=True, exist_ok=True)
        for name in ("queries_kn.csv", "queries_nl.csv"):
            src = ROOT / "experiments/ultra_v2/benchmark" / split / name
            dst = d / name
            rows = []
            with src.open(encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                fields0 = reader.fieldnames or fields
                rows = list(reader)
            if name == "queries_kn.csv":
                extra = [r for r in accepted if r["split"] == split]
                rows.extend(extra)
            with dst.open("w", encoding="utf-8-sig", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fields0, extrasaction="ignore")
                w.writeheader()
                for r in rows:
                    w.writerow(r)

    print("accepted", len(accepted))
    print("rejected", len(rejects))
    print("out_csv", OUT_CSV)
    print("review", REVIEW_MD)
    print("validation_bench", VAL_ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
