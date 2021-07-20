import pandas as pd
import numpy as np
import datetime
import twint
import re
import string
import plotly.express as px
import plotly.graph_objects as go
import base64
import urllib
from textblob import TextBlob
from home.models import Tweet


# git clone --depth=1 https://github.com/twintproject/twint.git

def get_twints(date1,date2,q):
    c = twint.Config()
    c.Search = q
    c.Lang = "en"
    c.Since = date1
    c.Until = date2
    c.Limit = 1
    c.Pandas = True
    return twint.run.Search(c)

def get_twints_geo(date1,date2,searched,lat,lng,km):
    c = twint.Config()
    c.Search = searched
    c.Lang = "en"
    c.Since = date1
    c.Until = date2
    c.Limit = 1
    s=lat +"," + lng + "," + km + "km"
    print(s)
    c.Geo = s
    c.Pandas = True
    return twint.run.Search(c)

def get_month(dt):
    s = dt[5:7]
    dt_obj = datetime.datetime.strptime(s,"%m")
    return dt_obj.strftime("%b")


def extract(start_date,end_date, search):
    all=Tweet.objects.filter(search=search)
    list_of_dfs = []
    search2 = search + " " + "lang:en"
    date_obj = datetime.datetime.strptime(start_date,"%Y-%m-%d")
    delta = datetime.timedelta(days=1)
    date_obj-=delta
    start_date = date_obj.strftime("%Y-%m-%d")
    while(start_date!=end_date):
        date_obj = datetime.datetime.strptime(start_date,"%Y-%m-%d")
        delta = datetime.timedelta(days=1)
        date_obj +=delta
        start_date_2 = date_obj.strftime("%Y-%m-%d")
        
        all2=all.filter(date=start_date_2).values()
        if(all2.exists()):
            df2=pd.DataFrame(all2)
            list_of_dfs.append(df2)

        else:
            get_twints(start_date,start_date_2,search2)
            df=twint.output.panda.Tweets_df[["tweet","date"]]
            df['date'] = pd.to_datetime(df['date']).dt.date
            df['clean_tweets'] = df['tweet'].apply(tweet_cleaner)
            df['clean_tweets'] = df['clean_tweets'].apply(remove_emoji)
            for i in range (0,df.shape[0]):
                Temp=Tweet(search=search,clean_tweets=df['clean_tweets'][i],date=df['date'][i])
                Temp.save()
            list_of_dfs.append(df)

        start_date= start_date_2
    
    tweet = pd.concat(list_of_dfs,ignore_index = True)
    tweet['sentiment_results'] = tweet['clean_tweets'].apply(get_sentiment)
    tweet = tweet.join(pd.json_normalize(tweet['sentiment_results']))
    tweet['sentiment'].value_counts()
    sentiment = pd.DataFrame(tweet[["polarity"]])
    sentiment = sentiment[sentiment.polarity != 0]
    t = set_time_line(tweet)  
    return (tweet, sentiment, t)

def search(start_date,end_date, search):
    (tweet,sentiment,t)=extract(start_date,end_date, search)
    return (get_plot(tweet,sentiment,t,search))

def compare(start_date,end_date, search1,search2):
    (tweet1,sentiment1,t1)=extract(start_date,end_date, search1)
    (tweet2,sentiment2,t2)=extract(start_date,end_date, search2)
    return(get_plot_comp(tweet1, tweet2, search1, search2, sentiment1, t1, sentiment2, t2))

def geolocation(start_date,end_date,search,lat,lng,km):
    list_of_dfs = []
    search2 = search + " " + "lang:en"
    date_obj = datetime.datetime.strptime(start_date,"%Y-%m-%d")
    delta = datetime.timedelta(days=1)
    date_obj-=delta
    start_date = date_obj.strftime("%Y-%m-%d")
    while(start_date!=end_date):
        date_obj = datetime.datetime.strptime(start_date,"%Y-%m-%d")
        delta = datetime.timedelta(days=1)
        date_obj +=delta
        start_date_2 = date_obj.strftime("%Y-%m-%d")
        get_twints_geo(start_date,start_date_2,search2,lat,lng,km)
        df=twint.output.panda.Tweets_df[["tweet","date"]]
        df['date'] = pd.to_datetime(df['date']).dt.date
        df['clean_tweets'] = df['tweet'].apply(tweet_cleaner)
        df['clean_tweets'] = df['clean_tweets'].apply(remove_emoji)
        list_of_dfs.append(df)
        start_date= start_date_2

    tweet = pd.concat(list_of_dfs,ignore_index = True)
    tweet['sentiment_results'] = tweet['clean_tweets'].apply(get_sentiment)
    tweet = tweet.join(pd.json_normalize(tweet['sentiment_results']))
    tweet['sentiment'].value_counts()
    sentiment = pd.DataFrame(tweet[["polarity"]])
    sentiment = sentiment[sentiment.polarity != 0]
    t = set_time_line(tweet)  
    return (get_plot(tweet,sentiment,t,search))



