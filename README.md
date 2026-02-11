# Stock News Sentiment Analyzer 📈

A Streamlit web application that analyzes sentiment from news articles for any stock ticker over the last 30 days using NewsAPI and VADER sentiment analysis.

## Features

- 🔍 **Search any stock ticker** - AAPL, GOOGL, TSLA, NVDA, etc.
- 📊 **Visual sentiment distribution** - See the spread of positive, neutral, and negative news
- 📈 **Key metrics** - Average sentiment, percentage of positive/negative articles
- 📰 **Recent articles** - View the latest headlines with sentiment scores
- ⚡ **Fast and interactive** - Real-time analysis with a clean interface

## Quick Start

### Option 1: Run Locally

1. **Clone or download** this repository

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get a NewsAPI key:**
   - Visit https://newsapi.org
   - Sign up for a free account
   - Copy your API key

4. **Run the app:**
   ```bash
   streamlit run sentiment_app.py
   ```

5. **Open in browser:**
   - The app will automatically open at `http://localhost:8501`
   - Enter your NewsAPI key in the sidebar
   - Enter a stock ticker and click "Analyze Sentiment"

### Option 2: Deploy to Streamlit Cloud (FREE) ⭐

This is the **easiest way** to share your app with others!

#### Step 1: Prepare Your Code

1. Create a GitHub account (if you don't have one)
2. Create a new repository on GitHub
3. Upload these files to your repository:
   - `sentiment_app.py`
   - `requirements.txt`
   - `README.md` (optional)

#### Step 2: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository, branch (usually `main`), and file (`sentiment_app.py`)
5. Click "Deploy"!

#### Step 3: Add Your API Key (Securely)

**Option A: Using Streamlit Secrets (Recommended)**
1. In your Streamlit Cloud dashboard, click on your app
2. Click the three dots (⋮) and select "Settings"
3. Click "Secrets" in the left sidebar
4. Add your NewsAPI key:
   ```toml
   NEWSAPI_KEY = "your_api_key_here"
   ```
5. Click "Save"

**Option B: Enter in the App**
- Users can enter their own API key directly in the sidebar when using the app

Your app will now be live at: `https://your-app-name.streamlit.app`

## How to Use

1. **Enter NewsAPI Key** - In the sidebar (or use environment variable)
2. **Enter Stock Ticker** - Any valid ticker symbol (e.g., AAPL, MSFT, TSLA)
3. **Select Time Range** - Choose how many days of news to analyze (7-30 days)
4. **Click "Analyze Sentiment"** - View the results!

## Understanding the Results

### Sentiment Scores
- **Range:** -1.0 (most negative) to +1.0 (most positive)
- **Positive:** Score > 0.05 😊
- **Neutral:** Score between -0.05 and 0.05 😐
- **Negative:** Score < -0.05 😞

### Metrics Displayed
- **Average Sentiment** - Overall sentiment across all articles
- **Positive Articles** - Percentage with positive sentiment
- **Negative Articles** - Percentage with negative sentiment
- **Sentiment Distribution Chart** - Visual histogram of all scores
- **Recent Headlines** - Table of latest articles with scores

## Example Tickers to Try

- **AAPL** - Apple Inc.
- **GOOGL** - Alphabet (Google)
- **MSFT** - Microsoft
- **TSLA** - Tesla
- **NVDA** - NVIDIA
- **AMZN** - Amazon
- **META** - Meta (Facebook)

## Requirements

See `requirements.txt` for full list of dependencies:
- streamlit
- newsapi-python
- yfinance
- nltk
- pandas
- matplotlib

## Troubleshooting

### "No articles found"
- Try a different ticker or more common company name
- Check if the ticker is valid
- NewsAPI free tier has limits (100 requests/day)

### "Error fetching articles"
- Verify your API key is correct
- Check your internet connection
- Ensure you haven't exceeded NewsAPI rate limits

### NLTK Download Error
- The app automatically downloads VADER lexicon on first run
- If it fails, manually run: `python -m nltk.downloader vader_lexicon`

## API Key Information

This app uses **NewsAPI** to fetch news articles:
- **Free tier:** 100 requests per day, up to 100 articles per request
- **Limitations:** Free tier only shows news from the last 30 days
- **Get your key:** https://newsapi.org

## Security Note

⚠️ **Never commit your API key to GitHub!**
- Use environment variables or Streamlit secrets
- Don't hardcode API keys in your code
- If you accidentally expose a key, regenerate it immediately

## License

Feel free to use and modify this app for your own projects!

## Credits

Built with:
- [Streamlit](https://streamlit.io) - Web framework
- [NewsAPI](https://newsapi.org) - News articles
- [VADER](https://github.com/cjhutto/vaderSentiment) - Sentiment analysis
- [yfinance](https://github.com/ranaroussi/yfinance) - Stock data
