import django
django.setup()
import nltk


from assistant.models import NotificationHolder

def store_data(value_strings):
    import django
    django.setup()
    from assistant.models import Top5Apps, User, PhoneUsage, Least5Apps, NotificationHolder
    from datetime import datetime, timedelta
    import requests
    try:
        values = str(value_strings['update_list_0']).split(',')[4]
        try:
            user = User.objects.get(unique_value=str(value_strings['update_list_0']).split(',')[4])
        except:
            user = User()
        user.username = str(value_strings['update_list_0']).split(',')[4]
        user.unique_value = user.username
        user.first_name = ""
        user.email = "nasty123@gmail.com"
        user.save()
        for id in range(0, len(value_strings)):
            update_id = 'update_list_' + str(id)
            complete_string = value_strings[update_id]
            split_values = str(complete_string).split(',')
            request_url = "https://play.google.com/store/apps/details?id=" + str(split_values[5])
            resp = requests.get(request_url).text
            if "Not Found" in resp and split_values[0] != "Camera":
                pass
            else:
                last_used = datetime.strptime(split_values[1], '%b %d  %Y %I:%M:%S %p')
                hours_used = split_values[2]
                percentage = (split_values[3].split('%')[0])
                hour_min_sec = hours_used.split(':')
                del hour_min_sec[-1]
                if len(hour_min_sec) == 1:
                    if split_values[0] == "Camera":
                        if float(hour_min_sec[0]) > float(30):
                            hour_min_sec = float(99)
                        else:
                            hour_min_sec = float(hour_min_sec[0])
                    else:
                        hour_min_sec = float(0)
                elif len(hour_min_sec) == 2:
                    if split_values[0] == "Camera":
                        hour_min_sec = float(99)
                    else:
                        hour_min_sec = float(hour_min_sec[0])*60 + float(hour_min_sec[1])
                elif len(hour_min_sec) == 3:
                    hour_min_sec = float(hour_min_sec[0]) * 60 * 60 + float(hour_min_sec[1])* 60 + float(hour_min_sec[2])
                elif len(hour_min_sec) == 0:
                    hour_min_sec = float(0)
                if split_values[0] == "Camera":
                    category = "Photography"
                else:
                    category = resp.split("genre")[1].split('"  class="')[1].split('">')[1].split("</a>")[0]

                phone_usage = PhoneUsage.objects.filter(application_name=split_values[0],
                                                    hours_used=hour_min_sec, percentage=percentage, user=user,
                                                    app_category=category)

                if phone_usage.count() >= 1:
                    pass
                else:
                    phone_usage = PhoneUsage.objects.create(application_name=split_values[0], last_used=last_used,
                                                        hours_used=hour_min_sec, percentage=percentage, user=user,
                                                        app_category=category)
    except:
        pass


# resp.split("genre")[1].split('"  class="')[1].split('">')[1].split("</a>")[0]

def find_top_5_apps():
    from assistant.models import User,PhoneUsage,Top5Apps

    #
    import random
    import time
    from datetime import datetime, timedelta
    from collections import Counter
    import django
    import requests
    from redis import Redis
    from rq import Queue
    from itertools import chain
    for user in User.objects.all():
        apps = PhoneUsage.objects.filter(last_used__date=datetime.now().date(),user_id = user.id).exclude(
            application_name='Camera').order_by('-hours_used')
        json_value = []
        application_names = []
        for app in apps:
            if app.application_name not in application_names:
                json_value.append(
                    {"app_name": app.application_name, "hours_used": app.hours_used, "category": app.app_category})
                application_names.append(app.application_name)
        if len(json_value):
            Top5Apps.objects.create(applications=str(json_value), user=user)


def find_least_5_apps():
    from assistant.models import User,PhoneUsage,Least5Apps
    from datetime import datetime
    for user in User.objects.all():
        apps = PhoneUsage.objects.filter(last_used__date=datetime.now().date(), user_id = user.id).exclude(
            application_name='Camera').order_by('hours_used')
        json_value = []
        application_names = []
        for app in apps:
            if app.application_name not in application_names:
                json_value.append(
                    {"app_name": app.application_name, "hours_used": app.hours_used, "category": app.app_category})
                application_names.append(app.application_name)
        Least5Apps.objects.create(applications=str(json_value), user=user)


