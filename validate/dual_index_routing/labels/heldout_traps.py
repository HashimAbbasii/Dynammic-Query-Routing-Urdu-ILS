# -*- coding: utf-8 -*-
"""
Frozen held-out trap queries (H001-H040).

DO NOT add these to training. DO NOT call .fit() on them.

Protocol gold_label follows LABELING_GUIDE.txt (headline enough = SHORT,
need the article = LONG). It is a designer protocol label, not a second
independent human rater. Hashim should fill gold_label_student on
heldout_trap_sheet.csv without looking at this file or at SVM output.
"""

# trap_type, script, category, query, gold
HELDOUT_TRAPS = [
    # --- SHORT_WORDS_LONG_NEED (3-5 words, need the story) ---
    # Half use V3 intent cues; half do not (harder generalization).
    ("H001", "SHORT_WORDS_LONG_NEED", "urdu", "Business & Economics", "پیٹرول کیوں مہنگا", "LONG"),
    ("H002", "SHORT_WORDS_LONG_NEED", "urdu", "Sports", "شکست کی وجہ", "LONG"),
    ("H003", "SHORT_WORDS_LONG_NEED", "urdu", "Entertainment", "فلم کیسے ڈوبی", "LONG"),
    ("H004", "SHORT_WORDS_LONG_NEED", "urdu", "Science & Technology", "سیلاب کا نقصان", "LONG"),
    ("H005", "SHORT_WORDS_LONG_NEED", "urdu", "Sports", "ٹیم ہار کا تجزیہ", "LONG"),
    ("H006", "SHORT_WORDS_LONG_NEED", "urdu", "Business & Economics", "مہنگائی کے اثرات", "LONG"),
    ("H007", "SHORT_WORDS_LONG_NEED", "urdu", "Entertainment", "فلم فیل کی کہانی", "LONG"),
    ("H008", "SHORT_WORDS_LONG_NEED", "urdu", "Business & Economics", "روپے گراوٹ کے نتائج", "LONG"),
    ("H009", "SHORT_WORDS_LONG_NEED", "roman", "Business & Economics", "petrol kyun mehnga", "LONG"),
    ("H010", "SHORT_WORDS_LONG_NEED", "roman", "Sports", "shikast ki waja", "LONG"),
    ("H011", "SHORT_WORDS_LONG_NEED", "roman", "Entertainment", "film kaise doobi", "LONG"),
    ("H012", "SHORT_WORDS_LONG_NEED", "roman", "Science & Technology", "flood ka nuksan", "LONG"),
    ("H013", "SHORT_WORDS_LONG_NEED", "roman", "Sports", "team haar ka tajzia", "LONG"),
    ("H014", "SHORT_WORDS_LONG_NEED", "roman", "Business & Economics", "mehngai ke asar", "LONG"),
    ("H015", "SHORT_WORDS_LONG_NEED", "roman", "Entertainment", "film fail ki kahani", "LONG"),
    ("H016", "SHORT_WORDS_LONG_NEED", "roman", "Business & Economics", "rupay girawut ke nataij", "LONG"),
    # --- LONG_WORDS_SHORT_NEED (6-9 words, one fact) ---
    ("H017", "LONG_WORDS_SHORT_NEED", "urdu", "Science & Technology", "آج لاہور کا درجہ حرارت کیا ہے", "SHORT"),
    ("H018", "LONG_WORDS_SHORT_NEED", "urdu", "Business & Economics", "سونے کی فی تولہ قیمت آج کتنی ہے", "SHORT"),
    ("H019", "LONG_WORDS_SHORT_NEED", "urdu", "Sports", "ایشیا کپ فائنل کب کھیلا جائے گا", "SHORT"),
    ("H020", "LONG_WORDS_SHORT_NEED", "urdu", "Science & Technology", "نیا آئی فون پاکستان میں کب آیا", "SHORT"),
    ("H021", "LONG_WORDS_SHORT_NEED", "urdu", "Science & Technology", "آج کراچی میں زیادہ سے زیادہ حرارت", "SHORT"),
    ("H022", "LONG_WORDS_SHORT_NEED", "urdu", "Sports", "پاکستان کا اگلا کرکٹ میچ کس ملک سے", "SHORT"),
    ("H023", "LONG_WORDS_SHORT_NEED", "urdu", "Business & Economics", "پیٹرول کی موجودہ قیمت فی لیٹر پاکستان", "SHORT"),
    ("H024", "LONG_WORDS_SHORT_NEED", "urdu", "Business & Economics", "آج سٹاک ایکسچینج کتنے پوائنٹ پر", "SHORT"),
    ("H025", "LONG_WORDS_SHORT_NEED", "roman", "Science & Technology", "aaj lahore ka temperature kya hai", "SHORT"),
    ("H026", "LONG_WORDS_SHORT_NEED", "roman", "Business & Economics", "sone ki tola qeemat aaj kitni hai", "SHORT"),
    ("H027", "LONG_WORDS_SHORT_NEED", "roman", "Sports", "Asia cup final kab khela jayega", "SHORT"),
    ("H028", "LONG_WORDS_SHORT_NEED", "roman", "Science & Technology", "naya iphone pakistan mein kab aaya", "SHORT"),
    ("H029", "LONG_WORDS_SHORT_NEED", "roman", "Science & Technology", "aaj karachi max temperature kitna raha", "SHORT"),
    ("H030", "LONG_WORDS_SHORT_NEED", "roman", "Sports", "pakistan agla cricket match kis mulk se", "SHORT"),
    ("H031", "LONG_WORDS_SHORT_NEED", "roman", "Business & Economics", "petrol ki mojooda qeemat per litre pakistan", "SHORT"),
    ("H032", "LONG_WORDS_SHORT_NEED", "roman", "Business & Economics", "aaj stock exchange kitne points par", "SHORT"),
    # --- controls (length and need agree) ---
    ("H033", "CONTROL_EASY_SHORT", "urdu", "Business & Economics", "ڈیزل ریٹ", "SHORT"),
    ("H034", "CONTROL_EASY_SHORT", "urdu", "Business & Economics", "سونا ریٹ", "SHORT"),
    ("H035", "CONTROL_EASY_SHORT", "roman", "Sports", "football score", "SHORT"),
    ("H036", "CONTROL_EASY_SHORT", "roman", "Business & Economics", "diesel rate", "SHORT"),
    (
        "H037",
        "CONTROL_EASY_LONG",
        "urdu",
        "Business & Economics",
        "ملک میں پٹرول ڈیزل اور بجلی کے نرخ بڑھنے سے ٹرانسپورٹ اور گھریلو بجٹ پر پڑنے والے بوجھ کا تفصیلی جائزہ",
        "LONG",
    ),
    (
        "H038",
        "CONTROL_EASY_LONG",
        "urdu",
        "Sports",
        "قومی کرکٹ ٹیم کی حالیہ شکست کے بعد سلیکٹرز کی حکمت عملی اور کھلاڑیوں کی فارم پر ایک گہری نظر",
        "LONG",
    ),
    (
        "H039",
        "CONTROL_EASY_LONG",
        "roman",
        "Business & Economics",
        "petrol diesel aur bijli ke rates barhne se transport aur gharailu budget par parne wale bojh ka tafseeli jaiza",
        "LONG",
    ),
    (
        "H040",
        "CONTROL_EASY_LONG",
        "roman",
        "Sports",
        "qaumi cricket team ki haaliya shikast ke baad selectors ki hikmat e amli aur players ki form par ek gehri nazar",
        "LONG",
    ),
]
