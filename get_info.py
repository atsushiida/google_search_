import requests
import time
from bs4 import BeautifulSoup
import pandas as pd
import re
import multiprocessing

'''
もし、実行時間が長いURLがあって実行が止まる場合には、追加してください
ただし、マルチプロセスなので、メモリーの利用料がおおくなります。
※対症療法的に該当のURLだけ除外して再実行した方が効率いいかもです。
def function_with_timeout(url):
    result_queue = multiprocessing.Queue()

    process = multiprocessing.Process(target=lambda q: q.put(get_text(url)), args=(result_queue,))
    process.start()
    process.join(15)

    if process.is_alive():
        process.terminate()  # タイムアウトした場合はプロセスを強制終了
        return 0
    else:
        return result_queue.get()
'''


def get_text(url):
  try:
    response = requests.get(url)
    time.sleep(1)
    soup = BeautifulSoup(response.content, 'html.parser')
    text=soup.get_text()

    return text
  except:
    return 0

def extract_contexts(text, context_length=20):
    contexts=[]

    keyword="revenue"
    x=[m.span() for m in re.finditer(keyword, text)]
    for i in x:
        if i[0]-20<0:
            start=0
        else:
            start=i[0]-20
        contexts.append(text[start:i[1]+20])

    return contexts
    

def get_info(target):
    contexts=[]
    url=[]
    comp=[]
    pdf_list_company=[]
    pdf_list_url=[]
    for i in range(len(target)):
        if i%10==0:
            print(f"{i+1}回目")
        
        #拡張子がpdfのものを弾く
        if target.iloc[i,1][-4:]==".pdf":
            pdf_list_company.append(target.iloc[i,0])
            pdf_list_url.append(target.iloc[i,1])
            continue
        
        #引っかかったものなどをはじく
        if target.iloc[i,1][12:20]=="zoominfo":
            continue
        if target.iloc[i,1][12:20]=='nasdaq.c':
            continue
        
        text=get_text(target.iloc[i,1])
        
        #アクセス拒否
        if text==0:
            continue
        
        new_contexts=extract_contexts(text)
        contexts=contexts+new_contexts
        new_url=[target.iloc[i,1]]*len(new_contexts)
        url=url+new_url
        new_comp=[target.iloc[i,0]]*len(new_contexts)
        comp=comp+new_comp
        
        #保険
        if i%300==0:
            res=pd.DataFrame()
            res['company']=comp
            res['url']=url
            res['contexts']=contexts
            res.to_csv('output_revenue.csv', encoding="shift-jis",errors="ignore")
    
            pdf=pd.DataFrame()
            pdf['company']=pdf_list_company
            pdf['url']=pdf_list_url
            pdf.to_csv('pdf_list.csv', encoding="shift-jis",errors="ignore")
        
    res=pd.DataFrame()
    res['company']=comp
    res['url']=url
    res['contexts']=contexts
    res.to_csv('output_revenue.csv', encoding="shift-jis",errors="ignore")

    pdf=pd.DataFrame()
    pdf['company']=pdf_list_company
    pdf['url']=pdf_list_url
    pdf.to_csv('pdf_list.csv', encoding="shift-jis",errors="ignore")
         

if __name__ == "__main__":
    #ターゲットに合わせて変えてもらえれば。0行目にcompany,1行目にurlを持つDataFrame
    li=pd.read_csv("url_list.csv")
    #非ロボット認証とかにより読み取れないと0の値が帰ってきます。
    get_info(li)
    