def gather_camera_data():
    from assistant.models import PhoneUsage
    from datetime import datetime
    app = PhoneUsage.objects.filter(last_used=datetime.now().date(), application_name="Camera").order_by('-hours_used')[
        0]
    if app.hours_used > float(0):
        return True
    else:
        return False


def run_analysis():
    find_top_5_apps()
    find_least_5_apps()


def get_the_5(unique_value):
    from datetime import datetime, timedelta
    import random
    from assistant.models import User,Top5Apps,Least5Apps,PhoneUsage
    user = User.objects.get(unique_value=unique_value)
    if random.choice([1, 0]):
        apps = Top5Apps.objects.filter(user=user, created_at__date=datetime.now().date()).order_by('-created_at')[0]
        applications = eval(apps.applications)
        string_value = "Your favourite apps are \n"
        for i,app in enumerate(applications):
            if i == 5:
                break
            string_value = string_value + str(app['app_name']) + "-(" + str(app['category']) + ")" + "\n"
        return string_value
    else:
        apps = Least5Apps.objects.filter(user=user, created_at__date=datetime.now().date()).order_by('-created_at')[0]
        applications = eval(apps.applications)
        if random.choice([1, 0]):
            string_value = "Your least favourites apps are \n"
            for i,app in enumerate(applications):
                if i == 5:
                    break
                string_value = string_value + str(app['app_name']) + "-(" + str(app['category']) + ")" + "\n"
            return string_value
        else:
            from collections import Counter
            count_array = list(range(3, 8))
            day_value = random.choice(count_array)
            string_value = "Started Disliking these apps? \n"
            string_value = string_value + "You have stopped these apps using frequently.. \n"
            apps = PhoneUsage.objects.filter(user=user,
                                             last_used__date__gte=datetime.now().date() - timedelta(day_value),
                                             last_used__date__lte=datetime.now().date()).values_list('application_name',
                                                                                                     flat=True)

            apps = Counter(apps)
            apps = apps.most_common()[:-5 - 1:-1]
            string_value = string_value + str(apps[0][0]).encode("utf-8") + "\n"
            string_value = string_value + str(apps[1][0]).encode("utf-8") + "\n"
            string_value = string_value + str(apps[2][0]).encode("utf-8")
            return string_value


def get_5_info(unique_value):
    from itertools import chain
    from datetime import datetime
    import random
    from assistant.models import User,Top5Apps,Least5Apps
    user = User.objects.get(unique_value=unique_value)
    top_apps = Top5Apps.objects.filter(user=user, created_at__date=datetime.now().date()).order_by('-created_at')[0]
    least_apps = Least5Apps.objects.filter(user=user, created_at__date=datetime.now().date()).order_by('-created_at')[0]
    final_apps = [app_name['app_name'] for app_name in eval(top_apps.applications)]
    final_app = random.choice(final_apps).encode('UTF-8')
    import requests
    from bs4 import BeautifulSoup
    page = requests.get("https://www.google.com/search?q=news+ "+str(final_app)+" app")
    soup = BeautifulSoup(page.content)
    import re
    links = soup.findAll("a")
    for i,link in enumerate(soup.find_all("a", href=re.compile("(?<=/url\?q=)(htt.*://.*)"))):
        url = re.split(":(?=http)", link["href"].replace("/url?q=", ""))[0].split("&sa=")[0]
        if str(final_app) not in  url.split("//")[-1].split("/")[0]:
            result_url = re.split(":(?=http)", link["href"].replace("/url?q=", ""))[0].split("&sa=")[0]
            break
    page = requests.get(result_url).text
    soup = BeautifulSoup(page,'html.parser')
    header_tag = soup.find('h1')
    return_string = "Some Newer Info about one of your APP "+str(final_app)+"\n"+"- "+str(text_from_html(str(header_tag)))
    return_string = return_string + "\n\n"
    name_box = soup.find_all('p')
    text = ""
    sentences = []
    for p in name_box:
        name = p.text.strip()
        string = name + "."
        text = text + string
        sentences.append(string)
    summary = summary_content(text)
    return_string = return_string + summary.strip()
    summary = text_from_html(summary)
    return return_string



