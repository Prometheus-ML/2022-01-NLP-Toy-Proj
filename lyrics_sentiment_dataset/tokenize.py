import pandas as pd
from nltk import sent_tokenize
import tensorflow.keras as tf
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re

new_stopwords = stopwords.words('english')
add_stopwords = ["[", "]", "(", ")", ",", "lyrics",
                 "chorus", "!", "?", "``", "oh", "ha", "ah", "-", "yo", "yeah", "uh", "uhh", ":"]
new_stopwords.extend(add_stopwords)
nltk.download('omw-1.4')
nltk.download('wordnet')
text_to_word_sequence = tf.keras.preprocessing.text.text_to_word_sequence

# sentence = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]','',sentence)
# import re
# regex = "\[[^\]]*\]|\s-\s.*"
# for i in range(len(df["lyrics"])):
#     df["lyrics"][i] = re.sub(regex,'',df["lyrics"][i])


def tokenize(str_lyrics):
    regex = "\[[^\]]*\]|\s-\s.*"
    split_lyrics = " ".join(str_lyrics.splitlines())
    re.sub(regex, ' ', split_lyrics)
    print("tokenize", split_lyrics)
    sentences = sent_tokenize(split_lyrics)
    init_words = []
    for sentence in sentences:
        word_tokens = text_to_word_sequence(sentence)
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
    # for i in range(10):
    lyrics = df.loc[i, 'lyrics']
    # tokenize
    init_words_list = tokenize(lyrics)
    init_words_list = list(init_words_list)
    # remove not alpha
    alpha_words_list = remove_not_alpa(init_words_list)
    # remove stopword
    filtered_word_list = remove_stopwords(alpha_words_list)
    # lemmatizer
    lemmatized_list = lemmatizer(filtered_word_list)
    lemmatized_list = list(lemmatized_list)
    final_list = remove_not_alpa(lemmatized_list)
    final_str = " ".join(final_list)

    # sentiment = get_lyric_sentiment(final_str)
    # print("\n%d번 째 인덱스" % i)
    # df.loc[i, 'neg_sentiment'] = sentiment['neg']
    # df.loc[i, 'neu_sentiment'] = sentiment['neu']
    # df.loc[i, 'pos_sentiment'] = sentiment['pos']
    # df.loc[i,
    #        'com_sentiment'] = sentiment['compound']

    df.loc[i, 'lyrics'] = final_str

df.to_csv("lyrics_sentiment_dataset_tokenized_temp.csv", index=False)
