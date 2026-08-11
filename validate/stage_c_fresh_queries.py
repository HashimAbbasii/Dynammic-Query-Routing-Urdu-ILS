# -*- coding: utf-8 -*-
# Stage C: Fresh, completely independent test set (never used in training,
# never used in the 50-query external set, never used in the 16-query
# holdout). Deliberately stratified across word-count buckets (with extra
# density in 5-9, the known weak zone) and both scripts. Topics chosen to
# be different from training/prior-test topics: transport, agriculture,
# environment, crime/security, science, tourism, food, real estate,
# banking, telecom, startups, football/badminton/tennis, local city news
# (Multan/Peshawar/Faisalabad), arts/culture, Ramadan/Eid, admissions.

fresh_stage_c = [
    # ---- short 2-4 words (both scripts) ----
    ("ٹریفک جام", "short"), ("زرعی قرض", "short"), ("سمندری آلودگی", "short"), ("چوری واردات", "short"),
    ("خلائی مشن", "short"), ("سیاحتی مقام", "short"), ("بینک قرض", "short"), ("ٹینس ٹورنامنٹ", "short"),
    ("traffic jam", "short"), ("agriculture loan", "short"), ("deforestation crisis", "short"), ("theft incident", "short"),
    ("space mission", "short"), ("tourist spot", "short"), ("bank loan", "short"), ("football match", "short"),

    # ---- exactly 5 words (both scripts) ----
    ("ملتان میں ٹریفک حادثہ ہوا", "long"), ("کسانوں کو نیا قرض ملے گا", "long"),
    ("پشاور میں چوری کی واردات", "long"), ("نیا اسٹارٹ اپ فنڈنگ حاصل کرے", "long"),
    ("فیصل آباد میں پانی صاف نہیں", "long"),
    ("multan mein traffic accident hua", "long"), ("kisano ko naya loan milega", "long"),
    ("peshawar mein chori ki waardaat", "long"), ("naya startup funding hasil karega", "long"),
    ("faisalabad mein pani saaf nahi", "long"),

    # ---- exactly 6 words (both scripts) ----
    ("رمضان میں اشیائے خوردونوش کی قیمتیں بڑھیں", "long"), ("نئے بینک اکاؤنٹ کھولنے کا طریقہ", "long"),
    ("عید سے پہلے بازاروں میں رش", "long"), ("خلائی سائنسدانوں نے نیا سیارہ دریافت کیا", "long"),
    ("فٹبال ٹیم نے فائنل میچ جیت لیا", "long"),
    ("ramzan mein cheezon ki qeemat barh gayi", "long"), ("naya bank account kholne ka tareeqa", "long"),
    ("eid se pehle bazaron mein rush hai", "long"), ("scientists ne naya sitara dhoond liya", "long"),
    ("football team ne final match jeet liya", "long"),

    # ---- exactly 7 words (both scripts) ----
    ("محکمہ ماحولیات نے جنگلات کی کٹائی روکنے کا فیصلہ کیا", "long"), ("سیاحوں کی تعداد میں حالیہ مہینوں کے دوران اضافہ ہوا", "long"),
    ("نئی ریلوے لائن کی تعمیر کا کام شروع ہو گیا", "long"), ("پولیس نے چوری کے واقعات میں ملوث گروہ پکڑ لیا", "long"),
    ("badminton championship mein pakistani player ne medal jeeta hai", "long"),
    ("mahikma-e-maholiyat ne jangalat ki katai rokne ka faisla kiya", "long"), ("sayahon ki tadad mein haleeya mahino ke dauran izafa hua", "long"),
    ("nai railway line ki tameer ka kaam shuru ho gaya", "long"), ("police ne chori ke waqiat mein mulawas giroh pakar liya", "long"),
    ("real estate prices mein is saal kaafi izafa dekha gaya", "long"),

    # ---- exactly 8 words (both scripts) ----
    ("نئے تعلیمی سال میں داخلوں کی تاریخ کا اعلان ہو گیا", "long"), ("ٹیلی کام کمپنیوں نے موبائل پیکجز کی قیمتیں کم کر دیں", "long"),
    ("مقامی فنکاروں نے شہر میں نئی نمائش کا اہتمام کیا", "long"), ("زرعی ماہرین نے کسانوں کو نئی فصل کی تربیت دی", "long"),
    ("naye education year mein admission ki date announce ho gayi", "long"), ("telecom companies ne mobile packages ki qeemat kam kar di", "long"),
    ("local artists ne shehar mein nai exhibition ka intizam kiya", "long"), ("agriculture experts ne kisano ko nai crop training di", "long"),
    ("cricket ke ilawa tennis mein bhi pakistan ne acha perform kiya", "long"), ("bank ne customers ke liye naya digital saving account launch kiya", "long"),

    # ---- exactly 9 words (both scripts) ----
    ("وفاقی حکومت نے چھوٹے کاروباروں کے لیے نئی سبسڈی اسکیم شروع کی", "long"), ("محکمہ جنگلات نے شہر کے مضافات میں نئے درخت لگانے کا آغاز کیا", "long"),
    ("نجی ہسپتالوں میں علاج کی قیمتوں پر حکومت نے کنٹرول لگا دیا", "long"),
    ("wafaqi hakumat ne chote karobaron ke liye nai subsidy scheme shuru ki", "long"), ("mahikma-e-jangalat ne shehar ke muzafat mein naye darakht lagane ka aghaz kiya", "long"),
    ("private hospitals mein ilaj ki qeemat par hakumat ne control laga diya", "long"), ("real estate sector mein invest karne wale logon ki tadad barh gayi hai", "long"),
    ("nai startup companies ko government se tax mein chhoot milne wali hai", "long"), ("tourism ministry ne northern areas mein naye resorts banane ka elan kiya", "long"),

    # ---- 10-14 words (both scripts, natural sentences) ----
    ("قومی اسمبلی میں آج زرعی اصلاحات کے بل پر بحث ہونے والی ہے", "long"),
    ("شہر کی سڑکوں پر ٹریفک کا نظام بہتر بنانے کے لیے نیا منصوبہ شروع کیا گیا ہے", "long"),
    ("national assembly mein aaj agriculture reforms ke bill par behas hone wali hai", "long"),
    ("shehar ki sarkon par traffic ka nizam behtar banane ke liye naya mansooba shuru kiya gaya hai", "long"),
    ("مقامی حکومت نے شہریوں کی سہولت کے لیے نیا صحت مرکز تعمیر کرنے کا فیصلہ کیا ہے", "long"),
    ("local government ne shehriyon ki sahulat ke liye naya health center tameer karne ka faisla kiya hai", "long"),
    ("خلائی تحقیقاتی ادارے نے نئے سیٹلائٹ کی کامیاب لانچنگ کا اعلان کیا ہے", "long"),
    ("space research organization ne naye satellite ki kamyab launching ka elan kiya hai", "long"),

    # ---- 15+ words ----
    ("محکمہ تعلیم نے سرکاری اسکولوں میں طلبہ کی حاضری بہتر بنانے کے لیے نیا نظام متعارف کرایا ہے جس کے تحت والدین کو روزانہ اطلاع ملے گی", "long"),
    ("education department ne sarkari schools mein talba ki hazri behtar banane ke liye naya nizam mutaraf karaya hai jiske tehat walidain ko rozana ittila milegi", "long"),

    # ---- deliberately UNSEEN-VOCABULARY probes (words checked NOT in the 1169-word training vocab) ----
    ("زلزلہ پیما آلات نے شدید جھٹکے ریکارڈ کیے", "long"),
    ("seismograph instruments ne shadeed jhatke record kiye", "long"),
    ("ماہرینِ فلکیات نے دومکیت کی نئی تصاویر جاری کیں", "long"),
    ("astronomers ne comet ki nai tasveeren jari ki hain", "long"),
    ("گلیشیئر پگھلنے کی رفتار میں تشویشناک اضافہ دیکھا گیا", "long"),
    ("glacier pighalne ki raftar mein tashweeshnak izafa dekha gaya", "long"),

    # ---- explicit mixed-script probes (KNOWN weak spot — zero training coverage, included to characterize not to hide) ----
    ("پاکستان کی economy is saal behtar ho rahi hai", "long"),
    ("cricket ٹیم نے آج زبردست performance دیا", "long"),
    ("نیا mobile فون بازار میں آ گیا", "long"),
    ("weather آج بہت اچھا ہے islamabad mein", "long"),
]

print(f"Total fresh Stage-C queries: {len(fresh_stage_c)}")
