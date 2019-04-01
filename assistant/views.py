# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from redis import Redis
from rq import Queue


# Create your views here.
from assistant.async_tasks import store_data

@csrf_exempt
def store_values(request):
    q = Queue(connection=Redis())
    q.enqueue(store_data,request.POST)
    return JsonResponse({'status':200})



@csrf_exempt
def get_response(request):
    query = request.POST.get('update_list_0')
    import re
    import requests
    from bs4 import BeautifulSoup
    h = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36"}
    page = requests.get("https://www.google.com/search?q=" + str(query))
    page1 = requests.get("https://www.google.com/search?q=" + str(query),headers=h)
    soup1 = BeautifulSoup(page1.content)
    soup = BeautifulSoup(page.content)
    feedback_box = soup1.find("div", {"class": "g knavi obcontainer mod"})
    description_box = soup1.find("div", {"class": "PZPZlf hb8SAc kno-fb-ctx"})
    other_box = soup1.find("div", {"class": "cUezCb xpd O9g5cc uUPGi"})
    web_box = soup1.find("div",{"class": "kp-blk c2xzTb Wnoohf OJXvsb"})
    info_box = soup1.find('div',{"class":"imso-loa imso_mh__mh-ed"})
    if feedback_box:
        summary = text_from_html(str(feedback_box))
        summary = summary.replace('Feedback', '')
    elif description_box:
        summary = text_from_html(str(description_box))
        summary = summary.replace('Feedback', '')
        summary = summary.replace('Description', '')
        summary = summary.replace('Wikipedia', '')
    elif web_box:
        summary = text_from_html(str(web_box))
        summary = summary.replace('Feedback', '')
    elif other_box:
        summary = text_from_html(str(other_box))
        summary = summary.replace('Feedback', '')
    elif info_box:
        summary = text_from_html(str(info_box))
        summary = summary.replace('Feedback', '')
    else:
        links = soup.findAll("a")
        for i, link in enumerate(soup.find_all("a", href=re.compile("(?<=/url\?q=)(htt.*://.*)"))):
            result_url = re.split(":(?=http)", link["href"].replace("/url?q=", ""))[0].split("&sa=")[0]
            break
        page = requests.get(result_url).text
        soup = BeautifulSoup(page, 'html.parser')
        name_box = soup.findAll('p')
        text = ""
        sentences = []
        for p in name_box:
            name = p.text.strip()
            string = name + "."
            text = text + string
            sentences.append(string)
        summary = summary_content(text)
    return HttpResponse(str(summary))




def text_from_html(body):
    import re
    cleanr = re.compile('<.*?>')
    body = re.sub(r'[^\x00-\x7F]+', ' ', body)
    cleantext = re.sub(cleanr, '', body)
    return cleantext

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




def speech_present(request):
    if request.GET.get('query').contains("guys"):
        return HttpResponse("SILENCEEEE")
    elif request.GET.get('query').contains("boring"):
        return HttpResponse(" I guess you are. They are sleeping i think.")
    elif request.GET.get('query').contains("humor"):
        return HttpResponse("Humor level reduced. HA HA HA")
    elif request.GET.get('query').contains("inspiration"):
        return HttpResponse("CHITTI. THE ROBOT")
    elif request.GET.get('query').contains("Why is it so?"):
        return HttpResponse("That one is the best of next 20 centuries")
    elif request.GET.get('query').contains("everything"):
        return HttpResponse("Dont Lie. I cant do all that. Well I can do this..  Work for you. ")


