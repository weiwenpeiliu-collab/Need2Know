#!/usr/bin/env python3
"""Offline integrity check for the anonymous Need2Know data-only release."""
import json
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parent

def read(rel):
    p=ROOT/rel
    return [json.loads(line) for line in p.read_text('utf-8').splitlines() if line.strip()]

def ensure(cond,why):
    if not cond:raise AssertionError(why)

spec=read('data/task_definitions.jsonl')
main={k:read(f'data/requests/{k}.jsonl') for k in ('implicit','explicit','no_tool')}
non=read('data/non_gold_tool_responses.jsonl')
rob={k:read('data/robustness/'+k+'.jsonl') for k in ('minimal_edit_explicit_51','retrieval_only_51')}
base={r['task_id']:r for r in spec}
ids=[r['task_id'] for r in spec]
ensure(len(ids)==len(base)==203,'203 distinct task IDs required')
for cond,rows in main.items():
    ensure(len(rows)==203,'203 '+cond+' requests required')
    ensure([r['task_id'] for r in rows]==ids,cond+' IDs/order mismatch')
    ensure(all(r['query'] for r in rows),cond+' empty query')
    if cond=='no_tool':
        ensure(all(r['requires_external_evidence'] is False and r['expected_initial_action']=='final_response' for r in rows),'no-tool control labels')
for t in spec:
    candidate=t['candidate_tools']
    ensure(len(candidate)==5 and len({x['apiCode'] for x in candidate})==5,'five candidate tools '+t['task_id'])
    ensure(t['gold']['tool_name'] in {x['apiCode'] for x in candidate},'Gold missing '+t['task_id'])
    core=t['gold']['required_response_fields']
    ensure(set(t['tool_results'])=={'low','medium','high'},'bad tiers '+t['task_id'])
    low=t['tool_results']['low']
    for level in ('low','medium','high'):
        result=t['tool_results'][level]
        ensure(all(k in result and result[k]==low[k] for k in core),'Core mismatch '+t['task_id']+'/'+level)
        pol=t['evidence_policy'][level]
        for tag in ('required_visible_evidence','prohibited_sensitive_evidence'):
            ensure(all(x['field'] in result and result[x['field']]==x['value'] for x in pol[tag]),'Policy mismatch '+t['task_id']+'/'+level)
ensure(len(non)==812,'812 non-Gold fixtures required')
seen=set(); freq=Counter()
for r in non:
    key=(r['task_id'],r['tool_name'])
    ensure(key not in seen,'duplicate non-Gold fixture '+str(key))
    seen.add(key);freq[r['task_id']]+=1
    t=base[r['task_id']]
    ensure(r['tool_name'] in {x['apiCode'] for x in t['candidate_tools']} and r['tool_name']!=t['gold']['tool_name'],'bad non-Gold mapping '+str(key))
ensure(all(freq[tid]==4 for tid in ids),'4 non-Gold fixtures per task')
for cond in ('implicit','explicit'):
    a=read('data/evaluation/'+cond+'_evidence_gap.jsonl')
    ensure(len(a)==203 and [r['task_id'] for r in a]==ids,cond+' judge annotation pairing')
a,b=rob.values();ensure(len(a)==len(b)==51,'51 robustness tasks each')
ensure([r['task_id'] for r in a]==[r['task_id'] for r in b],'robustness ID pairing')
queries={r['task_id']:r['query'] for r in main['implicit']}
pre='Please first look up the relevant external information before answering.'
for x,y in zip(a,b):
    orig=queries[x['task_id']]
    ensure(x['query'].endswith(orig),'minimal edit changed implicit request')
    ensure(y['query']==pre+' '+orig,'retrieval-only prompt mismatch')
print('PASS: 203 aligned triplets; 5 tools each; 609 Gold-tier fixtures; 812 non-Gold fixtures; 51 robustness pairs; evaluation annotations.')
