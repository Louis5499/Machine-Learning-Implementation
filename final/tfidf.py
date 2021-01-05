import os
import json
import math, re
import requests
from fractions import Fraction
from collections import defaultdict, Counter
from ckiptagger import data_utils, construct_dictionary, WS, POS, NER
from datetime import datetime
import csv

# ckip-Tagger installation
# Put data in Backend first~
ws = WS("./data")
pos = POS("./data")
ner = NER("./data")

os.chdir(os.getcwd())

stopwords = []
all_words_dict = {}
forum_dict = {}
D_dict = {}

with open('stopwords.txt', 'r') as f:
    stopwords = f.read().split('\n')
with open('all_words_dict.json', 'r') as f:
    all_words_dict = json.loads(f.read())
with open('forum_dict.json', 'r') as f:
    forum_dict = json.loads(f.read())
with open('D_dict.json', 'r') as f:
    D_dict = json.loads(f.read())
stopwords.extend(['.', '/', ':', '-', ' ', '(', ')', '⋯', '=', '～', '妳', '會', '裡', '說', '沒'])
totalD = 16810539


def tfidf(allContent, forum, type):
    tfidf_list = []
    ready_input = []

    # In some cases, we will encounter blank line, so we need to check whether length of a sentence > 0
    ready_input = [ sentence for content in allContent for sentence in content.split('\n') if len(sentence) > 0 ]
    
    # Break words
    # [['我', ' ', '全', '家', '同事'], ...]
    content_tok = ws(ready_input)

    # Turn the break word into counter
    # {'麥當勞': 6, '全': 5, '家': 5, '打工': 3, ...}
    contents_words = Counter([w for sentence in content_tok for w in sentence if w not in stopwords])
    contents_words = {key: item for key, item in sorted(contents_words.items(), key=lambda x: x[1], reverse=True)}

    N = len([w for sentence in content_tok for w in sentence])

    # Calculate TF-IDF (and PF)
    # PF aims to prevent some words are more important and frequent under certain forum, we need to renormalize it.
    for word, count in contents_words.items():
        if word not in all_words_dict.keys() or word not in D_dict.keys() or word in stopwords:   continue
        tf = count / N
        idf = math.log((totalD / D_dict[word])) # **
        if forum_dict.get(forum):
            if forum_dict[forum].get(word): pf = forum_dict[forum][word] / all_words_dict[word]
            else: pf = 1
        else: pf = 1
        tfidf_list.append([word, tf*idf, tf*idf*pf, tf, idf, pf])
    tfidf_list.sort(key = lambda s: s[type], reverse=True)

    # Find bi-word combinations (「今天」「要去」, 「要去」「郊遊」)
    for word in tfidf_list:
        bi_list = []
        for sentence in content_tok:
            if word[0] in sentence:
                idx = sentence.index(word[0])
                if idx+1 < len(sentence) and sentence[idx+1] not in stopwords:
                    bi_list.append(sentence[idx] + sentence[idx+1])
                if idx > 0 and sentence[idx-1] not in stopwords:
                    bi_list.append(sentence[idx-1] + sentence[idx])
                if idx-2 >= 0 and sentence[idx-2] not in stopwords and sentence[idx-1] not in stopwords:
                    bi_list.append(sentence[idx-2] + sentence[idx-1] + sentence[idx])
                if idx+2 < len(sentence) and sentence[idx+1] not in stopwords and sentence[idx+2] not in stopwords:
                    bi_list.append(sentence[idx] + sentence[idx+1] + sentence[idx+2])
                if idx > 0 and idx+1 < len(sentence) and sentence[idx-1] not in stopwords and sentence[idx+1] not in stopwords:
                    bi_list.append(sentence[idx-1] + sentence[idx] + sentence[idx+1])
        bi_count = Counter(bi_list).most_common(5)
        bi_count = [word[0] for word in bi_count]
        word.append(bi_count)
    return tfidf_list

