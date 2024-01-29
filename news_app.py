# Necessary Library Imports:
import feedparser
import streamlit as st
import psycopg2
from datetime import datetime
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Initialize NLTK
nltk.download('stopwords')
nltk.download('punkt')

st.title("WELCOME TO NEWS APP")

st.markdown(
    """
    <style>
    .reportview-container {
        background: url("https://images.unsplash.com/photo-1487147264018-f937fba0c817")
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Connect to PostgreSQL database
conn = psycopg2.connect(
    host="localhost",
    dbname="news_db",
    user="postgres",
    password="postsql",
    port=5432,
    sslmode="disable"
)
cur = conn.cursor()

# Create the table if not exists
cur.execute("""
   CREATE TABLE IF NOT EXISTS news_articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    link VARCHAR NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR,
    image_url VARCHAR,
    published_at TIMESTAMP DEFAULT current_timestamp
);

""")
conn.commit()

# NLTK Text Classification
def classify_news(text):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text)
    words = [word.lower() for word in words if word.isalnum()]
    words = [word for word in words if word not in stop_words]

    # For simplicity, let's use a basic keyword-based classification
    positive_keywords = ['happy', 'uplifting', 'positive']
    disaster_keywords = ['disaster', 'earthquake', 'hurricane', 'flood']
    political_keywords = ['protest', 'terrorism', 'political unrest', 'riot']

    for keyword_list, category in zip(
        [positive_keywords, disaster_keywords, political_keywords],
        ['Positive/Uplifting', 'Natural Disasters', 'Terrorism/Protest/Political Unrest/Riot']
    ):
        if any(keyword in words for keyword in keyword_list):
            return category

    return 'Others'

def rss_feed_url(url):
    """given an RSS feed url, extract its entities"""
    rss_feed_contents = feedparser.parse(url)
    news = rss_feed_contents.entries

    for idx, curr_news in enumerate(news):
        id = str(idx + 1)
        title = curr_news.get('title', 'No title available')
        actual_link = curr_news.get('link', 'No link available')

        # Check if 'summary' key exists
        if 'summary' in curr_news:
            content = curr_news['summary'].split('<')[0] if curr_news['summary'].split('<')[0] != '' else 'No article summary available, click on the link to read'
        else:
            content = 'No article summary available, click on the link to read'

        # Display image if available
        if 'media_content' in curr_news and len(curr_news['media_content']) > 0:
            image_url = curr_news['media_content'][0]['url']
            st.image(image_url, caption=f"Image for {title}", use_column_width=True)
        elif 'media_thumbnail' in curr_news and len(curr_news['media_thumbnail']) > 0:
            image_url = curr_news['media_thumbnail'][0]['url']
            st.image(image_url, caption=f"Image for {title}", use_column_width=True)
        else:
            # Display a placeholder image or skip image display
            st.image('https://icon-library.com/images/no-picture-available-icon/no-picture-available-icon-1.jpg', caption=f"Image not available", use_column_width=True)

        st.header(f"\n({id}) {title}")
        st.write(f"{content}")
        st.write(f"Read full story here: {actual_link}")
        st.write("---------------------------------------------------------")

        if idx > 10:
            break


# Our RSS news feeds look-up table
dict_rss_news_feeds = {
    'Top Stories': "http://rss.cnn.com/rss/cnn_topstories.rss",
    'Feeds': "http://qz.com/feed",
    'Politics': "http://feeds.foxnews.com/foxnews/politics",
    'New Shour World': "http://feeds.feedburner.com/NewshourWorld",
    'India And Worlds News': "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml"
}

# Category-wise buttons
selected_category = st.radio("Select Category", list(dict_rss_news_feeds.keys()))

# Fetching news summary for the selected category
st.title(f"{selected_category}: \n")
rss_feed_url(dict_rss_news_feeds[selected_category])
