from collections import defaultdict, Counter
import json


def load_data(mention_file_1, mention_file_2, ngram_file):
    ngram_count = Counter()
    with open(mention_file_1) as f_1, open(mention_file_2) as f_2, open(ngram_file) as f_3:
        mention_count_v1 = json.load(f_1)
        mention_count_v2 = json.load(f_2)
        next(f_3)
        for line in f_3:
            line = line.split('\t')
            ngram_count[line[0]] = int(line[1])
    return mention_count_v1, mention_count_v2, ngram_count


def calculate_linking_rate(mention_count, ngram_count):
    linking_rate = Counter()
    for key in mention_count:
        if key in ngram_count:
            rate = round(mention_count[key]/ngram_count[key], 3)
            linking_rate[key] = rate
    return linking_rate


def write_to_file(file_map):
    for file_name, dictionary in file_map.items():
        with open(file_name, 'w') as outf:
            json.dump(dictionary, outf, ensure_ascii=False)


if __name__ == "__main__":
    
    mention_count_v1, mention_count_v2, ngram_count = load_data('mention_count-zh.json', 'mention_count_v2-zh.json', 'ngram_count.txt')

    linking_rate_v1 = calculate_linking_rate(mention_count_v1, ngram_count)
    linking_rate_v2 = calculate_linking_rate(mention_count_v2, ngram_count)

    file_map = {'mention_linking_rate-zh_test.json': linking_rate_v1, 
                'mention_linking_rate_v2-zh_test.json': linking_rate_v2}
    write_to_file(file_map)