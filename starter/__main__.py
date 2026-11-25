"""Run with python -m starter --help."""
import argparse
import json
import sys
from pathlib import Path
from .core import PROMPTS, answer, bounded_text, decide, propose, run_agent
from .runtime import Ollama


def main():
    parser=argparse.ArgumentParser(description='Original local AI starters / Plantillas locales')
    parser.add_argument('example',choices=['agent','workflow','qa'])
    parser.add_argument('--question',default='notebook stock / inventario notebook')
    parser.add_argument('--lang',choices=['es','en'],default='es')
    parser.add_argument('--offline',action='store_true',help='Deterministic fixture; no model inference')
    parser.add_argument('--model',default='qwen3:4b')
    parser.add_argument('--workspace',type=Path,default=Path('output/demo'))
    parser.add_argument('--decision',choices=['APPROVE','REJECT'])
    args=parser.parse_args()
    if args.offline: print('OFFLINE FIXTURE: deterministic plumbing demo; no model inference.',file=sys.stderr)
    calls=0
    def fixture(messages, timeout):
        nonlocal calls
        calls+=1
        if args.example=='agent':
            return {'tool':'stock','arguments':{'item':'notebook'}} if calls==1 else {'answer':'12 notebooks [offline fixture]'}
        if args.example=='workflow': return {'draft':'Gracias por contactarnos. / Thank you for contacting us. [offline fixture]'}
        return {'answer':'Devoluciones: 30 días / Returns: 30 days [policy.txt]','sources':['policy.txt']}
    model=fixture if args.offline else Ollama(args.model)
    try:
        if args.example=='agent': result=run_agent(model,args.question,args.lang)
        elif args.example=='qa':
            data=Path(__file__).resolve().parent.parent/'data'
            docs={p.name:p.read_text(encoding='utf-8') for p in data.glob('*.txt')}
            result=answer(args.question,docs,model,args.lang)
        elif args.decision: result=decide(args.workspace,args.decision)
        else:
            draft=model([{'role':'system','content':PROMPTS[args.lang]+' Draft a short support acknowledgment only. JSON {"draft":"text"}.'},{'role':'user','content':bounded_text(args.question)}],30)
            if not isinstance(draft,dict) or set(draft)!={'draft'}: raise ValueError('Invalid draft response')
            result=propose(args.workspace,draft['draft'])
        print(json.dumps(result,ensure_ascii=False,indent=2))
    except (ValueError, OSError, KeyError, TypeError, TimeoutError) as exc:
        parser.exit(1,'Error: '+str(exc)+'\n')

if __name__=='__main__': main()
