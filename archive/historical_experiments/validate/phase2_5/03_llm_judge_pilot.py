# -*- coding: utf-8 -*-
"""Phase 2.5: preliminary local-LLM relevance judging via Ollama.

Run from repository root:
  python validate\\phase2_5\\03_llm_judge_pilot.py --limit 8

This creates a separate CSV and NEVER modifies judgment_template.csv.
The judge receives only query + article headline + article text; it is not
shown word_count, script, tag, pre_registered_hypothesis, retrieval mode,
rank, or retrieval score.
"""
import argparse, csv, json, os, re, sys, urllib.error, urllib.request
from collections import OrderedDict

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
DEFAULT_MODEL = "qwen3:0.6b"
PHASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(PHASE_DIR))
DEFAULT_INPUT = os.path.join(PHASE_DIR, "judgment_template.csv")
DEFAULT_OUTPUT = os.path.join(PHASE_DIR, "llm_judgments_pilot.csv")
CORPUS_CSV = os.path.join(REPO_ROOT, "data", "clean_articles.csv")
ALLOWED = {"relevant":"Relevant", "partially relevant":"Partially relevant", "partial":"Partially relevant", "partially_relevant":"Partially relevant", "not relevant":"Not relevant", "not_relevant":"Not relevant"}

SYSTEM_PROMPT = """Read the USER QUERY and the NEWS ARTICLE.

Judge whether the NEWS ARTICLE satisfies the event or information requested by the USER QUERY.

Important:
- Same topic alone does NOT mean relevant.
- The article must describe the event asked for by the query.
- If the article describes the opposite event or outcome, mark it Not relevant.
- Example: if the query says the market rose, an article mainly saying the market fell is Not relevant.
- Related background information can be Partially relevant if it does not fully satisfy the query.
- Do NOT use word count, SHORT, LONG, QUERY-DEPENDENT, or any hypothesis.
- Judge only the query and article content.

Choose exactly one:
Relevant
Partially relevant
Not relevant

Confidence must be exactly one of:
high
medium
low

Return ONLY valid JSON:
{"relevance":"Relevant","confidence":"high"}

No explanation.
No markdown.
No extra text."""


def args():
    p=argparse.ArgumentParser()
    p.add_argument('--input',default=DEFAULT_INPUT)
    p.add_argument('--output',default=DEFAULT_OUTPUT)
    p.add_argument('--limit',type=int,default=1)
    p.add_argument('--start',type=int,default=0)
    p.add_argument('--all',action='store_true')
    p.add_argument('--model',default=DEFAULT_MODEL)
    p.add_argument('--article-chars',type=int,default=3500)
    p.add_argument('--timeout',type=int,default=300)
    return p.parse_args()

