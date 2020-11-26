import os
import csv

from .load_bold import BOLD_TABLE_zh


BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA_DIR = os.path.join(BASE_DIR, "ned_data")

class redirect_table(object):
    
    def __init__(self, lang='en'):
        self.load_redirect(lang)
        
        
    def load_redirect(self, lang='en', headers=True):
        
        file="enwiki-latest-redirect.tsv" if lang == 'en' else "zhwiki-latest-redirect.tsv"
        redirect_file = os.path.join(DATA_DIR, file)
        self.redirect2id = {} # {from_title: to_id}

        bold_table = BOLD_TABLE if lang == 'en' else BOLD_TABLE_zh
        
        with open(redirect_file, errors='replace') as csvfile:
            
            spamreader = csv.reader(csvfile, delimiter='\t')
            
            if headers:
                next(spamreader, None)
            
            for row in spamreader:
                
                wikiid, _, redirect, _, _ = row
                redirect = self._normalize_title(redirect)
                wikiid = int(wikiid)
                

                # 確認該筆資料是否有在 bold 裡面（且為正確的）
                if wikiid not in bold_table.id2title or redirect not in bold_table.title2id:
                    continue
                    
                redirect_text = bold_table.id2title[wikiid] # from_title
                redirect_id = bold_table.title2id[redirect] # to_id
                
                    
                self.redirect2id[redirect_text] = redirect_id
                
    def _normalize_title(self, title):
        return title.replace("_", " ")
                

# REDIRECT_TABLE = redirect_table('en')
REDIRECT_TABLE_zh = redirect_table('zh')