requests.packages.urllib3.disable_warnings()
cookie = '__auc=6dc9ccdd17143b13780f7882a84; __gads=ID=4a1a6db174d6b764:T=1585978677:S=ALNI_MYhw2OFmwPMXG1d6oDGLtOSaoaUBw; _gid=GA1.2.1722273152.1586581391; dcard=eyJ0b2tlbiI6bnVsbCwiX2V4cGlyZSI6MTU4OTE3NTA2NjgzNCwiX21heEFnZSI6MjU5MjAwMDAwMH0=; dcard.sig=V23CgwwWlQwERJ_4oClxCfx3eJo; dcsrd=u5srf5XIcfZBSFOWoTUlB9A1; dcsrd.sig=ILdWwvOz55JmB6jAgNThu9LMRwA; __asc=7bc8218c171681f2a3a6d824441; _gat=1; amplitude_id_bfb03c251442ee56c07f655053aba20fdcard.tw=eyJkZXZpY2VJZCI6ImU0Njc2NzQ5LTQyZWUtNDFhNS04ZWE4LTA5N2JkMzhhOWZkMlIiLCJ1c2VySWQiOiI1OTk2MDgxIiwib3B0T3V0IjpmYWxzZSwic2Vzc2lvbklkIjoxNTg2NTg5ODA1ODU3LCJsYXN0RXZlbnRUaW1lIjoxNTg2NTg5ODIxMTk2LCJldmVudElkIjozNiwiaWRlbnRpZnlJZCI6MjIsInNlcXVlbmNlTnVtYmVyIjo1OH0=; __cfduid=d9fff663f1a6dd3065426909f15752fcb1586589920; _ga=GA1.1.2128013235.1585978618; _ga_C3J49QFLW7=GS1.1.1586589804.10.1.1586589846.0'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
    # 'cookie': cookie,
    # 'X-CSRF-Token': token,
    'Connection':'close'
}
tfidf_post_keys = ['title']
tfidf_comment_keys = ['content']
dcard_api = 'https://www.dcard.tw/service/api/v2/'
retries = 3

extractedCols = ['title', 'content', 'excerpt', 'anonymousSchool', 'anonymousDepartment', 'createdAt', 'commentCount', 'likeCount', 'tags', 'topics', 'withNickname', 'forumAlias', 'school', 'department', 'gender', 'reactions']

def remove_emoji(string):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                        #    u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)

def clean(string):
    string = re.sub(r'^https?:\/\/.*[\r\n]*', '', string, flags=re.MULTILINE)
    # string = re.sub('\W+',' ', string)
    string = remove_emoji(string)
    return string

def url_to_json(url):
    for i in range(retries):
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == requests.codes.ok:
            json_file = response.json()
            response.close()
            return json_file
        elif response.status_code == 404:
            return None
        else:
            print('status error:',  response.status_code)
            continue
            # response.raise_for_status()
        response.close()
    print('EXCEED RETRIES: ', url)

def get_comment_json(post_id):
    url = dcard_api + 'posts/' + str(post_id) + '/comments?popular=true' # Only specify hot top 3 comments
    comments = []
    _comments = url_to_json(url)  # a list of dict
    for _comment in _comments:
        if 'content' in _comment.keys():    comments.append(clean(_comment['content']))
    return comments

def get_post_json(post_id):
    url = dcard_api + 'posts/' + str(post_id)
    _post = url_to_json(url) # dict
    if _post is None:
        return None
    post = {}
    for extractedCol in extractedCols:
        if extractedCol in _post:
            if extractedCol == 'content': post[extractedCol] = clean(_post[extractedCol])
            else: post[extractedCol] = _post[extractedCol]
    # post['url'] = 'https://www.dcard.tw/f/' + post['forumAlias'] + '/p/' + str(post_id)
    return post

def transformKeywordDataToReadableData(keyword_list, isPf):
    outputDict = {}
    colList = ['word', 'tf*idf', 'tf*idf*pf', 'tf', 'idf', 'pf', 'biword']
    colList = [ "keyword_" + colName for colName in colList ]
    if (isPf): colList = [ "pf_" + colName for colName in colList ]
    for idx, valItems in enumerate(keyword_list):
        countColList = [ colName + f'_{idx+1}' for colName in colList ]
        for innerIdx, item in enumerate(valItems):
            outputDict[countColList[innerIdx]] = item
    return outputDict

