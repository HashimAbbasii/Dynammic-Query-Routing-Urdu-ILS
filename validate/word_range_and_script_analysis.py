import sys, pickle
sys.path.insert(0, '..')
import numpy as np
from validation_response import extract_features, load_roman_dict

roman_dict = load_roman_dict()
old_model = pickle.load(open('../models/svm_classifier_PRE_GAPFIX_backup.pkl','rb'))
old_scaler = pickle.load(open('../models/scaler_PRE_GAPFIX_backup.pkl','rb'))
new_model = pickle.load(open('../models/svm_classifier.pkl','rb'))
new_scaler = pickle.load(open('../models/scaler.pkl','rb'))

external_queries = [
    ("پاکستان نے بھارت کو ورلڈ کپ فائنل میں شکست دی", "long"), ("کرکٹ", "short"),
    ("بابر اعظم نے سنچری اسکور کی", "long"), ("میچ", "short"),
    ("قومی ٹیم کے کھلاڑیوں کی فٹنس رپورٹ جاری", "long"),
    ("pakistan cricket world cup final match result", "long"), ("score", "short"),
    ("babar azam ne century kaise score ki aaj ke match mein", "long"), ("wicket", "short"),
    ("pakistan team ne india ko kis tarah se harayaa", "long"), ("وزیراعظم", "short"),
    ("حکومت نے نئے بجٹ کا اعلان کر دیا", "long"), ("الیکشن", "short"),
    ("قومی اسمبلی میں اپوزیشن نے تحریک عدم اعتماد پیش کی", "long"), ("سیاست", "short"),
    ("PM ne naya budget announce kiya aaj assembly mein", "long"), ("election", "short"),
    ("opposition ne government ke khilaf motion submit kiya", "long"), ("wazir", "short"),
    ("pakistan mein siyasi buhran ke baad nai hakumat bani", "long"), ("ڈالر", "short"),
    ("عالمی بینک نے پاکستان کو قرض دینے سے انکار کر دیا", "long"), ("مہنگائی", "short"),
    ("اسٹیٹ بینک نے شرح سود میں اضافہ کر دیا", "long"), ("بجٹ", "short"),
    ("dollar rate aaj kitna hai", "long"), ("mehngai", "short"),
    ("imf ne pakistan ko loan dene ki sharait rakhi hain", "long"), ("market", "short"),
    ("pakistan ki economy mein behteri aa rahi hai ya nahi", "long"), ("ہسپتال", "short"),
    ("کورونا وائرس کی نئی لہر نے پاکستان میں دستک دے دی", "long"), ("دوائی", "short"),
    ("وزارت صحت نے ویکسین مہم شروع کرنے کا فیصلہ کیا", "long"), ("علاج", "short"),
    ("hospital", "short"), ("corona ki nayi lehar pakistan mein phail rahi hai", "long"),
    ("dawai", "short"), ("sehat ka khayal kaise rakha jaye garmiyon mein", "long"),
    ("vaccine", "short"), ("موبائل", "short"),
    ("مصنوعی ذہانت نے طب کے شعبے میں انقلاب برپا کر دیا", "long"), ("انٹرنیٹ", "short"),
    ("پاکستان میں فائیو جی سروس کب شروع ہوگی", "long"), ("ٹیکنالوجی", "short"),
    ("mobile", "short"), ("AI ne medical field mein kitni taraqqi ki hai abhi tak", "long"),
    ("internet", "short"), ("pakistan mein 5G service kab tak launch hogi officially", "long"),
    ("tech", "short"),
]

fresh_holdout = [
    ("موسم رپورٹ", "short"), ("فلم ریلیز", "short"), ("عمرہ ویزا", "short"),
    ("weather report", "short"), ("movie release", "short"), ("umrah visa", "short"),
    ("اسلام آباد میں آج بارش کا امکان ہے", "long"), ("نئی فلم نے باکس آفس پر ریکارڈ بنایا", "long"),
    ("حج کے لیے درخواستیں کب شروع ہوں گی", "long"), ("قومی ہاکی ٹیم نے فائنل جیت لیا", "long"),
    ("kal barish hone ka imkan hai islamabad mein", "long"), ("nai film ne box office pe record banaya", "long"),
    ("hajj ke liye application kab shuru hogi", "long"), ("hockey team ne final match jeet liya", "long"),
    ("موسمیاتی تبدیلی کی وجہ سے شمالی علاقہ جات میں برف باری کا نظام متاثر ہو رہا ہے", "long"),
    ("entertainment industry mein naye directors ko kaam karne ke mauqe kam milte hain kyunki competition bohat zyada hai", "long"),
]

all_test = external_queries + fresh_holdout
print(f"Total combined frozen test set: {len(all_test)} queries")

def is_roman(q):
    return not any('\u0600'<=c<='\u06FF' for c in q)

def predict(model, scaler, q):
    x = np.array([extract_features(q, roman_dict)])
    xt = scaler.transform(x)
    return model.predict(xt)[0]

rows = []
for q, true in all_test:
    wc = len(q.split())
    script = 'roman' if is_roman(q) else 'urdu'
    old_pred = predict(old_model, old_scaler, q)
    new_pred = predict(new_model, new_scaler, q)
    rows.append(dict(q=q, true=true, wc=wc, script=script, old=old_pred, new=new_pred))

print("\n=== POINT 3: Word-range stratified accuracy ===")
buckets = [(2,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,14),(15,999)]
print(f"{'Range':<8}{'n':<5}{'Old Acc':<10}{'New Acc':<10}")
for lo,hi in buckets:
    sub = [r for r in rows if lo<=r['wc']<=hi]
    if not sub: 
        print(f"{lo}-{hi if hi<999 else '+':<5}{0:<5}{'n/a':<10}{'n/a':<10}")
        continue
    old_acc = sum(1 for r in sub if r['old']==r['true'])/len(sub)
    new_acc = sum(1 for r in sub if r['new']==r['true'])/len(sub)
    label = f"{lo}-{hi}" if hi<999 else f"{lo}+"
    oa = f"{old_acc:.2%}"
    na = f"{new_acc:.2%}"
    print(f"{label:<8}{len(sub):<5}{oa:<10}{na:<10}")

print("\n=== POINT 4: Script-stratified accuracy/precision/recall/F1 ===")
from collections import Counter
for script in ['urdu','roman']:
    sub = [r for r in rows if r['script']==script]
    for label, mkey in [('OLD','old'),('NEW','new')]:
        y_true = [r['true'] for r in sub]
        y_pred = [r[mkey] for r in sub]
        acc = sum(1 for t,p in zip(y_true,y_pred) if t==p)/len(y_true)
        tp = sum(1 for t,p in zip(y_true,y_pred) if t=='long' and p=='long')
        fp = sum(1 for t,p in zip(y_true,y_pred) if t=='short' and p=='long')
        fn = sum(1 for t,p in zip(y_true,y_pred) if t=='long' and p=='short')
        prec = tp/(tp+fp) if (tp+fp) else float('nan')
        rec = tp/(tp+fn) if (tp+fn) else float('nan')
        f1 = 2*prec*rec/(prec+rec) if (prec+rec) else float('nan')
        print(f"{script:<8}{label:<5} n={len(sub):<4} Acc={acc:.2%}  P(long)={prec:.2%}  R(long)={rec:.2%}  F1={f1:.2%}")
