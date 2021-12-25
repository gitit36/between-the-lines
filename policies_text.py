import requests
import pymysql
pymysql.install_as_MySQLdb()
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.schema import CreateTable
from bs4 import BeautifulSoup

def extract_policy(df_company_nameanddomain, N):
    policies = {}
    print("here")
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

# connect to sql database
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

policies = extract_policy(df_company_nameanddomain, 10)