def breakWords(allContent):
    ready_input = [ sentence for content in allContent for sentence in content.split('\n') if len(sentence) > 0 ]
    return ws(ready_input)

def keywords_byID(ids):
    data_list = []
    for id in ids:
        data = get_post_json(id)
        comments = get_comment_json(id)
        if data == []:  return data_list
        if data == None: continue
        print(f"Searching for: {id} {data['title']}")
        keyword_content = transformKeywordDataToReadableData(tfidf([data['content']], data['forumAlias'], 1)[:3], 0)
        keyword_content_pf = transformKeywordDataToReadableData(tfidf([data['content']], data['forumAlias'], 2)[:3], 1)
        data['break_words'] = breakWords([data['content']])
        data['comments'] = comments
        data = { **data, **keyword_content, **keyword_content_pf }
        data_list.append(data)
    return data_list


def get_forum_posts(forum_name, post_num = 20, popular='false', query=None):

  MAXIMUN_POSTS = 100
  roundIdx = 0
  last_post_id = None
  post_result_list = []
  tidied_post_id_arr = []
  if popular == 'true' or query is not None:
    print(f"Fetching all of the popular data")
    limits = min(MAXIMUN_POSTS, post_num)
    if query is not None:
        sortType = 'create' if popular == 'false' else 'like'
        url = dcard_api + f'search/posts?limit={post_num}&query={query}&field=topics&sort={sortType}'
    else: url = dcard_api + 'forums/' + forum_name + f'/posts?limit={limits}&popular=true' # Dcard could only fetch 61 popular data, so in the response the amount of posts could be fewer than the the desired amount
    post_arr = url_to_json(url)
    if post_arr is None:
        return None
    for per_post in post_arr:
        tidied_post_id_arr.append(per_post['id'])
    post_result_list = keywords_byID(tidied_post_id_arr)
    for item in post_result_list:
        item['popular'] = 'true'
  else:
    while (post_num > 0):
        limits = min(MAXIMUN_POSTS, post_num)
        print(f"Round {roundIdx}: the limit of post is {limits}     Last Post Id: {last_post_id}     Your Request: Popular={popular}")

        # Call API
        # We can get article list(without content) by calling forum API
        # If we need to get the content, we should call getPost API
        url = dcard_api + 'forums/' + forum_name + f'/posts?limit={limits}&popular={popular}'
        if roundIdx > 0: url += f'&before={last_post_id}'

        post_arr = url_to_json(url)
        tidied_post_id_arr = []

        # Fetch posts' ids
        if post_arr is None:
            return None
        for per_post in post_arr:
            tidied_post_id_arr.append(per_post['id'])
            last_post_id = per_post['id']

        print(f"Round {roundIdx}: the number of post is {len(tidied_post_id_arr)}")
        post_result_list += keywords_byID(tidied_post_id_arr)
        post_num -= limits
        roundIdx += 1
    for item in post_result_list:
        item['popular'] = 'true'


  query = '' if query is None else query
  get_all_col_nam = ['title','content','excerpt','anonymousSchool','anonymousDepartment','createdAt','commentCount','likeCount','tags','topics','withNickname','forumAlias','school','department','gender','reactions', 'popular', 'keyword_word_1','keyword_tf*idf_1','keyword_tf*idf*pf_1','keyword_tf_1','keyword_idf_1','keyword_pf_1','keyword_biword_1','keyword_word_2','keyword_tf*idf_2','keyword_tf*idf*pf_2','keyword_tf_2','keyword_idf_2','keyword_pf_2','keyword_biword_2','keyword_word_3','keyword_tf*idf_3','keyword_tf*idf*pf_3','keyword_tf_3','keyword_idf_3','keyword_pf_3','keyword_biword_3','pf_keyword_word_1','pf_keyword_tf*idf_1','pf_keyword_tf*idf*pf_1','pf_keyword_tf_1','pf_keyword_idf_1','pf_keyword_pf_1','pf_keyword_biword_1','pf_keyword_word_2','pf_keyword_tf*idf_2','pf_keyword_tf*idf*pf_2','pf_keyword_tf_2','pf_keyword_idf_2','pf_keyword_pf_2','pf_keyword_biword_2','pf_keyword_word_3','pf_keyword_tf*idf_3','pf_keyword_tf*idf*pf_3','pf_keyword_tf_3','pf_keyword_idf_3','pf_keyword_pf_3','pf_keyword_biword_3', 'break_words', 'comments']
  file_name = f"result-for-{forum_name}-{query}-{int(datetime.now().timestamp())}.csv"
  with open(file_name, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(get_all_col_nam)
    for idx, valRowDict in enumerate(post_result_list):
        output = []
        for colName in get_all_col_nam:
            if colName in valRowDict: output += [ valRowDict[colName] ]
            else: output += [ '' ]
        writer.writerow(output)

  print(f"Exported as {file_name}!\n")
  return post_result_list

print("-----")
print("Please follow the instruction to enter your command")
print("(If you just type the wrong command and want to skip, please enter 'skip')")
print("(If you want to shut down the program, please enter 'exit')")
command = ""
state_correct = False
tag_correct = False
forum_correct = False
popular_correct = False
limits_correct = False
shouldShutDown = False
shouldSkip = False
while(shouldShutDown == False):
    state_name = ""
    forum_name = ""
    tag_name = None
    is_popular = ""
    limit_num = ""

    state_correct = False
    tag_correct = False
    forum_correct = False
    popular_correct = False
    limits_correct = False

    while(state_correct == False):
        print("please indicate you want to search 1) forum or 2) tags (Enter '1' or '2'): ")
        search_state = input(">> ")
        if (search_state == 'exit'):
            shouldShutDown = True
            break
        if (search_state == 'skip'):
            shouldSkip = True
            break
        if (search_state != '1' and search_state != '2'):
            print("Plase only input '1' & '2' without quotation mark.")
            continue
        state_name = search_state  
        state_correct = True   

    if (search_state == '1'):
        # Choose forum name
        while(forum_correct == False):
            print("please give a forum name you want to search: ")
            search_forum = input(">> ")
            if (search_forum == 'exit'):
                shouldShutDown = True
                break
            if (search_forum == 'skip'):
                shouldSkip = True
                break
            forum_name = search_forum
            forum_correct = True
    else:
        # Choose tags name
        while(tag_correct == False):
            print("please give a tag name you want to search: ")
            search_tag = input(">> ")
            if (search_tag == 'exit'):
                shouldShutDown = True
                break
            if (search_tag == 'skip'):
                shouldSkip = True
                break
            tag_name = search_tag
            tag_correct = True
    
    # Choose popular(熱門) or not
    while(shouldShutDown == False and shouldSkip == False and popular_correct == False):
        print("please specify you want popular posts or not (true or false): ")
        search_popular = input(">> ")
        if (search_popular == 'exit'):
            shouldShutDown = True
            break
        if (search_popular == 'skip'):
            shouldSkip = True
            break

        if (search_popular != 'true' and search_popular != 'false'):
            print("Plase only input 'true' & 'false' with lower case.")
            continue
        is_popular = search_popular
        popular_correct = True

    # Choose limits
    while(shouldShutDown == False and shouldSkip == False and limits_correct == False):
        print("please specify the amount of posts you want to take (number): ")
        search_limits = input(">> ")
        if (search_limits == 'exit'):
            shouldShutDown = True
            break
        if (search_limits == 'skip'):
            shouldSkip = True
            break
        limit_num = int(search_limits)
        limits_correct = True

    if shouldShutDown:
        print("Bye Bye~~")
        break
    if shouldSkip:
        shouldSkip = False
        continue
    else:
        if (limit_num > 61 and is_popular == 'true'): print(f"[Warning!!!!] Dcard will only respond 61 popular posts, so you will not receive {limit_num} posts.")
        get_forum_posts(forum_name, limit_num, is_popular, tag_name)