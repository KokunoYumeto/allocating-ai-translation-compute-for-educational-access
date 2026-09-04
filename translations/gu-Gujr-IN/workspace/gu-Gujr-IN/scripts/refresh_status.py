"""Refresh factual counts from the coverage/QA files, without declaring completion."""
import csv
from datetime import datetime
import json
from pathlib import Path

LANG=Path(__file__).resolve().parents[1]


def read(name):
    return json.loads((LANG/name).read_text(encoding='utf-8'))


def main():
    coverage=read('COVERAGE.json')
    queue=read('WORK_QUEUE.json')
    qa=read('LIBRARY_QA.json')
    terms=list(csv.DictReader((LANG/'terminology.csv').open(encoding='utf-8')))
    modules=coverage['modules']
    checked={m['key']:m for m in qa['modules']}
    status=read('STATUS.json')
    if 'translated' in status:
        status['checkpoint_40f1ab6']={'translated':status.pop('translated'),'separate_companion':status.pop('separate_companion'),'outputs':status.pop('outputs')}
    status['schema']='gujarati-full-assignment-status-v1'
    status['date']=datetime.now().date().isoformat()
    status['state']='full_assignment_in_progress'
    status['assignment_complete']=False
    status['full_modules_workflow_complete']={'A00':0,'A10':0}
    status['complete_source_drafts_with_structure_checks']={book:[m['module_id'] for m in modules if m['program']==book and m['source_translation']=='draft_complete_pending_review' and checked.get(book+':'+m['module_id'],{}).get('complete_source_tree')] for book in ('A00','A10')}
    status['current_parallel_work']={name:details['role'] for name,details in queue['workers'].items()}
    status['current_library']={'html_pages_checked':qa['html_pages_checked'],'source_exercises':sum(m['exercises'] for m in qa['modules']),'source_supplied_solutions':sum(m['source_solutions'] for m in qa['modules']),'added_worked_answers':sum(m.get('added_worked_answers',{}).get('count',0) for m in modules),'terminology_entries':len(terms),'tagged_screen_pdf_complete':False,'native_educator_review_complete':False}
    status['verification_receipts']=list(dict.fromkeys(status['verification_receipts']+['A00_ADDED_SOLUTIONS_QA.json','A00_ADDITION_ANSWERS_QA.json','A00_SUBTRACTION_ANSWERS_QA.json','A00_MULTIPLICATION_ANSWERS_QA.json','A00_DIVISION_ANSWERS_QA.json','A10_ALGEBRA_ANSWERS_QA.json','MULTIPLICATION_FIGURE_QA.json','DIVISION_FIGURE_QA.json','reviews/a10-m82454-figures-qa.json','reviews/a10-m82454-figures-browser.json','reviews/a10-m82454-figures-root-browser.json','reviews/a10-m82455-figures-qa.json','reviews/a00-m81268-figures-qa.json','reviews/sixteen-draft-browser.json','reviews/nineteen-draft-browser.json','reviews/a10-m82456-figures-qa.json','reviews/a00-pinned-assessment-counts.json','A10_FRONT_MATTER_QA.json','WORK_QUEUE.json']))
    status['verification_receipts']=list(dict.fromkeys(status['verification_receipts']+['A10_INTEGER_ANSWERS_QA.json','reviews/twenty-three-draft-browser.json','reviews/a10-m82457-figures-qa.json','reviews/a10-m82458-qa.json','reviews/a10-m82454-added-solutions-independent.md','reviews/a10-m82454-added-solutions-independent-qa.json']))
    pdf_receipt=LANG/'reviews/a00-m81243-tagged-pdf-qa.json'
    if pdf_receipt.exists():
        pdf=read('reviews/a00-m81243-tagged-pdf-qa.json')
        status['tagged_pdf_technical_draft']={'module':'A00:m81243','path':'output/tagged-screen-pdf/a00-m81243.pdf','pages':pdf['pages'],'sha256':pdf['pdf_sha256'],'structure_errors':pdf['errors'],'screen_accessibility_complete':False,'known_limitation':'PDF.js and plain pypdf lose some Gujarati shaped clusters; HTML remains preferred. No PDF/UA claim.'}
    status['next_source_boundary']={name:details.get('source_modules',[]) for name,details in queue['workers'].items() if details.get('source_modules')}
    status['pending']=['Continue all remaining assigned source modules','Localize and review all diagrams','Complete AX-3 definitions/summaries/worked scaffolding and diagnostic-remediation sequence','Portable offline package for current and final editions','Tagged screen and print PDF workflows','Gujarati educator review','Child usability check','Screen-reader and keyboard evaluation']
    (LANG/'STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(status['current_library'],ensure_ascii=False))


if __name__=='__main__':main()
