from opencc import OpenCC
import glob
from collections import defaultdict, Counter
import json
from ned import load_bold, load_redirect

tw2s = OpenCC('tw2s')
s2tw = OpenCC('s2tw')


class MentionExtractor():
    def __init__(self, ver=1, mention_set=None):
        self.ver = ver
        self.mention_set = mention_set
        self.mention_count = Counter()
        self.mention_entities = defaultdict(Counter)

    def load_data(self, file_paths):
        for f_path in file_paths:
            with open(f_path) as file:
                for document in file:
                    self.__extract_links(eval(document))

    def get_mention_count(self):
        return self.mention_count

    def get_mention_entities(self):
        return self.mention_entities


    def __extract_links(self, document):
        def gen_candidates(n_min, n_max, line):
            def ngrams(n, line): # 只考慮有被超連結過的片語
                return [line[i:i+n] for i in range(len(line)-n+1) if line[i:i+n] in self.mention_set]
            candidates = []
            for n in range(n_min, n_max+1):
                candidates += ngrams(n, line)
            return candidates

        def update_doc_count(mention, entity_id):
            mention_dict[mention].add(entity_id)
            if self.ver != 1: # 考慮部分比對
                for sub_mention in gen_candidates(1, len(mention)-1, mention):
                    mention_dict[sub_mention].add(entity_id)

        mention_dict = defaultdict(set)
        for line in document["text"]:
            for link in line['links']:
                start, end = link[:2]
                mention = s2tw.convert(line['line'])[start:end]
                entity = link[2]
                entity_id = self.__check_redirect(entity)
                if entity_id != -1:
                    update_doc_count(mention, entity_id, ver)
        self.__update_result(mention_dict)


    def __check_redirect(self, text, layer=0):
        r_table = load_redirect.REDIRECT_TABLE_zh

        wikiid = load_bold.BOLD_TABLE_zh.title2id.get(text, -1)
        redirect_count = 0
        while text in r_table.redirect2id and redirect_count < 10:
            wikiid = r_table.redirect2id[text]
            text = load_bold.BOLD_TABLE_zh.id2title.get(wikiid, "")
            redirect_count += 1
        
        if wikiid == -1 and layer == 0: # 檢查是不是簡體繁體的問題
            for t in {s2tw.convert(text), tw2s.convert(text)}:
                wikiid = self.__check_redirect(t, 1)
                if wikiid != -1:
                    return wikiid
        return wikiid


    def __update_result(self, mention_dict):
        for mention, entity_ids in mention_dict.items():
            self.mention_count[mention] += 1
            if self.ver == 1:
                for entity_id in entity_ids:
                    self.mention_entities[mention][entity_id] += 1



def write_to_file(file_map):
    for file_name, dictionary in file_map.items():
        with open(file_name, 'w') as outf:
            json.dump(dictionary, outf, ensure_ascii=False)


if __name__ == "__main__":

    all_paths = [path for path in glob.glob("/home/nlplab/jocelyn/wiki_page_data/linking_data/*/*"]
    
    # obtain result of mention_entities & mention_count_v1
    metion_extractor_1 = MentionExtractor(ver=1)
    metion_extractor_1.load_data(all_paths)
    mention_count_v1 = metion_extractor_1.get_mention_count()
    mention_entities = metion_extractor_1.get_mention_entities()

    # obtain result of mention_count_v2 (need mention_set)
    mention_set = set([key for key in mention_count_v1])
    metion_extractor_2 = MentionExtractor(ver=2, mention_set)
    metion_extractor_2.load_data(all_paths)
    mention_count_v2 = metion_extractor_2.get_mention_count()

    file_map = {'mention_entities-zh_test.json': mention_entities, 
                'mention_count-zh_test.json': mention_count_v1, 
                'mention_count_v2-zh_test.json': mention_count_v2}
    write_to_file(file_map)