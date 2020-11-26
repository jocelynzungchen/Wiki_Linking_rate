# Wiki_Linking_rate

### Goal
-
計算維基百科中的片語被超連結的比例。\
例如：（摘自中文維基百科中「美國總統」內文）
> *...美國現任（第45任）總統為<a href="https://zh.wikipedia.org/wiki/%E5%85%B1%E5%92%8C%E9%BB%A8_(%E7%BE%8E%E5%9C%8B)">共和黨</a>籍的<a href="https://zh.wikipedia.org/wiki/%E5%94%90%E7%B4%8D%C2%B7%E5%B7%9D%E6%99%AE">唐納·川普</a>，於2017年就任。...*

其中 `唐納·川普` 與 `共和黨` 為兩個有被超連結的片語。此 repo 的目標為計算所有有被超連結過的片語被超連結的比例（有被超連結的次數/總共出現果的次數），作為一個片語是否需要被賦予超連結的參考。\
次數以 document count 來計算。（某個片語出現在幾個維基頁面中（或在幾個頁面中有被超連結），而不考慮在某個頁面底下出現的次數）

### Issue
***
針對「被超連結次數」提供了兩種算法，一種是只考慮整個片語，一種是考慮部分比對。\
例如上述句子中，「唐納·川普」被超連結，在第一種版本中，只有「唐納·川普」這個片語屬於「被超連結的片語」（被超連結次數加一），而第二種版本中我除了「唐納·川普」也把「唐納」、「川普」、「川」...等等的片語也當作「被超連結的片語」。\
考慮部分比對後，許多片語在第二種算法下被超連結的比例就會大幅上升。例如：「川普」在第一種算法下的被超連結的比例為 0.172 ，而第二種為 0.744。但也會造成部分片語因常和別的詞結合成專有名詞而導致被超連結率很高。

### Steps
***
1. Dump Wikipedia 原始資料\
[https://dumps.wikimedia.org/zhwiki/latest/](https://dumps.wikimedia.org/zhwiki/latest/)\
下載 `zhwiki-latest-pages-articles-multistream.xml.bz2`

2. Parse 原始資料成 json 檔\
[https://github.com/attardi/wikiextractor](https://github.com/attardi/wikiextractor)\
處理完檔案位置：`jocelyn/wiki_page_data/OUTPUT`

    ```bash
    pip install wikiextractor

    python -m wikiextractor.WikiExtractor --process 20 -o OUTPUT --json -l [path_of_your_zhwiki-latest-pages-articles-multistream.xml.bz2_file]
    ```
    ```bash
    格式：
    {"id": "13",  
     "url": "https://zh.wikipedia.org/wiki?curid=13",  
     "title": "数学", 
     "text": "数学\n\n数学是利用符号语言研究<a href=\"%E6%95%B8%E9%87%8F\">數量</a>、<a href=\"%E6%95%B0%E5%AD%A6%E7%BB%93%E6%9E%84\">结构</a>、<a   href=\"%E5%8F%98%E5%8C%96\">变化</a>以及<a href=\"%E7%A9%BA%E9%97%B4%20%28%E6%95%B0%E5%AD%A6%29\">空间</a>等概念的一門<a href=\"%E5%AD%A6%E7%A7%91\">学科</a>，从某种角度看 屬於<a href=\"%E5%BD%A2%E5%BC%8F%E7%A7%91%E5%AD%B8\">形式科學</a>的一種。"
    }
    ```

3. Run `wiki_parse_parallel-zh.py` 抽取出內文中的連結\
處理完檔案位置：`jocelyn/wiki_page_data/linking_data`
    ```bash
    python wiki_parse_parallel-zh.py -i [input_path(output_dir_from_step_2)] -o [output_path]
    ```
    
    ```bash
    格式：
    {"id": "13",  
     "url": "https://zh.wikipedia.org/wiki?curid=13",  
     "title": "数学", 
     "text": [
        {"line": "数学是利用符号语言研究數量、结构、变化以及空间等概念的一門学科，从某种角度看屬於形式科學的一種。", 
         "links": [[11, 13, "量_(物理)"], [14, 16, "数学结构"]]
        },
        {"line": ...,
         "links": ...
        }, ...]
    }

    line:  包含 hyperlink 的句子
    links: 句中的 hyperlink，[start_idx, end_idx, connect_to_page]
             例如 line[16:34] = 數量 會連到維基頁面「量_(物理)」
    ```
    
4. Run `mention_extract.py` 得到 mention_entities-zh.json 以及 mention_count-zh.json 與 mention_count_v2-zh.json
    ```bash
    mention_entities-zh.json 格式：
    dict[mention][entity_page_id] = count
    e.g. {"川普": {527286: 78, 4109629: 29, 5329174: 1}}
    （page_id「527286」對應到「唐納·川普」，「4109629」對應到「川普」，「5329174」對應到「特朗普集團」）

    mention_count-zh.json 格式：
    dict[mention] = count
    e.g. {"川普": 108}
    ```

5. 計算片語在所有維基頁面中總共出現的 document count（統計 1-15 gram），得到 ngram_count.txt
    ```bash
    python cal_ngram_count.py > ngram_count.txt
    ```
    
6. Run `cal_linking_rate.py` 得到 mention_linking_rate-zh.json 與 mention_linking_rate_v2-zh.json
    ```bash
    格式：
    dict[mention] = linking_rate
    e.g. {"川普": 0.172}
    ```
