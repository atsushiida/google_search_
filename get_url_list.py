import re
import time
import urllib.parse
from bs4 import BeautifulSoup
import requests
import pandas as pd

def search_list(keyword):
  search_query = keyword

  r = requests.get('https://www.google.co.jp/search?hl=jp&gl=JP&num=5&q=' + search_query)
  html_soup = BeautifulSoup(r.text, 'html.parser')

  url_results = []
  for t in html_soup.select('.kCrYT > a'):
      u_result = re.sub(r'/url\?q=|&sa.*', '', t.get('href'))
      url_results.append(urllib.parse.unquote(u_result))
      time.sleep(2)

  return url_results

def get_list(target,start=0,end=-1):
    if end==-1:
        end=len(target)
    for i in range(start,end):
        if i==0:
            x=search_list(f"{target.iloc[i,0]} revenue")
            n=[li.iloc[i,0]]*len(x)
            url=x
        else:
            x=search_list(f"{target.iloc[i,0]} revenue")
            t=[li.iloc[i,0]]*len(x)
            n=n+t
            url=url+x
        if (i+1)%10==0:
            print(i+1)
        
        res=pd.DataFrame()
        res['company']=n
        res['url']=url
        res.to_csv(f'output_revenue_{start}-{i}.csv', encoding="shift-jis",errors="ignore")

if __name__ == "__main__":
    #ターゲットに合わせて成型してください。
    li=pd.read_csv("list.csv",header=None)
    #get_list関数。引数は、ターゲットのデータフレームと会社のスタート番号と終了番号
    #検索しすぎるとIPアドレスではじかれるので、小分けにして、実行の間隔を開けるor別のPCで実行
    #定常的に利用するなら、googleのsearchAPIを用いた方が早いし確実ですが、無料枠の制限はあります。
    get_list(li,0,len(li)) 
    