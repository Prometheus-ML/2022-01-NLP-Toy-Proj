import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk import sent_tokenize, word_tokenize
import lyricsgenius
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd

# Function to return song lyrics


def get_lyrics(title, artist):
    try:
        return genius.search_song(title, artist).lyrics
    except:
        return 'not found'

# Function to return sentiment score of each song


def get_lyric_sentiment(lyrics):
    sentiment = sid_obj.polarity_scores(lyrics)
    return sentiment


''' 원본 파일에서 가수, 제목을 통해서 가사 + 감정 점수 불러오기'''

genius = lyricsgenius.Genius(
    "DuO42xKa4Ts70InLe_Y_strEpeL_CxowzCtXyAMaiNlbAOVOTfFpt2q5FdP4lo_U")
sid_obj = SentimentIntensityAnalyzer()

lyrics_sentiment_dataset = pd.read_csv(
    './lyrics_sentiment_dataset/tcc_ceds_music.csv', encoding='cp949')
print(lyrics_sentiment_dataset.keys())
lyrics_sentiment_dataset = lyrics_sentiment_dataset.drop(
    ['Unnamed: 0', 'genre',
     'lyrics', 'len', 'dating', 'violence', 'world/life', 'night/time',
     'shake the audience', 'family/gospel', 'romantic', 'communication',
     'obscene', 'music', 'movement/places', 'light/visual perceptions',
     'family/spiritual', 'like/girls', 'sadness', 'feelings', 'danceability',
     'loudness', 'acousticness', 'instrumentalness', 'valence', 'energy',
     'topic', 'age'], axis=1)

lyrics_sentiment_dataset.drop_duplicates(subset='track_name', inplace=True)
lyrics_sentiment_dataset.reset_index(drop=True)
lyrics_sentiment_dataset_3 = lyrics_sentiment_dataset.iloc[9460:14190, 0:]

# 노래 가사 불러오기
lyics1 = lyrics_sentiment_dataset_3.apply(lambda row: get_lyrics(
    row['track_name'], row['artist_name']), axis=1)
lyrics_sentiment_dataset_3['lyrics'] = lyics1
print(lyrics_sentiment_dataset_3.shape)
# not found 제거
lyrics_sentiment_dataset_3 = lyrics_sentiment_dataset_3.drop(
    lyrics_sentiment_dataset_3[lyrics_sentiment_dataset_3['lyrics'] == 'not found'].index)

# Use get_lyric_sentiment to get sentiment score for all the song lyrics
sentiment = lyrics_sentiment_dataset_3.apply(
    lambda row: get_lyric_sentiment(row['lyrics']), axis=1)

for i in lyrics_sentiment_dataset_3.index.tolist():
    lyrics_sentiment_dataset_3.loc[i, 'neg_sentiment'] = sentiment[i]['neg']
    lyrics_sentiment_dataset_3.loc[i, 'neu_sentiment'] = sentiment[i]['neu']
    lyrics_sentiment_dataset_3.loc[i, 'pos_sentiment'] = sentiment[i]['pos']
    lyrics_sentiment_dataset_3.loc[i,
                                   'com_sentiment'] = sentiment[i]['compound']

lyrics_sentiment_dataset_3.to_csv(
    "lyrics_sentiment_dataset_3.csv", index=False)


''' 감정 점수 중 0점이 하나라도 있거나, 가수, 제목에 매칭되지 않는 가사 지우기 '''

'''
df.shape : (2394, 8)
filtered_df.shape : (2265, 8)
점수 중에 하나라도 0점이 있는 데이터: 129개
filtered_df.count() : Null Zero
filtered_df에서의 lyrics 평균길이: 6099

drop_df = len_df.drop(len_df.index[0:30], inplace=False)
filtered_df에서 내림차순 정렬 기준 앞에서부터 30개를 버리면 lyrics 평균길이 : 2508
filtered_df에서 내림차순 정렬 기준 앞에서부터 50개를 버리면 lyrics 평균길이 : 1908
'''

df = pd.read_csv('./lyrics_sentiment_dataset/lyrics_sentiment_dataset_3.csv')

# 하나라도 0점이면 out
filtered_df = df[(df['neg_sentiment'] != 0.000) & (df['neu_sentiment'] != 0.000) & (
    df['pos_sentiment'] != 0.000) & (df['com_sentiment'] != 0.000)]

# lyrics_len column 추가 -> 길이순 대로 정렬 -> 너무 긴거는 지우기
get_len = []
for i in filtered_df.index.tolist():
    length = len(filtered_df.loc[i, 'lyrics'])
    filtered_df.loc[i, 'lyrics_len'] = length

# lyrics_len 내림차순 정렬
filtered_df.sort_values('lyrics_len', ascending=False, inplace=True)

