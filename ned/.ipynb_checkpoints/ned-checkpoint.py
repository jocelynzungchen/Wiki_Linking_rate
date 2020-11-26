import os
from typing import List, Tuple


from .load_data import load_bold, load_redirect, load_anchor

from opencc import OpenCC
s2tw = OpenCC('s2tw') 
tw2s = OpenCC('tw2s') 

def gen_confusion_chinese(entity: str): # 產生各種簡繁候選字
    
    confusion_set = set()
    confusion_set.add(entity)
    confusion_set.add(s2tw.convert(entity))
    confusion_set.add(tw2s.convert(entity))

    return confusion_set

def disambiguate_rule(candidates, entity, theta=0.5, min_anchor_count=10):
    
    wikiid = -1
    
    if candidates['redirect'] != -1:
        wikiid = candidates['redirect']
    elif candidates['title'] != -1 and entity not in load_redirect.REDIRECT_TABLE.redirect2id:
        wikiid = candidates['title']
    elif len(candidates['bold']) == 1:
        wikiid = candidates['bold'][0]
    elif candidates['anchor']:
        total_count = sum(candidates['anchor'].values())
        if total_count >= min_anchor_count:
            key, count = max(candidates['anchor'].items(), key=lambda x: x[1])
            if count >= total_count // 2:
                wikiid = key
    
    return _id2title(wikiid)



def gen_NE_candidates(entity: str):
    
    title_result = check_title(entity)
    if title_result in load_bold.BOLD_TABLE.disambiguate_pages:
        title_result = -1
    
    redirect_result = check_redirect(entity)
    if redirect_result in load_bold.BOLD_TABLE.disambiguate_pages:
        redirect_result = -1
    
    bold_result = check_bold(entity)
    bold_result = [bold for bold in bold_result if bold not in load_bold.BOLD_TABLE.disambiguate_pages]
    
    anchor_result = check_anchor(entity)
    anchor_result = {key:value for key, value in anchor_result.items() if key not in load_bold.BOLD_TABLE.disambiguate_pages}
    
    return {'title': title_result, 'redirect': redirect_result, 'bold': bold_result, 'anchor': anchor_result}


    
def check_title(text: str) -> int:
    return load_bold.BOLD_TABLE.title2id.get(text, -1)

def check_redirect(text: str) -> int:
    
    wikiid = -1
    while text in load_redirect.REDIRECT_TABLE.redirect2id:
        wikiid = load_redirect.REDIRECT_TABLE.redirect2id[text]
        text = _id2title(wikiid)
    
    return wikiid

def check_bold(text: str) -> List[int]:
    return load_bold.BOLD_TABLE.bold2id.get(text, [])

def check_anchor(text: str) -> List[Tuple[int, int]]:
    return load_anchor.ANCHOR_TABLE.anchor2count.get(text, {})
    
def _id2title(wikiid: int) -> str:
    return load_bold.BOLD_TABLE.id2title.get(wikiid, "")


def disambiguate_NE(entity: str):

    title = ""
    for entity in gen_confusion_chinese(entity):
        candidates = gen_NE_candidates(entity)
        title = disambiguate_rule(candidates, entity)

        if title:
            return title
    return title
        


