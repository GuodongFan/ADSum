import re
#from src.process_data.process_base import convert_nwords, vocab
#from src.utils.social_tokenizer import SocialTokenizer
from tqdm import tqdm
#tokenise = SocialTokenizer(lowercase=True, debug=False, verbose=False).tokenize
#from text_processor import Processor

from cleantext.sklearn import CleanTransformer

cleaner = CleanTransformer(
    fix_unicode=True,               # fix various unicode errors
    to_ascii=True,                  # transliterate to closest ASCII representation
    lower=True,                     # lowercase text
    no_line_breaks=True,           # fully strip line breaks as opposed to only normalizing them
    no_urls=False,                  # replace all URLs with a special token
    no_emails=False,                # replace all email addresses with a special token
    no_phone_numbers=False,         # replace all phone numbers with a special token
    no_numbers=False,               # replace all numbers with a special token
    no_digits=False,                # replace all digits with a special token
    no_currency_symbols=False,      # replace all currency symbols with a special token
    no_punct=False,                 # remove punctuations
    replace_with_punct="",          # instead of removing punctuations you may replace them
    replace_with_url="<URL>",
    replace_with_email="<EMAIL>",
    replace_with_phone_number="<PHONE>",
    replace_with_number="<NUMBER>",
    replace_with_digit="0",
    replace_with_currency_symbol="<CUR>",
    lang="en"                       # set to 'de' for German special handling
)

def clean_issue(result):
    issue_id = result.string[result.regs[0][0]:result.regs[0][1]].split('/')[-1].strip()
    fields = issue_id.split('#')
    issue_id = fields[0]

    try:
        int(issue_id)
    except:
        return None

    return issue_id

with open('./data/message/content.annotation.txt', 'r') as file:
    lines = file.readlines()

dialogs_list = []
issue_list = []
create_time_list = []

developer_dialog = {}
temp = []
create_time = ''
has_issue = False
count = 0
refer_github_count = 0
for line in tqdm(lines, total=len(lines)):

    result = re.search('github.com[^\s]*TypeScript/issues[^\s]+[0-9]*\s', line, flags=0)
    #result2 = re.search('#[0-9]*\s', line, flags=0)
    if result != None :
        #print(line)
        issue_id = clean_issue(result)
        if issue_id != None:
            has_issue = True
        else:
            has_issue = False

    if line == '--------------------------------------------------------------------------------------------------\n':
        if has_issue:
            refer_github_count += 1
            sentence = ''
            for utter in temp:
                create_time = utter.split('\t')[0]
                utter = utter.split('\t')[-1]
                sentence += utter + ' . '
            dialogs_list.append(sentence)
            issue_list.append(issue_id)
            create_time_list.append(create_time)
        else:
            sentence = ''
            for utter in temp:
                create_time = utter.split('\t')[0]
                utter = utter.split('\t')[-1]
                sentence += utter + ' . '
            dialogs_list.append(sentence)
            issue_list.append('')
            create_time_list.append(create_time)
        count += 1
        temp = []
        has_issue = False
    else:
        temp.append(line)


print('refer github count', refer_github_count)
print('count ', count)
#processor = Processor()
with open('./data/dialog.txt', 'w', encoding='utf-8') as file:
    for idx, dialog in tqdm(enumerate(dialogs_list), total=len(dialogs_list)):
        #dialog = processor.forward(dialog)
        dialog = cleaner.transform([dialog])
        file.write(issue_list[idx] + '\t' + create_time_list[idx] + '\t' + dialog[0] + '\n')

