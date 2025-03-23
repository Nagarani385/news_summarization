import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import BartForConditionalGeneration, BartTokenizer
from gtts import gTTS
from googletrans import Translator
from utils import save_report, save_final_report

# Initialize necessary tools
analyzer = SentimentIntensityAnalyzer()
translator = Translator()

# Define local path for the pre-downloaded BART models
MODEL_PATH = "models/bart-large-cnn"
try:
    model = BartForConditionalGeneration.from_pretrained(MODEL_PATH)
    tokenizer = BartTokenizer.from_pretrained(MODEL_PATH)
except Exception as e:
    print(f"Error loading model: {e}")
    model, tokenizer = None, None

HEADERS = {'User-Agent': 'Mozilla/5.0'}


def extract_articles(company_name):
    """Extracts articles related to the specified company from BBC News.

    Args:
        company_name (str): The name of the company to search for.

    Returns:
        list: A list of dictionaries containing article details (title, summary, URL, date_time, sentiment).
    """
    try:
        search_url = f"https://www.bbc.co.uk/search?q={company_name}&filter=news"
        response = requests.get(search_url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Failed to retrieve the page, status code: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []

        for link in soup.find_all('a', href=True):
            if '/news/' in link['href'] and len(articles) < 10:
                full_url = urljoin("https://www.bbc.co.uk", link['href'])
                title, summary, date_time = extract_article_info(full_url)
                if title and summary and date_time:
                    sentiment = analyze_sentiment(summary)
                    articles.append({
                        'title': title,
                        'summary': summary,
                        'url': full_url,
                        'date_time': date_time,
                        'sentiment': sentiment
                    })
        return articles
    except Exception as e:
        print(f"Error extracting articles: {e}")
        return []


def extract_article_info(url):
    """Extracts title, summary, and date/time from a BBC News article.

    Args:
        url (str): The URL of the article.

    Returns:
        tuple: A tuple containing (title, summary, date_time) of the article.
    """
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            return None, None, None

        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "No Title Found"
        time_tag = soup.find('time', {'data-testid': 'timestamp'})
        date_time = time_tag.get('datetime') if time_tag else "No datetime found."
        paragraphs = soup.find_all('p')
        summary = " ".join(p.get_text(strip=True) for p in paragraphs[:3]) if paragraphs else "No Summary Available"
        return title, summary, date_time
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return None, None, None


def analyze_sentiment(text):
    """Analyzes sentiment using VADER and returns the sentiment label.

    Args:
        text (str): The text to analyze.

    Returns:
        str: The sentiment label ('Positive', 'Negative', or 'Neutral').
    """
    try:
        sentiment_score = analyzer.polarity_scores(text)["compound"]
        return "Positive" if sentiment_score >= 0.05 else "Negative" if sentiment_score <= -0.05 else "Neutral"
    except Exception as e:
        print(f"Error analyzing sentiment: {e}")
        return "Neutral"


def generate_combined_summary(articles):
    """Generates a summarized version of all article summaries.

    Args:
        articles (list): A list of article dictionaries containing summaries.

    Returns:
        str: A summarized version of the combined articles.
    """
    try:
        combined_text = " ".join(article['summary'] for article in articles)
        inputs = tokenizer.encode(combined_text, return_tensors="pt", max_length=1024, truncation=True)
        summary_ids = model.generate(inputs, max_length=200, min_length=80, do_sample=False)
        return tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    except Exception as e:
        print(f"Error generating summary: {e}")
        return "Summary generation failed."


def translate_to_hindi(text1, text2):
    """Translates English text to Hindi.

    Args:
        text1 (str): The first text to translate.
        text2 (str): The second text to translate.

    Returns:
        tuple: Translated texts in Hindi.
    """
    try:
        translation1 = translator.translate(text1, src="en", dest="hi").text
        translation2 = translator.translate(text2, src="en", dest="hi").text
        return translation1, translation2
    except Exception as e:
        print(f"Error translating text: {e}")
        return text1, text2


def text_to_speech(text, filename="summary_audio.mp3", lang="hi"):
    """Converts text to speech and saves as an MP3 file.

    Args:
        text (str): The text to convert to speech.
        filename (str, optional): The filename to save the audio file. Defaults to "summary_audio.mp3".
        lang (str, optional): The language of the speech. Defaults to "hi" (Hindi).
    """
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(filename)
        print(f"Speech saved as {filename}")
    except Exception as e:
        print(f"Error generating speech: {e}")


def analyse_news(company_name):
    """Extracts news, summarizes, analyzes sentiment, translates, and generates speech for a given company.

    Args:
        company_name (str): The name of the company to analyze news for.

    Returns:
        tuple: The combined summary and the filename of the generated speech audio.
    """
    try:
        news_articles = extract_articles(company_name)
        if not news_articles:
            print("No articles found for this company.")
            return None, None

        combined_summary = generate_combined_summary(news_articles)
        combined_sentiment = analyze_sentiment(combined_summary)

        hindi_summary, hindi_sentiment = translate_to_hindi(combined_summary, combined_sentiment)
        text_to_speech(f"{hindi_summary}. Sentiment analysis of summary: {hindi_sentiment}",
                       "combined_summary_audio.mp3")

        save_report(news_articles)
        save_final_report(combined_summary)

        return combined_summary, "combined_summary_audio.mp3"
    except Exception as e:
        print(f"Error in script execution: {e}")
        return None, None