def tweet_cleaner(text):
    text = re.sub('@[^\s]+','',text) #remove handlers
    text = re.sub('#\S+','',text) # remove hashtags
    text = re.sub(r'RT[\s]*','',text)
    text = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','',text) #Convert www.* or https?://* to empty strings
    text = re.sub(r':w*','',text)
    text = re.sub(r'\s+',' ',text,flags = re.I) # Substituting multiple spaces with single space
    text = re.sub(r'\w*\d+\w*', '', text) # remove numbers
    text = re.sub('[%s]' % re.escape(string.punctuation), ' ', text) # remove punctuations
    text = re.sub('[^A-Za-z0-9 ]+','', text) #Remove all characters which are not alphabets, numbers or whitespaces
    return text

def remove_emoji(text):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'',text)

def get_sentiment(text):
    
    analysis = TextBlob(text)
    sentiment_polarity = analysis.sentiment.polarity
    sentiment_subjectivity = analysis.sentiment.subjectivity
    if sentiment_polarity > 0:
        sentiment_label = 'Positive'
    elif sentiment_polarity == 0:
        sentiment_label = 'Neutral'
    else: sentiment_label = 'Negative'
    result = {'polarity':sentiment_polarity, 
              'subjectivity':sentiment_subjectivity, 
              'sentiment':sentiment_label}
    return result


def set_time_line(df):
    timeline = df.groupby(['date']).agg(np.nanmean).reset_index()
    timeline['count'] = df.groupby(['date']).count().reset_index()['polarity']
    timeline = timeline[['date', 'count', 'polarity','subjectivity']]
    timeline['polarity'] = timeline['polarity'].astype(float)
    timeline['subjectivity'] = timeline['subjectivity'].astype(float)
    return timeline


def get_plot(tweet,sentiment,t,search):
    fig1=px.histogram(tweet,x='sentiment',color='sentiment',title="Tweet Count Vs Sentiment",template="plotly_dark")
    fig2=px.histogram(sentiment,x='polarity',range_x=[-1,1],title='Tweet Count Vs Polarity',template="plotly_dark")
    fig2.update_traces(xbins=dict(start=-1,end=1,size=0.25))
    fig2.update_layout(bargap=0.02)
    fig3 = px.bar(t, x='date', y='count', color='polarity',title = search,template="plotly_dark")
    # fig4 = go.Figure(go.Scatter(x=t.date, y=t.polarity,mode='lines+markers', name=search))
    # fig4.update_layout(title="Polarity Vs Date",template="plotly_dark")
    fig4 = px.line(t, x="date", y="polarity", title='Polarity Vs Date',template="plotly_dark")
    fig4.update_yaxes(range=[-1,1])
    fig5 = px.bar(t, x='date', y='count', color='subjectivity',title = search,template="plotly_dark")
    # fig6 = go.Figure(go.Scatter(x=t.date, y=t.polarity,mode='lines+markers', name=search))
    # fig6.update_layout(title="Subjectivity Vs Date",template="plotly_dark")
    fig6 = px.line(t, x="date", y="subjectivity", title='Subjectivity Vs Date',template="plotly_dark")
    fig6.update_yaxes(range=[0,1])
    return (get_graph(fig1),get_graph(fig2),get_graph(fig3),get_graph(fig4),get_graph(fig5),get_graph(fig6))

def get_plot_comp(tweet1,tweet2,search1,search2,sentiment1,t1,sentiment2,t2):
    fig1 = go.Figure()
    fig1.add_trace(go.Histogram(x=tweet1.sentiment,name= search1))
    fig1.add_trace(go.Histogram(x=tweet2.sentiment,name=search2))
    fig1.update_layout(title_text='Tweet Count Vs Sentiment',xaxis_title_text='Sentiment Label',
        yaxis_title_text='Tweet count',barmode='group',template="plotly_dark")
    
    fig2 = go.Figure()
    fig2.add_trace(go.Histogram(x=sentiment1.polarity,name=search1,marker_color='#000080'))
    fig2.add_trace(go.Histogram(x=sentiment2.polarity,name=search2))
    fig2.update_xaxes(range=[-1,1])
    fig2.update_traces(xbins=dict(start=-1,end=1,size=0.25))
    fig2.update_layout(title_text='Tweet Count Vs Polarity',xaxis_title_text='Polarity score',
        yaxis_title_text='Tweet count',barmode='group',template="plotly_dark")

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=t1.date, y=t1.polarity,mode='lines+markers', name=search1))
    fig3.add_trace(go.Scatter(x=t2.date, y=t2.polarity,mode='lines+markers', name=search2))
    fig3.update_yaxes(range=[-1,1])
    fig3.update_layout(title_text='Polarity vs Date',xaxis_title_text='Date',yaxis_title_text='Polarity',template="plotly_dark")

    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=t1.date, y=t1.subjectivity,mode='lines+markers', name=search1))
    fig4.add_trace(go.Scatter(x=t2.date, y=t2.subjectivity,mode='lines+markers', name=search2))
    fig4.update_yaxes(range=[0,1])
    fig4.update_layout(title_text='Subjectivity vs Date',xaxis_title_text='Date',yaxis_title_text='Subjectivity',template="plotly_dark")

    return (get_graph(fig1),get_graph(fig2),get_graph(fig3),get_graph(fig4))

def get_graph(fig):
    image_png=fig.to_image(format='png')
    graph = base64.b64encode(image_png).decode()
    uri = 'data:image/png;base64,' + urllib.parse.quote(graph)
    return uri