def get_suggestion_5(unique_value):
    from assistant.models import User, Top5Apps, PhoneUsage
    from datetime import datetime
    user = User.objects.get(unique_value = unique_value)
    categories = PhoneUsage.objects.filter(user=user).values('app_category')
    total_category = []
    for category in categories:
        total_category.append(category['app_category'])
    top_apps = Top5Apps.objects.filter(user=user, created_at__date=datetime.now().date()).order_by('-created_at')[0]
    top_app_categories = [app_name['app_name'] for app_name in eval(top_apps.applications)]
    suggestion_categories = list(set(total_category).symmetric_difference(top_app_categories))
    return_string = "Find Balance for your life dude..."
    return_string = return_string + "\n"
    return_string = return_string + "You have been using %s"%(",".join(top_app_categories[:5])) + "\n\n"
    return_string = return_string + "Try to use these apps too %s"%(",".join(suggestion_categories[:5]))
    return return_string

def response_generator():
    from assistant.models import *
    import random
    functions = ['get_the_5', 'get_5_info', 'get_suggestion_5']
    for user in User.objects.all():
        function_name = random.choice(functions)
        if function_name == "get_the_5":
            return_string = get_the_5(user.unique_value)
        elif function_name == "get_5_info":
            return_string = get_5_info(user.unique_value)
        elif function_name == "get_suggestion_5":
            return_string = get_suggestion_5(user.unique_value)
        else:
            return_string = ""
        exec('common_string = %s'%function_name)
        final_string = "Hey there...." + return_string
        NotificationHolder.objects.create(user=user, notification_content=final_string)

def get_ne_vals(query):
    # importing the libraries needed in this section
    import nltk
    from nltk.tokenize import RegexpTokenizer

    # defining the text
    text = query

    # instantiating the tokenizer object. By passing r'\w+' to the RegexpTokenizer
    # I am selecting groups of single words, discarding the punctuation
    tokenizer = RegexpTokenizer(r'\w+')

    # getting the tokens
    tokens = tokenizer.tokenize(text)

    # importing the library needed in this section
    from nltk.corpus import stopwords

    # assigning the english stop-words to the sw list
    sw = stopwords.words('english')

    # assigning the non stop-words contained in the tokens list
    # to a new list named clean_tokens through a list comprehension
    clean_tokens = [token for token in tokens if token not in sw]

    # importing the library needed in this section
    from nltk.stem import WordNetLemmatizer

    # instantiating the lemmaztizer object
    lemmatizer = WordNetLemmatizer()

    # lemmatizing each word through a list comprehension
    [lemmatizer.lemmatize(token) for token in clean_tokens]

    # importing the library needed in this section
    from nltk.stem.porter import PorterStemmer

    # instantiating the stemmer object
    pstemmer = PorterStemmer()

    # stemming each word through a list comprehension
    [pstemmer.stem(token) for token in clean_tokens]


    return " ".join(clean_tokens)

