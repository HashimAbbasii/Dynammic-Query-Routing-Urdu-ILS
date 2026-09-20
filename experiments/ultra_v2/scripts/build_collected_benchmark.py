# -*- coding: utf-8 -*-
"""Write ULTRA v2 Phase 1 KN/NL CSVs. No retrieval. No BM25."""
from __future__ import annotations

import csv
import os
import re
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_DIR, "..", "..", ".."))
BENCH = os.path.join(ROOT, "experiments", "ultra_v2", "benchmark")
CORPUS = os.path.join(ROOT, "data", "clean_articles.csv")
TOKEN_RE = re.compile(r"[\u0600-\u06FF]+|[A-Za-z0-9]+", re.UNICODE)
TS = "2026-09-09T12:00:00Z"
WRITER = "W1"

KN = [
    (92506, "malaysia air race world championship third round kab shuru hua", "event", "air-race article need"),
    (90691, "zim t20 mein hosts ko chase ke liye kitna target mila", "factoid", "second t20 target"),
    (17150, "تھیٹر کے عالمی دن پر ثقافت کے فروغ کیوں ضروری سمجھا جاتا ہے", "explanatory", "theatre day"),
    (14991, "desi ghee sehat ke liye faida mand hai ya nuqsan deh", "topical", "ghee debate"),
    (64084, "iran amreeka tension ke baad local equities opening par kyun rebound hua", "event", "market open"),
    (29860, "kolkata ne delhi ko ipl thriller mein kis margin se haraaya", "factoid", "IPL result"),
    (70358, "وفاقی ادارے ٹڈی دل کو کھاد میں کیسے تبدیل کرنے جا رہے ہیں", "event", "locust compost"),
    (47197, "teen tennis sensation ne kaunsa canadian hardcourt title jeeta", "entity_person", "Rogers Cup"),
    (21892, "برقی رو انسانی جسم کے لیے کیوں جان لیوا بن جاتی ہے", "explanatory", "electric current"),
    (1674, "benami accounts walo ke khilaf revenue board ne kya saza tajweez ki", "event", "FBR benami"),
    (60226, "france ki hydrogen solar wind powered boat ka naam kya hai", "factoid", "Energy Observer"),
    (13580, "comedy nights wali dadi wapas kyun nahi ban na chahte", "entity_person", "Ali Asghar"),
    (82652, "world cup mein pakistan india fixture ke tickets black mein kyun bik rahe", "event", "ticket scalping"),
    (79754, "mobile slow charge hone ki user side ghalti kya ho sakti hai", "explanatory", "charging delay"),
    (22450, "viral maths puzzle ne internet users ko kyun confuse kiya", "topical", "math riddle"),
    (100673, "priyanka ke african kids se hair compliment exchange kis tour par hua", "entity_person", "UNICEF visit"),
    (19341, "boom supersonic passenger prototype kab unveil hua", "factoid", "XB-1"),
    (17943, "aladdin kahani kisi haqeeqi shakhs par mabni hai ya sirf fable hai", "topical", "Aladdin historicity"),
    (5092, "jlo ne 50 saal ki umar mein fitness kaise maintain ki", "entity_person", "Lopez fitness"),
    (60895, "cpec joint cooperation committee ka session kis shehar mein chal raha tha", "location", "CPEC JCC"),
    (13065, "jungle book live action ne india box office par kya record banaya", "event", "Disney India"),
    (14664, "shahid mira sangeet se pehle shaadi ki tayyariyan kab khatam huin", "event", "pre-wedding"),
    (12128, "qawwal aziz mian ki barsi kis tarah yaad ki jati hai", "entity_person", "qawwali legacy"),
    (31154, "west indies ke khilaf dubai day night series pakistan ka kaunsa milestone test hai", "factoid", "400th Test"),
    (60831, "adb country director ne pm se mil kar investment ke bare mein kya kaha", "event", "ADB meeting"),
    (102664, "salman ki wrestler film ka pehla poster kis director ki movie ka hai", "entity_person", "Sultan poster"),
    (59279, "chameleon satellite minutes mein naya mission kyun assume kar sakte hain", "explanatory", "reconfigurable sats"),
    (76785, "state bank ke mutabiq external debt burden mein kitni percent kami hui", "factoid", "SBP debt"),
    (101347, "houston new year show mein kumar sanu kis community event ka hissa bane", "event", "diaspora concert"),
    (47083, "imran tahir odi bowling ranking mein number one kab bane", "entity_person", "ICC rankings"),
    (29423, "fifa ranking mein germany top par hai to pakistan ka number kya hai", "factoid", "FIFA table"),
    (41695, "umar akmal par fixing case mein kitne saal ki pabandi lagi", "factoid", "PCB ban"),
    (81673, "shane warne test cap auction se bushfire fund ko kitni raqam mili", "factoid", "memorabilia"),
    (13398, "sharmeen obaid oscar short documentary category mein dobara kab jeeti", "entity_person", "second Oscar"),
    (10546, "zaheer khan ne sagarika se shaadi ka elaan kab kiya", "entity_person", "cricketer marriage"),
    (76509, "aglay das mahine mein local oil gas output mein kya izafa verqai hai", "factoid", "hydrocarbon outlook"),
    (22739, "nayi photo app chehre tabdeel karne ke ilawa kya karti hai", "topical", "selfie app"),
    (40057, "peshawar used car mela mein logon ki dilchaspi kis cheez par thi", "location", "auto exhibition"),
    (23062, "nokia android handset china launch par ek minute mein kyun sold out hua", "event", "flash sale"),
    (24596, "samsung ne galaxy s7 active ko galti se kis app mein leak kiya", "factoid", "unreleased model"),
    (65903, "caretaker finance minister ne cpec projects mukammal karne ka kya wazheh kiya", "event", "Shamshad Akhtar"),
    (111652, "current account deficit ki raftaar slow kyun hui SBP ke mutabiq", "explanatory", "CAD slowdown"),
    (21399, "moto p30 front design kis apple flagship se milta julta hai", "topical", "phone clone"),
    (23544, "twitter ka naya feature facebook snapchat se muqabla kyun karta hai", "topical", "product launch"),
    (19783, "messenger rooms jaisa group video chat facebook ne kab add kiya", "factoid", "Messenger Rooms"),
    (109714, "ml1 railway upgrade ko deadline se pehle track par lanay ki tayyari kya hai", "event", "CPEC ML-1"),
    (61862, "fbr aur sindh revenue board ne sales tax input par kya deal ki", "event", "tax MoU"),
    (20073, "samsung s10 lite aur note 10 lite 2020 lineup kab launch honay walay thay", "factoid", "budget flagships"),
    (86593, "lahore psl final ke liye stadium ke gird kitne personnel deploy honge", "factoid", "security plan"),
    (34762, "afghanistan world cup jeetne ki peshgoi kis foundation par ki gai", "topical", "prediction piece"),
    (21160, "gmail ke naye interface ko purane layout jaisa kaise banaya ja sakta hai", "explanatory", "UI revert"),
    (59426, "samsung ne vegas ces par human-like robots kyun dikhaye", "event", "CES robots"),
    (22115, "huawei mate 10 lite pakistan mein pehli baar kitne cameras ke sath aaya", "factoid", "local launch"),
    (4400, "kangana ke bayan par momina iram ne kya jawab diya", "entity_person", "industry spat"),
    (93957, "shahid afridi ne zim series jeetne ko kyun khush aind qaraar diya", "entity_person", "series reaction"),
    (36103, "fifa ne brazil stadium accident ke bawajood world cup shift karne se kyun inkaar kiya", "event", "host decision"),
    (77904, "sandy storm ke baad wall street dobara kab khula", "event", "NYSE reopen"),
    (60372, "facebook ne fake news flag karne ka tool kab introduce kiya", "event", "misinfo tools"),
    (111408, "pak china free trade deal ki amendments par ittefaq kab hua", "event", "FTA revision"),
    (39535, "karachi retail tomato rate mandi se sasta hone ke bawajood itna mehnga kyun hai", "explanatory", "price gouging"),
    (22565, "samsung dual screen monitor kis user need ke liye banaya gaya", "topical", "display launch"),
    (58490, "pak england dubai second test pehle match draw ke baad kab shuru hona tha", "event", "Test schedule"),
    (60934, "sales tax refunds ki qist mein kitne filers ko raqam mili", "factoid", "FBR refunds"),
    (21003, "apple charging cables mein bari tabdeeli users ke liye kyun dhakka ho sakti hai", "explanatory", "port change"),
    (48528, "malaya university food festival mein kitne mulkon ke students shamil hue", "factoid", "campus festival"),
    (59040, "pcb chairman ne bangladesh series haarne ka afsos kis wajah se zahir kiya", "entity_person", "Shahryar Khan"),
    (69049, "mehdi hassan ki chauthi barsi par unke naghmon ko kyun yaad kiya jata hai", "entity_person", "ghazal legacy"),
    (1485, "psx ceo richard morin ne achanak isteefa kyun diya", "entity_person", "exchange leadership"),
    (50209, "saif kareena ke bete ka naam kya rakha gaya", "factoid", "Pataudi newborn"),
    (111773, "state bank ne payment operators ke directors ki chaan been kyun shuru ki", "event", "FATF fit-and-proper"),
    (7621, "parineeti ne shaadi ki afwahon par khamoshi kyun tori", "entity_person", "marriage rumours"),
    (74609, "azad kashmir assembly mein naya budget kis wazeer finance ne pesh karna tha", "event", "AJK budget"),
    (85952, "nasir jamshed ka kehna hai pcb un par dabaao kaise dal rahi hai", "entity_person", "player vs board"),
    (94470, "bayern ne german super cup mein stuttgart ko kis score se haraaya", "factoid", "treble add-on"),
    (66482, "ten minutes gone thriller mein bank heist ke baad memory loss ki kahani kya hai", "topical", "trailer synopsis"),
    (19418, "vivo y51 pakistan mein global launch se pehle kyun aaya", "event", "local-first phone"),
    (26632, "ronaldo ke hat trick celebration par uefa ne kaunsa rule tootte hone ka ilzam lagaya", "event", "UEFA charge"),
    (55400, "new zealand ne world cup mein england ko kitni wickets se haraaya", "factoid", "WC result"),
    (18981, "orangi anp office blast mein kitne log halak hue", "event", "Karachi attack"),
    (22611, "huawei nova dual camera phones retail par kab aaye", "factoid", "Nova sale"),
    (75156, "chinese firm pakistani textile company ke kitne percent shares khareedegi", "factoid", "FDI stake"),
    (68949, "qandeel murder case ke main accused ko judicial remand par kyun jail bheja gaya", "event", "Multan court"),
    (44548, "sri lanka squad terror ke bawajood pakistan tour ke baad ghar kab lauta", "event", "historic tour"),
    (20866, "xiaomi mix 3 5g barcelona mwc par kab dikhaya gaya", "factoid", "MWC phone"),
    (21746, "mausam har chand mahine baad kyun badalta hai", "explanatory", "seasons science"),
    (3139, "asad umar committee ne steel mills lease ki tafseel kyun maangi", "event", "NA committee"),
    (106444, "angelina jolie maleficent trailer kis studio ne release kiya", "entity_person", "Disney trailer"),
    (20343, "chandrayaan 2 landing fail hui ya sirf contact toot gaya", "event", "ISRO mission"),
    (72832, "sbp annual report mein tax exports investment par kya gaps bataye gaye", "topical", "SBP yearbook"),
    (105894, "varun dhawan teri hero song video mein heroine ko kaise attract karta dikhaya gaya", "topical", "item song video"),
]