'''
# 어디까지는 지워야하는지 확인 -> filtered_df 기준 인덱스 90까지 지워야됨
delete = filtered_df.iloc[0:91, 0:]
print(delete)

# 해당 가수의 가사 찾기
li = filtered_df[(filtered_df['artist_name'] == 'the brian jonestown massacre') & (filtered_df['track_name'] == 'fucker')]['lyrics'].tolist()
print(li)
'''

fin_filtered_df = filtered_df.iloc[91:, 0:]

# 제일 마지막은 들어본 결과 가사가 없음 => del
short_lyrics = fin_filtered_df[(fin_filtered_df['artist_name'] == 'blues traveler') & (
    fin_filtered_df['track_name'] == 'the good, the bad and the ugly')].index

fin_filtered_df = fin_filtered_df.drop(short_lyrics)
fin_filtered_df.to_csv("lyrics_sentiment_dataset_3.csv", index=False)

''' 데이터 전처리 '''

new_stopwords = stopwords.words('english')
add_stopwords = ["[", "]", "(", ")", ",", "lyrics",
                 "chorus", "!", "?", "``", "oh", "ha", "ah", "-", "yo", "yeah", "uh", "uhh", ":"]
new_stopwords.extend(add_stopwords)
nltk.download('omw-1.4')
nltk.download('wordnet')


def tokenize(str_lyrics):
    split_lyrics = " ".join(str_lyrics.splitlines())
    sentences = sent_tokenize(split_lyrics)
    init_words = []
    for sentence in sentences:
        word_tokens = word_tokenize(sentence)
        for word in word_tokens:
            word = word.lower()
            init_words.append(word)

    return init_words


def remove_not_alpa(words_list):
    for word in words_list:
        if (("'" in word) or ("lyrics" in word) or (not word.isalpha()) or (len(word) == 1)):
            words_list.remove(word)

    return words_list


def remove_stopwords(words_list):
    filtered_words = []
    for word in words_list:
        if word not in new_stopwords:
            filtered_words.append(word)

    return filtered_words


def lemmatizer(tokenzied_list):
    lemmatized_list = []
    for word in tokenzied_list:
        word = lemma.lemmatize(word)
        lemmatized_list.append(word)
    return lemmatized_list


def get_lyric_sentiment(lyrics):
    sentiment = sid_obj.polarity_scores(lyrics)
    return sentiment


lemma = WordNetLemmatizer()
sid_obj = SentimentIntensityAnalyzer()

df = pd.read_csv('./lyrics_sentiment_dataset/lyrics_sentiment_dataset_3.csv')


for i in df.index.tolist():
    lyrics = df.loc[i, 'lyrics']
    # tokenize
    init_words_list = tokenize(lyrics)
    init_words_list = list(set(init_words_list))
    # remove not alpha
    alpha_words_list = remove_not_alpa(init_words_list)
    # remove stopword
    filtered_word_list = remove_stopwords(alpha_words_list)
    # lemmatizer
    lemmatized_list = lemmatizer(filtered_word_list)
    lemmatized_list = list(set(lemmatized_list))
    final_list = remove_not_alpa(lemmatized_list)
    final_str = " ".join(final_list)

    # print("['neg': {0:.3f} 'neu': {1:.3f} 'pos': {2:.3f} 'com': {3:.3f}]".format(df.loc[i, "neg_sentiment"], df.loc[i, "neu_sentiment"],
    #       df.loc[i, "pos_sentiment"], df.loc[i, "com_sentiment"]))

    # sentiment = get_lyric_sentiment(final_str)
    # print(sentiment)

    df.loc[i, 'lyrics'] = final_str

df.to_csv("lyrics_sentiment_dataset_3_tokenized.csv", index=False)

''' JOIN '''
df_1 = pd.read_csv(
    './join_dataset/lyrics_sentiment_dataset_1.csv', index_col=False)
df_2 = pd.read_csv(
    './join_dataset/lyrics_sentiment_dataset_2.csv', encoding='utf-8', index_col=False)
df_3 = pd.read_csv(
    './join_dataset/lyrics_sentiment_dataset_3.csv', index_col=False)
df_4 = pd.read_csv(
    './join_dataset/lyrics_sentiment_dataset_4.csv', index_col=False)
df_5 = pd.read_csv(
    './join_dataset/lyrics_sentiment_dataset_5.csv', index_col=False)
df_6 = pd.read_csv(
    './join_dataset/lyrics_sentiment_dataset_6.csv', index_col=False)


final_df = pd.concat([df_1, df_2, df_3, df_4, df_5, df_6], ignore_index=True)
final_df.reset_index()

print(final_df)
final_df.to_csv("lyrics_sentiment_dataset_final.csv", index=False)
