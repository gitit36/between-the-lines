from flask import Flask, render_template, request
import requests
import textstat
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import io
import base64
from sqlalchemy import create_engine
from sqlalchemy.schema import CreateTable
import numpy as np
import matplotlib
from matplotlib.patches import Rectangle
import matplotlib.colors as mcolors
from io import BytesIO
from wordcloud import WordCloud, STOPWORDS
import matplotlib.colors as mcolors
from collections import Counter
import requests
import pprint
import re
from gensim import corpora
import gensim
import pickle
import spacy
spacy.load("en_core_web_sm")
from spacy.lang.en import English
import nltk
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# nltk.download()
import nltk
# nltk.download('wordnet')
from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer
# nltk.download('stopwords')
en_stop = set(nltk.corpus.stopwords.words('english'))
import random
parser = English()
matplotlib.use('Agg')
import pymysql
pymysql.install_as_MySQLdb()
import pandas as pd
import json

app = Flask(__name__)

#function to extract text
def extract_text(url):
  resp = requests.get(url, timeout=10)
  soup = BeautifulSoup(resp.text, 'html.parser')
  txt = " ".join([p.text for p in soup.find_all("p")])
  txt = txt.replace("\n", "")
  txt = ' '.join(txt.split())
  
  return txt


def get_raw_fig(plt):
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    raw_fig = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return raw_fig

#function to summarize 
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
model1 = AutoModelForSeq2SeqLM.from_pretrained("t5-base")
tokenizer = AutoTokenizer.from_pretrained("t5-base")
def summarization(text):
  inputs = tokenizer("summarize: " + text, return_tensors="pt",truncation=True,max_length=512)
  outputs = model1.generate(inputs["input_ids"],length_penalty=2.0, num_beams=4, early_stopping=True,max_length=200, min_length=80)
  result=tokenizer.decode(outputs[0])
  result = result.strip("<pad>")
  result = result.strip("</s>")
  result=result.capitalize()
  return result

# function to analyze similarity
from sentence_transformers import SentenceTransformer, util
import variables
model = SentenceTransformer('sentence-transformers/paraphrase-MiniLM-L6-v2')
best = variables.best
good = variables.good
average = variables.average
bad = variables.bad

def similarity(text,best,good,average,bad):
    scores=[]
    # encode sentences to get their embeddings
    embedding1 = model.encode(text, convert_to_tensor=True)
    embedding_best = model.encode(best, convert_to_tensor=True)
    embedding_good = model.encode(good, convert_to_tensor=True)
    embedding_bad = model.encode(bad, convert_to_tensor=True)
    embedding_average = model.encode(average, convert_to_tensor=True)
    # compute similarity scores of two embeddings
    cosine_scores1 = util.pytorch_cos_sim(embedding1, embedding_best)
    scores.append(cosine_scores1.item())
    cosine_scores2 = util.pytorch_cos_sim(embedding1, embedding_good)
    scores.append(cosine_scores2.item())
    cosine_scores3 = util.pytorch_cos_sim(embedding1, embedding_average)
    scores.append(cosine_scores3.item())
    cosine_scores4 = util.pytorch_cos_sim(embedding1, embedding_bad)
    scores.append(cosine_scores4.item())

    if max(scores)== scores[0]:
        return("According to our model, this privacy policy most closely matches some of the bad privacy policies in terms of semantics. \nOn a scale of 1 to 5, it ranks 1." )
    if max(scores)== scores[1]:
        return("According to our model, this privacy policy most closely matches average privacy policies in terms of semantics. \nOn a scale of 1 to 5, it ranks 2." )
    if max(scores)== scores[2]:
        return("According to our model, this privacy policy most closely matches good privacy policies in terms of semantics. \nOn a scale of 1 to 5, it ranks 3." )
    if max(scores)== scores[3]:
        return("According to our model, this privacy policy most closely matches best privacy policies in terms of semantics. \nOn a scale of 1 to 5, it ranks 5." )
    

# all the code below are for topic modeling