NL = [
    ("لاہور میں موسم سرما کی چھٹیوں کا شیڈول کب جاری ہوگا", "factoid", 0, "school calendar", ""),
    ("sindh board matric result kab announce hota hai usually", "factoid", 0, "exam timing", ""),
    ("پشاور یونیورسٹی میں ایم اے داخلے کی آخری تاریخ کیا ہے", "factoid", 0, "admissions", ""),
    ("how to renew cnic in nadra mega center without token confusion", "explanatory", 0, "civic process", ""),
    ("کراچی میں سبز لائن کے نئے سٹیشن کہاں کھلے ہیں", "location", 0, "transit", ""),
    ("multan metro bus route kis ilaqon se guzarti hai", "location", 0, "public transport", ""),
    ("آزاد کشمیر میں سیاحوں کے لیے نیلم وادی کا محفوظ راستہ کون سا ہے", "location", 0, "travel safety", ""),
    ("gilgit flight cancel hone par refund ka process kya hai", "explanatory", 0, "airline disruption", ""),
    ("پنجاب میں زرعی ٹیوب ویل کے بل کی ادائیگی آن لائن کیسے ہو", "explanatory", 0, "utility payment", ""),
    ("fbr iris par sales tax return upload karte waqt common error kya hota hai", "explanatory", 0, "tax filing", ""),
    ("کوئٹہ میں پانی کی قلت کی حالیہ وجوہات کیا بتائی جا رہی ہیں", "explanatory", 0, "municipal water", ""),
    ("why do load shedding schedules change every week in small cities", "explanatory", 0, "power roster", ""),
    ("پاکستان سپر لیگ کے نئے فرنچائز مالک کون بنے", "entity_person", 0, "league ownership", ""),
    ("wasim jaffer coaching stint pakistan A ke sath kab thi", "entity_person", 0, "coach tenure", ""),
    ("نعمی قریشی کی نئی کتاب کا موضوع کیا ہے", "entity_person", 0, "author work", ""),
    ("atif aslam live concert tickets lahore fort se kaise milte hain", "event", 0, "ticket access", ""),
    ("عالمی یوم معلم پر سرکاری اسکولوں میں کیا تقریبات ہوتی ہیں", "event", 0, "teachers day", ""),
    ("when is urs of data darbar usually observed in lahore", "event", 0, "cultural calendar", ""),
    ("سندھ تہذیبی میلے میں کون سے لوک ساز پیش کیے جاتے ہیں", "topical", 0, "folk culture", ""),
    ("pakistan mein e sports tournaments legally kaise register hote hain", "topical", 0, "gaming rules", ""),
    ("موبائل والیٹ سے بجلی کا بل ادا کرنے پر سروس چارج کتنا ہے", "factoid", 0, "fintech fee", ""),
    ("hajj quota pakistan ke liye is saal kitni announced hui thi", "factoid", 0, "pilgrimage quota", ""),
    ("سوموار کو بینکوں کے اوقات کار رمضان میں کیسے بدلتے ہیں", "factoid", 0, "banking hours", ""),
    ("can overseas pakistanis vote in general elections from gulf", "factoid", 1, "franchise rules vary", "I1: legal right to overseas vote in that election. I2: operational gulf polling stations exist."),
    ("پاکستان میں کم از کم اجرت صوبہ وار کہاں مختلف ہے", "topical", 0, "labour policy", ""),
    ("women protection helpline number punjab mein kya hai", "factoid", 0, "public service", ""),
    ("تھل میں سیلاب کے بعد خیمہ بستیوں کا بندوبست کون کرتا ہے", "location", 0, "disaster camps", ""),
    ("gwadar fishermen ko cpec port ke baad kis masle ka sab se zyada shikwa hai", "explanatory", 0, "livelihood", ""),
    ("کراچی پورٹ پر کنٹینر بیک لاگ کم کرنے کی کیا تجاویز ہیں", "explanatory", 0, "logistics", ""),
    ("why is smog worse in november around lahore canals", "explanatory", 0, "air quality", ""),
    ("فیصل آباد ٹیکسٹائل ملز کو گیس دباؤ کم ہونے سے کیا نقصان ہوتا ہے", "explanatory", 0, "industry energy", ""),
    ("cotton support price kis formula se decide hota hai", "explanatory", 0, "agri policy", ""),
    ("پاکستان میں آرگينک شہد کیسے تصدیق شدہ ہوتا ہے", "topical", 0, "food standards", ""),
    ("is bottled water quality tested monthly by psqca", "factoid", 0, "consumer safety", ""),
    ("لاہور زو میں نئے جانور کب لائے گئے", "event", 0, "zoo news", ""),
    ("margalla trail 5 monsoon ke baad hiking ke liye safe hai", "location", 0, "outdoor safety", ""),
    ("مری کی پہاڑی سڑک پر ٹریفک بندش کی اطلاع کہاں ملتی ہے", "location", 0, "road status", ""),
    ("karachi circular railway revival kis phase mein hai", "topical", 0, "infrastructure", ""),
    ("پاکستان ٹیلی ویژن کے پرانے ڈرامے یوٹیوب پر قانونی ہیں", "topical", 0, "archive access", ""),
    ("how do students apply for ehsaas undergraduate scholarship", "explanatory", 0, "student aid", ""),
    ("ہائر ایجوکیشن کمیشن کی اٹیسٹیشن کے لیے کون سے کاغذات درکار ہیں", "explanatory", 0, "HEC process", ""),
    ("punjab education commission grade 8 exam pattern kya hai", "factoid", 0, "PEC exam", ""),
    ("teachers assignment originality bina paid software ke kaise check karein", "explanatory", 0, "academic integrity", ""),
    ("پاکستان میں سائبر ہراسانی کی شکایت فیا کے پاس کیسے دائر ہو", "explanatory", 0, "cybercrime", ""),
    ("what documents are needed for police character certificate in islamabad", "factoid", 0, "civic document", ""),
    ("بلوچستان بورڈ انٹرمیڈیٹ سپلیمنٹری امتحان کب ہوتا ہے", "factoid", 0, "board calendar", ""),
    ("khyber medical university entry test syllabus kahan publish hota hai", "factoid", 0, "medical admissions", ""),
    ("آغاخان یونیورسٹی ہسپتال میں او پی ڈی کا وقت کیا ہے", "factoid", 0, "hospital hours", ""),
    ("siut dialysis registration ke liye kya procedure hai", "explanatory", 0, "public hospital", ""),
    ("ڈینگی کے بارے میں پنجاب ہیلتھ لائن کیا مشورہ دیتی ہے", "topical", 0, "public health", ""),
    ("measles vaccination catch up campaign kab chal rahi hai", "event", 0, "EPI campaign", ""),
    ("پاکستان میں ہیپاٹائٹس سی کا مفت علاج کہاں دستیاب بتایا جاتا ہے", "location", 0, "treatment access", ""),
    ("mental health ordinance ke under patient rights kya hain", "topical", 0, "health law", ""),
    ("کرکٹ کے علاوہ قومی ہاکی ٹیم کی اگلی سیریز کہاں ہے", "event", 0, "hockey calendar", ""),
    ("pakistan squash ranking mein current junior standout kaun hai", "entity_person", 0, "squash talent", ""),
    ("کبڈی ایشین گیمز میں پاکستان کا آخری میڈل کب آیا", "factoid", 0, "kabaddi", ""),
    ("women cricket domestic tournament ka naam kya hai ab", "factoid", 0, "domestic structure", ""),
    ("پی ایس ایل کے بجائے نیشنل ٹی ٹوئنٹی کپ کب کھیلا جاتا ہے", "event", 0, "domestic T20", ""),
    ("why do pakistan football clubs struggle in afc competitions", "explanatory", 0, "football development", ""),
    ("لاہور قذافی سٹیڈیم کی مرمت کب مکمل ہونے والی تھی", "location", 0, "venue works", ""),
    ("karachi national stadium flood lights upgrade hua ya nahi", "factoid", 0, "venue facilities", ""),
    ("پی ٹی آئی جلسہ اسلام آباد میں کس چوک پر ہونا تھا", "event", 0, "rally location", ""),
    ("senate elections proportional seats kaise allocate hoti hain", "explanatory", 0, "constitutional process", ""),
    ("الیکشن کمیشن کی حساس حلقوں کی فہرست کہاں جاری ہوتی ہے", "factoid", 0, "ECP notice", ""),
    ("local government act sindh ke mutabiq mayor ka tenure kitna hai", "factoid", 0, "LG law", ""),
    ("پاکستان میں حق معلومات کی درخواست کس فارم پر جاتی ہے", "explanatory", 0, "RTI", ""),
    ("how to check online fir status in punjab police portal", "explanatory", 0, "e-policing", ""),
    ("عدالت عظمی کے کیس کی سماعت کی تاریخ کیسے معلوم کریں", "explanatory", 0, "cause list", ""),
    ("nacta public advisory latest kis threat ke mutaliq hai", "event", 0, "security advisory", ""),
    ("سرحدی علاقے میں سکول بند کرنے کا فیصلہ کون کرتا ہے", "explanatory", 0, "school closure authority", ""),
    ("pakistan space weather alerts kis agency se aate hain", "factoid", 0, "space weather", ""),
    ("تھل چینل کی بحالی سے کون سے اضلاع کو پانی ملے گا", "location", 0, "irrigation", ""),
    ("indus river dolphin count latest survey mein kitna tha", "factoid", 0, "wildlife", ""),
    ("مکران ساحل پر کچھوؤں کے انڈے بچانے کی مہم کب ہوتی ہے", "event", 0, "conservation", ""),
    ("how is wheat seed certified before sowing in punjab", "explanatory", 0, "seed certification", ""),
    ("کراچی میں رین ہارویسٹنگ پائلٹ کہاں لگے", "location", 0, "urban water", ""),
    ("lahore waste management app par complaint ka ticket number kaise milta hai", "explanatory", 0, "municipal app", ""),
    ("پاکستان پوسٹ کی سپیڈ پوسٹ ترسیل کا تخمینی وقت کیا ہے", "factoid", 0, "postal service", ""),
    ("can i track international parcel on pakistan post website", "factoid", 0, "parcel tracking", ""),
    ("ریلوے رزرویشن چارٹ ٹرین چلنے سے کتنے گھنٹے پہلے فائنل ہوتا ہے", "factoid", 0, "rail reservation", ""),
    ("motorway m2 fog advisory kis number par milti hai", "factoid", 0, "NHA advisory", ""),
    ("پاکستان میں الیکٹرک سکوٹر رجسٹریشن کے قواعد کیا ہیں", "topical", 0, "EV rules", ""),
    ("is there a ban on used laptop import through baggage", "factoid", 0, "customs", ""),
    ("سمگل شدہ موبائل IMEI بلاک ہونے کے بعد واپسی کا طریقہ کیا ہے", "explanatory", 0, "PTA DIRBS", ""),
    ("pta complaint against spam sms ka portal kahan hai", "explanatory", 0, "telecom complaint", ""),
    ("پاکستان میں فری لانسرز کے لیے پیےون کا ٹیکس سٹیٹس کیا ہے", "topical", 0, "freelancer tax", ""),
    ("how do exporters claim drawback on stitched garments", "explanatory", 0, "trade facilitation", ""),
    ("سی پیک مغربی روٹ پر وزنی ٹریفک کی پابندی کب لگتی ہے", "location", 0, "western route", ""),
    ("gwadar airport naya terminal kab open hua tha", "event", 0, "airport", ""),
    ("پاکستان میں حلال سرٹیفیکیشن کون سا ادارہ دیتا ہے", "factoid", 0, "halal cert", ""),
    ("is basmati gi tag recognized for pakistan rice exports", "topical", 0, "GI dispute", ""),
    ("چائنہ پاکستان سائنس کانفرنس آخری بار کہاں ہوئی", "event", 0, "science diplomacy", ""),
    ("comsats islamabad fall admissions interviews kab start hote hain", "factoid", 0, "university calendar", ""),
    ("NUST کی انٹری ٹیسٹ کی تیاری کے مفت وسائل کہاں ہیں", "explanatory", 0, "NUST prep", ""),
    ("lums need based aid form deadline usually kab hoti hai", "factoid", 0, "financial aid", ""),
    ("پاکستان میں پبلک لائبریری ممبرشپ لاہور میں کیسے بنتی ہے", "explanatory", 0, "library access", ""),
    ("radio pakistan fm frequencies lahore ke liye kya hain", "factoid", 0, "broadcast", ""),
    ("ڈان اخبار کے آرکائیو مضامین مفت کب تک دستیاب رہتے ہیں", "topical", 0, "news archive", ""),
    ("how to file pemra complaint against a drama timeslot", "explanatory", 0, "media regulator", ""),
    ("پاکستان میں فیکٹ چیک ادارے الیکشن کے دوران کیا کردار ادا کرتے ہیں", "topical", 0, "fact checking", ""),
    ("climate change ministry heatwave advisory kis shehron ke liye hoti hai", "location", 0, "heatwave", ""),
    ("تھرپارکر میں خشک سالی ریلیف پیکیج میں کیا شامل بتایا گیا", "event", 0, "drought relief", ""),
    ("pakistan national disaster management authority app ka naam kya hai", "factoid", 0, "NDMA app", ""),
    ("کراچی میں سمندری طوفان کی وارننگ کون جاری کرتا ہے", "factoid", 0, "PMD cyclone", ""),
    ("does pakistan still run a locust control aircraft spray program", "factoid", 0, "locust control", ""),
    ("پنجاب میں اسکول وین کی حفاظتی کیمرہ پالیسی کیا ہے", "topical", 0, "child transport", ""),
    ("how are madaris required to register under the new mapping drive", "explanatory", 0, "madrasa mapping", ""),
    ("خواتین کے لیے پبلک ٹرانسپورٹ میں مخصوص ڈبہ کراچی بس میں ہے", "factoid", 0, "gendered transit", ""),
    ("is pink bus still operating in islamabad", "factoid", 0, "women bus", ""),
    ("پاکستان میں ٹرانس جینڈر تحفظ قانون کے تحت شناختی کارڈ کیسے بنتا ہے", "explanatory", 0, "CNIC process", ""),
]


