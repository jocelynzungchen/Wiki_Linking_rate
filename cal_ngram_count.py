from pyspark import SparkConf, SparkContext
import re
import json
from opencc import OpenCC

s2tw = OpenCC('s2tw')

def load_mentions(file_name):
    with open(file_name) as file:
        mention_count = json.load(file)
        return set([key for key in mention_count.keys()])


mention_set = load_mentions('mention_entities-zh.json')


def ngrams(n, line):
    def legal(string):
        if string in mention_set:
            return True
        return False

    return [ line[i:i+n] for i in range(len(line)-n+1) if legal(line[i:i+n])]


def gen_candidates(n_min, n_max, line):
    candidates = []
    for n in range(n_min, n_max+1):
        candidates += ngrams(n, line)
    return candidates


def mapper(line):
    item = eval(line)
    all_candidates = set()
    for sent in item["text"].split('\n'):
        if not sent.strip():
            continue
        sent = re.sub('<a href=(.+?)>', '', sent.strip())
        sent = re.sub('</a>', '', sent)
        sent = s2tw.convert(sent)
        for c in gen_candidates(1, 15, sent):
            all_candidates.add((c, 1))
    
    return list(all_candidates)


if __name__ == "__main__":

    conf = SparkConf().set("spark.default.parallelism", 4)
    sc = SparkContext(conf=conf)

    lines = sc.textFile('/home/nlplab/jocelyn/wiki_page_data/OUTPUT/*/*').flatMap(mapper).reduceByKey(lambda x, y: x+y)
 
    print("{}\t{}".format("ngram", "count"))
    for (term, count) in lines.collect():
        print("{}\t{}".format(term, count))