##### FUNCTION THAT RENDERS A TOPIC MODELLING MODEL ####
def render_model(num_topics, text_data):
    dictionary = corpora.Dictionary(text_data)
    corpus = [dictionary.doc2bow(text) for text in text_data]
    
    pickle.dump(corpus, open('corpus.pkl', 'wb'))
    dictionary.save('dictionary.gensim')
    
    dictionary = gensim.corpora.Dictionary.load('dictionary.gensim')
    corpus = pickle.load(open('corpus.pkl', 'rb'))

    lda = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                          id2word=dictionary,
                                          num_topics=num_topics, 
                                          random_state=100,
                                          update_every=1,
                                          chunksize=10,
                                          passes=10,
                                          alpha='symmetric',
                                          iterations=100,
                                          per_word_topics=True)
    return lda



def processText(text):
    endpoint_watson = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/3d4468af-8ad0-4453-9535-72f90c9eb5c4/v1/analyze"
    params = {'version': '2021-08-01',}

    #header = type of content
    headers = {'Content-Type': 'application/json',}

    watson_options = {
        "text": text,
        "features":
        {"summarization": {"limit": 2}}
    }
    username = "apikey"
    password = "-OwF1ab-S1ekafX-ps_dSnaFE_Q0eYBf9wtTdcVV2x0B"

    resp = requests.post(endpoint_watson,
        #since we are using post we give data tp APi backednd to analyze --> make the server do smthn intercatinve wiht the data
        data=json.dumps(watson_options),
        headers=headers,
        params=params,
        auth=(username, password)
    )
    return resp.json()



def extract_policy(df_company_nameanddomain, N):
    policies = {}
    for url in df_company_nameanddomain['0'][:N]:
        try:
            resp = requests.get(url, timeout=10)
            
        except:
            continue

        soup = BeautifulSoup(resp.text,'html.parser')

        txt = " ".join([p.text for p in soup.find_all("p")])
        txt = txt.replace("\n", "")
        txt = ' '.join(txt.split())

        if "Sign in with a different account" in txt:
            continue

        elif "Sorry" in txt:
            continue
            
        elif len(txt) > 100:
            policies[url] = txt
    return policies



# returns policies dict as a dataframe with Flesch Kincaid Readability Scores
# argument 'policies' is a dictionary
def FK_score(policies):
    
    # transform dictionary to datafram
    policies_df = pd.DataFrame.from_dict(policies,orient='index',columns=['policy'])
    
    # reset index
    policies_df.reset_index(inplace=True)

    # rename index column to url
    policies_df.rename(columns={"index": "url"},inplace=True)

    # make a column for flesch-kincaid scores
    policies_df['flesch_kincaid_score'] = np.nan

    # calculate flesch-kincaid for each policy extracted from the urls
    for i in range(len(policies_df['policy'])):
        policies_df.loc[i,'flesch_kincaid_score'] = textstat.flesch_kincaid_grade(str(policies_df.loc[i,'policy']))
    policies_df['policy'] = policies_df['policy'].str.encode('ascii', 'ignore').str.decode('ascii')
    

    return policies_df


# 'policies' would be the dataframe produced by function extract_policy()
def summarize_policies(policies):
    for i in policies:
        try:
            summ = processText(policies[i])
            summ = summ['summarization']['text']
            policies[i] = summ
        except:
            continue
    return policies


def tokenize(text):
    lda_tokens = []
    tokens = parser(text)
    for token in tokens:
        if token.orth_.isspace():
            continue
        elif token.like_url:
            lda_tokens.append('URL')
        elif token.orth_.startswith('@'):
            lda_tokens.append('SCREEN_NAME')
        else:
            lda_tokens.append(token.lower_)
    return lda_tokens


def get_lemma(word):
    lemma = wn.morphy(word)
    if lemma is None:
        return word
    else:
        return lemma
    
    
def get_lemma2(word):
    return WordNetLemmatizer().lemmatize(word)


def prepare_text_for_lda(text):
    tokens = tokenize(text)
    tokens = [token for token in tokens if len(token) > 4]
    tokens = [token for token in tokens if token not in en_stop]
    tokens = [get_lemma(token) for token in tokens]
    return tokens