def similarities_finder(unique_value):
    from assistant.models import User, Query
    user = User.objects.get(unique_value = unique_value)
    from datetime import datetime, timedelta
    from collections import Counter
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    three_days_back = datetime.today() - timedelta(days = 3)
    today = datetime.today()
    queries = Query.objects.filter(user=user)
    query_texts = []
    for query in queries:
        query_texts.append(query.text)
    for query in query_texts:
        for q in query_texts:
            if query_texts != q:
                values = get_cosine_sim(query,q)
                if values[0][1] > 0.5:
                    if len(query) > len(q):
                        final_query = query
                    else:
                        final_query = q
                    named_entitie_string = get_ne_vals(final_query)
                    print(named_entitie_string)
                    import re
                    import requests
                    from bs4 import BeautifulSoup
                    page = requests.get("https://www.google.com/search?q=" + str(named_entitie_string))
                    soup = BeautifulSoup(page.content)
                    links = soup.findAll("a")
                    for i, link in enumerate(soup.find_all("a", href=re.compile("(?<=/url\?q=)(htt.*://.*)"))):
                        result_url = re.split(":(?=http)", link["href"].replace("/url?q=", ""))[0].split("&sa=")[0]
                        break
                    page = requests.get(result_url).text
                    soup = BeautifulSoup(page, 'html.parser')
                    header_tag = soup.find('h1')
                    header_tag = text_from_html(str(header_tag))
                    name_box = soup.findAll('p')
                    text = ""
                    sentences = []
                    for p in name_box:
                        name = p.text.strip()
                        string = name + "."
                        text = text + string
                        sentences.append(string)
                    summary = summary_content(text)
                    return_string = "The things you have been searching a lot --> " + header_tag + "\n\n" + summary
                    objs = NotificationHolder.objects.filter(user=user, notification_content=return_string)
                    if not objs.count():
                        print("CAME IN --> %s"%(return_string))
                        NotificationHolder.objects.create(user=user, notification_content=return_string)


def get_cosine_sim(*strs):
    from collections import Counter
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    vectors = [t for t in get_vectors(*strs)]
    return cosine_similarity(vectors)

def get_vectors(*strs):
    from collections import Counter
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    text = [t for t in strs]
    vectorizer = CountVectorizer(text)
    vectorizer.fit(text)
    return vectorizer.transform(text).toarray()


def summary_content(text):

    import argparse
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    from string import punctuation
    from nltk.probability import FreqDist
    from heapq import nlargest
    from collections import defaultdict
    sentence_tokens, word_tokens = tokenize_content(text)
    sentence_ranks = score_tokens(word_tokens, sentence_tokens)
    summary = summarize(sentence_ranks, sentence_tokens, 1)

    return summary.encode('UTF-8')





def sanitize_input(data):
    import argparse
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    from string import punctuation
    from nltk.probability import FreqDist
    from heapq import nlargest
    from collections import defaultdict
    """
    
    Currently just a whitespace remover. More thought will have to be given with how
    to handle sanitzation and encoding in a way that most text files can be successfully
    parsed
    """
    replace = {
        ord('\f'): ' ',
        ord('\t'): ' ',
        ord('\n'): ' ',
        ord('\r'): None
    }

    return str(data).translate(replace)


def tokenize_content(content):
    import argparse
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    from string import punctuation
    from nltk.probability import FreqDist
    from heapq import nlargest
    from collections import defaultdict
    """
    Accept the content and produce a list of tokenized sentences,
    a list of tokenized words, and then a list of the tokenized words
    with stop words built from NLTK corpus and Python string class filtred out.
    """
    stop_words = set(stopwords.words('english') + list(punctuation))
    words = word_tokenize(content.lower())

    return [
        sent_tokenize(content),
        [word for word in words if word not in stop_words]
    ]


def score_tokens(filterd_words, sentence_tokens):
    import argparse
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    from string import punctuation
    from nltk.probability import FreqDist
    from heapq import nlargest
    from collections import defaultdict
    """
    Builds a frequency map based on the filtered list of words and
    uses this to produce a map of each sentence and its total score
    """
    word_freq = FreqDist(filterd_words)

    ranking = defaultdict(int)

    for i, sentence in enumerate(sentence_tokens):
        for word in word_tokenize(sentence.lower()):
            if word in word_freq:
                ranking[i] += word_freq[word]

    return ranking


def summarize(ranks, sentences, length):
    import argparse
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    from string import punctuation
    from nltk.probability import FreqDist
    from heapq import nlargest
    from collections import defaultdict
    """
    Utilizes a ranking map produced by score_token to extract
    the highest ranking sentences in order after converting from
    array to string.
    """
    if int(length) > len(sentences):
        print("Error, more sentences requested than available. Use --l (--length) flag to adjust.")
        exit()

    indexes = nlargest(length, ranks, key=ranks.get)
    final_sentences = [sentences[j] for j in sorted(indexes)]
    return ' '.join(final_sentences)



def text_from_html(body):
    import re
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', body)
    return cleantext