def detect_script(query: str) -> str:
    urdu = sum(1 for c in query if "\u0600" <= c <= "\u06FF")
    latin = sum(1 for c in query if ("A" <= c <= "Z") or ("a" <= c <= "z"))
    if urdu == 0 and latin == 0:
        return "OTHER"
    if urdu > 0 and latin > 0:
        return "MIXED"
    if urdu > 0:
        return "URDU"
    return "ROMAN"


def length_bin_of(text: str) -> str:
    n = len(text.split())
    if n <= 5:
        return "short"
    if n <= 12:
        return "medium"
    return "long"


def tokens(text: str) -> set[str]:
    return set(TOKEN_RE.findall((text or "").lower()))


def overlap(q: str, h: str) -> float:
    qt = tokens(q)
    if not qt:
        return 1.0
    return len(qt & tokens(h)) / float(len(qt))


def kn_split(i: int) -> str:
    if i < 36:
        return "train"
    if i < 54:
        return "dev"
    return "test"


def nl_split(i: int) -> str:
    if i < 44:
        return "train"
    if i < 66:
        return "dev"
    return "test"


def load_headlines(ids: set[int]) -> dict[int, str]:
    out: dict[int, str] = {}
    with open(CORPUS, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
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


def write_csv(path: str, fields: list[str], rows: list[dict]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    if len(KN) != 90 or len(NL) != 110:
        print("count_error KN", len(KN), "NL", len(NL))
        return 1
    ids = {x[0] for x in KN}
    if len(ids) != 90:
        print("duplicate kn sources")
        return 1
    headlines = load_headlines(ids)
    kn_fields = [
        "query_id", "track", "script", "intent_type", "length_bin", "ambiguous",
        "query_text", "source_doc_id", "source_article_hash_or_identifier",
        "headline_overlap", "writer_id", "creation_timestamp", "split", "status",
        "notes", "interpretation_notes",
    ]
    nl_fields = [
        "query_id", "track", "script", "intent_type", "length_bin", "ambiguous",
        "query_text", "writer_id", "creation_timestamp", "split", "status",
        "notes", "interpretation_notes",
    ]
    kn_by_split = {"train": [], "dev": [], "test": []}
    rejects = []
    for i, (sid, qtext, intent, notes) in enumerate(KN):
        hl = headlines.get(sid, "")
        ov = overlap(qtext, hl)
        if ov >= 0.50 or not tokens(qtext):
            rejects.append((sid, ov, qtext, hl))
            continue
        split = kn_split(i)
        status = "sealed" if split == "test" else "accepted"
        kn_by_split[split].append({
            "query_id": "KN%03d" % (i + 1),
            "track": "KN",
            "script": detect_script(qtext),
            "intent_type": intent,
            "length_bin": length_bin_of(qtext),
            "ambiguous": 0,
            "query_text": qtext,
            "source_doc_id": sid,
            "source_article_hash_or_identifier": "index:%s" % sid,
            "headline_overlap": "%.6f" % ov,
            "writer_id": WRITER,
            "creation_timestamp": TS,
            "split": split,
            "status": status,
            "notes": notes,
            "interpretation_notes": "",
        })
    if rejects:
        print("KN_OVERLAP_REJECTS", len(rejects))
        for item in rejects:
            print("reject", item[0], "%.4f" % item[1], item[2][:80])
        return 2
    nl_by_split = {"train": [], "dev": [], "test": []}
    for i, (qtext, intent, amb, notes, inotes) in enumerate(NL):
        split = nl_split(i)
        status = "sealed" if split == "test" else "accepted"
        nl_by_split[split].append({
            "query_id": "NL%03d" % (i + 1),
            "track": "NL",
            "script": detect_script(qtext),
            "intent_type": intent,
            "length_bin": length_bin_of(qtext),
            "ambiguous": amb,
            "query_text": qtext,
            "writer_id": WRITER,
            "creation_timestamp": TS,
            "split": split,
            "status": status,
            "notes": notes,
            "interpretation_notes": inotes,
        })
    for split in ("train", "dev", "test"):
        write_csv(os.path.join(BENCH, split, "queries_kn.csv"), kn_fields, kn_by_split[split])
        write_csv(os.path.join(BENCH, split, "queries_nl.csv"), nl_fields, nl_by_split[split])
        print(split, "kn", len(kn_by_split[split]), "nl", len(nl_by_split[split]))
    from collections import Counter
    scripts = Counter(r["script"] for sp in kn_by_split.values() for r in sp)
    scripts.update(r["script"] for sp in nl_by_split.values() for r in sp)
    print("scripts", dict(scripts))
    print("status: WROTE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