def process_text(policies):
    text_data = []
    for i in policies:
        try:
            tokens = prepare_text_for_lda(policies[i])
            text_data.append(tokens)
        except:
            pass
    return text_data


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/summarization.html")
def summarize_index():
    return render_template("summarization.html")


@app.route("/summarization.html", methods=['POST'])
def summarize():
    url = request.form['url']
    pre_txt = extract_text(url)
    txt = summarization(pre_txt)
    return render_template("summarization.html", txt = txt)


@app.route("/readability.html")
def readability_index():
    return render_template("readability.html")


@app.route("/readability.html", methods=['POST'])
def check_readability():
    url = request.form['url']
    txt = extract_text(url)
    score = textstat.flesch_kincaid_grade(txt)
    if score<13:
        result="Grade Level is: "+str(score)+". The readability of this privacy policy is within school level."
    if 13<score<22:
        result="Grade Level is: "+str(score)+". The readability of this privacy policy is within university level."
    if 22<score<30:
        result="Grade Level is: "+str(score)+". The readability of this privacy policy is within professional level."
    if score>30:
        result="Grade Level is: "+str(score)+". The readability of this privacy policy is within an advanced level."
    return render_template("readability.html", score = result)

@app.route("/similarity.html")
def similarity_index():
    return render_template("similarity.html")

@app.route("/similarity.html", methods=['POST'])
def check_similarity():
    url = request.form['url']
    pre_txt = extract_text(url)
    result = similarity(pre_txt,best,good,average,bad)
    return render_template("similarity.html", result = result)

@app.route("/topic_modeling.html")
def topic_modeling_index():
    return render_template("topic_modeling.html", first_visit = True)

import policies_text
@app.route("/topic_modeling.html", methods=['POST'])
def generate_topic_modeling():
    num_topics = int(request.form['url'])
    print(num_topics)
    # connect to sql database
    '''
    conn = 'mysql://{user}:{password}@{host}:{port}/{db}?charset=utf8'.format(
        user='byteme', 
        password='26I2omTQtSM=', 
        host = 'jsedocc7.scrc.nyu.edu', 
        port=3306, 
        db='ByteMe',
        encoding = 'utf-8'
    )
    engine = create_engine(conn)

    query = "select * from privacyPage_urls"
    df_company_nameanddomain = pd.read_sql(query, con=engine)
    print(df_company_nameanddomain)
    policies = extract_policy(df_company_nameanddomain, 100)
    '''
    all_policies = policies_text.policies
    policies = summarize_policies(all_policies)
    print(2)
    text_data = process_text(policies)
    print(3)
    lda = render_model(num_topics, text_data)
    print(4)
    topic_wordcloud = BytesIO()

    cols = [color for name, color in mcolors.TABLEAU_COLORS.items()]

    cloud = WordCloud(stopwords=en_stop,
                      background_color='white',
                      width=2500,
                      height=1800,
                      max_words=10,
                      colormap='tab10',
                      color_func=lambda *args, **kwargs: cols[i],
                      prefer_horizontal=1.0)

    topics = lda.show_topics(formatted=False)
    
    row_num = 2 + num_topics % 2

    fig, axes = plt.subplots(2, row_num, figsize=(10,10), sharex=True, sharey=True)

    for i, ax in enumerate(axes.flatten()):
        fig.add_subplot(ax)
        topic_words = dict(topics[i][1])
        cloud.generate_from_frequencies(topic_words, max_font_size=300)
        plt.gca().imshow(cloud)
        plt.gca().set_title('Topic ' + str(i), fontdict=dict(size=16))
        plt.gca().axis('off')


    plt.subplots_adjust(wspace=0, hspace=0)
    plt.axis('off')
    plt.margins(x=0, y=0)
    plt.tight_layout()
    
    plt.savefig(topic_wordcloud, format='png')
    plt.close()
    topic_wordcloud.seek(0)
    plot_url = base64.b64encode(topic_wordcloud.getvalue()).decode('utf8')
    return render_template('topic_modeling.html', plot_url = plot_url, first_visit = False)

@app.route("/data_leaks.html")
def data_leaks_index():
    import glob
    image_paths = glob.glob("./static/images/*")
    image_paths.sort()
    return render_template("data_leaks.html", image_paths = image_paths)

if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)