def read_template(path):
    with open(path,encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
    if not rows: raise RuntimeError('judgment_template.csv is empty.')
    req={'query_id','query','retrieval_mode','rank','doc_id','doc_headline','relevance'}
    missing=req-set(rows[0])
    if missing: raise RuntimeError(f'Missing required columns: {sorted(missing)}')
    return rows

def select(rows,start,limit,all_rows):
    eligible=[(i,r) for i,r in enumerate(rows) if r.get('relevance','').strip().upper()=='UNJUDGED']
    return (eligible[start:] if all_rows else eligible[start:start+limit]),len(eligible)

def load_articles(path,wanted):
    found={}
    with open(path,encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        for idx,row in enumerate(reader):
            if idx in wanted:
                found[idx]={'headline':row.get('Headline',''),'news_text':row.get('News Text',''),'category':row.get('Category','')}
                if len(found)==len(wanted): break
    missing=sorted(set(wanted)-set(found))
    if missing: raise RuntimeError('Missing doc_id values: '+','.join(map(str,missing[:20])))
    return found

def check_model(model,timeout):
    req=urllib.request.Request('http://127.0.0.1:11434/api/tags')
    with urllib.request.urlopen(req,timeout=timeout) as r: obj=json.loads(r.read().decode())
    names={m.get('name') for m in obj.get('models',[]) if isinstance(m,dict)}
    if model not in names: raise RuntimeError(f"Model '{model}' is not installed. Run: ollama pull {model}")

def call(model,query,headline,text,timeout,maxchars):
    article=text.strip()
    if len(article)>maxchars: article=article[:maxchars]+'\n[ARTICLE TEXT TRUNCATED FOR THIS PILOT]'
    prompt=f'USER QUERY:\n{query}\n\nARTICLE HEADLINE:\n{headline}\n\nARTICLE TEXT:\n{article}'
    payload={'model':model,'messages':[{'role':'system','content':SYSTEM_PROMPT},{'role':'user','content':prompt}], 'stream':False, 'think':False, 'options':{'temperature':0}}
    data=json.dumps(payload,ensure_ascii=False).encode('utf-8')
    req=urllib.request.Request(OLLAMA_URL,data=data,headers={'Content-Type':'application/json'},method='POST')
    with urllib.request.urlopen(req,timeout=timeout) as r: obj=json.loads(r.read().decode('utf-8'))
    content=(obj.get('message',{}).get('content','') or '').strip()
    return content

def parse(content):
    candidates=[content]
    m=re.search(r'\{.*\}',content,re.S)
    if m: candidates.append(m.group(0))
    for s in candidates:
        try:
            o=json.loads(s); lab=str(o.get('relevance','')).strip().lower(); conf=str(o.get('confidence','')).strip().lower()
            if lab in ALLOWED and conf in {'high','medium','low'}: return ALLOWED[lab],conf
        except Exception: pass
    return None,None

def main():
    a=args()
    if not os.path.exists(a.input): raise FileNotFoundError(f'Input not found: {a.input}')
    if not os.path.exists(CORPUS_CSV): raise FileNotFoundError(f'Corpus not found: {CORPUS_CSV}')
    print('[1/4] Checking Ollama...'); check_model(a.model,a.timeout); print('      OK')
    rows=read_template(a.input)
    selected,total=select(rows,a.start,a.limit,a.all)
    print(f'[2/4] {len(rows)} template rows; {total} UNJUDGED; selected {len(selected)}')
    if not selected: print('Nothing to judge.'); return
    ids={int(r['doc_id']) for _,r in selected if str(r['doc_id']).strip().lstrip('-').isdigit()}
    print('[3/4] Loading required articles...'); articles=load_articles(CORPUS_CSV,ids); print(f'      Loaded {len(articles)}')
    out=[]
    for n,(source_idx,row) in enumerate(selected,1):
        doc_id=int(row['doc_id'])
        raw=call(a.model,row['query'],articles[doc_id]['headline'],articles[doc_id]['news_text'],a.timeout,a.article_chars)
        label,conf=parse(raw)

        if not label:
            print(f'      Invalid response for {row["query_id"]}; retrying once...')
            raw_retry=call(a.model,row['query'],articles[doc_id]['headline'],articles[doc_id]['news_text'],a.timeout,a.article_chars)
            label,conf=parse(raw_retry)
            raw=raw + "\n[RETRY RESPONSE]\n" + raw_retry

        if not label:
            label='LLM_UNPARSEABLE'
            conf='low'
        x=OrderedDict()
        x['source_csv_row']=source_idx+2; x['query_id']=row['query_id']; x['query']=row['query']; x['retrieval_mode']=row['retrieval_mode']; x['rank']=row['rank']; x['doc_id']=row['doc_id']; x['doc_headline']=row['doc_headline']; x['doc_category']=row.get('doc_category',''); x['retrieval_score']=row.get('score',''); x['llm_relevance']=label; x['llm_confidence']=conf; x['llm_model']=a.model; x['raw_llm_response']=raw
        out.append(x); print(f'      [{n}/{len(selected)}] {row["query_id"]} | {row["retrieval_mode"]} | rank {row["rank"]} -> {label} ({conf})')
    print('[4/4] Writing separate LLM output...')
    with open(a.output,'w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    print(f'Done: {a.output}')
    print('judgment_template.csv was NOT modified. These are preliminary LLM judgments; do not run script 02 on them yet.')

if __name__=='__main__':
    try: main()
    except KeyboardInterrupt: print('\nStopped.'); sys.exit(130)
    except Exception as e: print(f'ERROR: {e}',file=sys.stderr); sys.exit(1)
