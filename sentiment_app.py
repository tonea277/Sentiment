import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from newsapi import NewsApiClient
from datetime import datetime, timedelta
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import os

# Download VADER lexicon (only runs once)
@st.cache_resource
def download_nltk_data():
    nltk.download('vader_lexicon', quiet=True)
    return SentimentIntensityAnalyzer()

# Initialize sentiment analyzer
sia = download_nltk_data()

# Set pandas display option
pd.set_option("display.max_colwidth", 1000)

# Function to get articles from NewsAPI
def get_articles(query, from_date, api_key):
    try:
        newsapi = NewsApiClient(api_key=api_key)
        
        articles = newsapi.get_everything(
            q=query,
            from_param=from_date,
            language='en',
            sort_by='publishedAt'
        )
        
        return articles.get('articles', [])
    except Exception as e:
        st.error(f"Error fetching articles: {str(e)}")
        return []

# Function to calculate sentiment scores
def calculate_sentiment(articles_df):
    sentiment_scores = []
    
    for text in articles_df['description']:
        if isinstance(text, str):
            sentiment_scores.append(sia.polarity_scores(text)['compound'])
        else:
            sentiment_scores.append(0)
    
    articles_df['sentiment'] = sentiment_scores
    return articles_df

# Function to get company name from ticker
def get_company_name(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info.get('longName', ticker)
    except:
        return ticker

# Streamlit App
def main():
    st.set_page_config(page_title="Stock Sentiment Analyzer", page_icon="📈", layout="wide")
    
    st.title("📈 Stock News Sentiment Analyzer")
    st.markdown("Analyze sentiment distribution from news articles for any stock ticker over the last 30 days")
    
    # Sidebar for inputs
    st.sidebar.header("Configuration")
    
    # API Key input (with option to use environment variable)
    api_key = st.sidebar.text_input(
        "NewsAPI Key", 
        value=os.getenv("NEWSAPI_KEY", ""),
        type="password",
        help="Get your free API key from https://newsapi.org"
    )
    
    # Ticker input
    ticker = st.sidebar.text_input(
        "Stock Ticker Symbol",
        value="NVDA",
        help="Enter a stock ticker (e.g., AAPL, GOOGL, TSLA, NVDA)"
    ).upper()
    
    # Days input
    days = st.sidebar.slider("Days to analyze", min_value=7, max_value=30, value=30)
    
    # Analyze button
    analyze_button = st.sidebar.button("🔍 Analyze Sentiment", type="primary", use_container_width=True)
    
    # Main content area
    if analyze_button:
        if not api_key:
            st.error("⚠️ Please enter your NewsAPI key in the sidebar")
            st.info("Get a free API key at https://newsapi.org")
            return
        
        if not ticker:
            st.error("⚠️ Please enter a stock ticker")
            return
        
        # Show loading spinner
        with st.spinner(f'Fetching news articles for {ticker}...'):
            # Get company name
            company_name = get_company_name(ticker)
            
            # Calculate date range
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # Fetch articles
            search_query = f"{ticker} stock OR {company_name} stock"
            articles = get_articles(search_query, from_date, api_key)
            
            if not articles:
                st.warning(f"No articles found for {ticker} in the last {days} days")
                return
            
            # Create dataframe
            articles_df = pd.DataFrame(articles)
            
            # Calculate sentiment
            articles_df = calculate_sentiment(articles_df)
            
            # Display results
            st.success(f"Found {len(articles)} articles about {company_name} ({ticker})")
            
            # Create two columns for metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_sentiment = articles_df['sentiment'].mean()
                st.metric("Average Sentiment", f"{avg_sentiment:.3f}")
            
            with col2:
                positive_pct = (articles_df['sentiment'] > 0.05).sum() / len(articles_df) * 100
                st.metric("Positive Articles", f"{positive_pct:.1f}%")
            
            with col3:
                negative_pct = (articles_df['sentiment'] < -0.05).sum() / len(articles_df) * 100
                st.metric("Negative Articles", f"{negative_pct:.1f}%")
            
            # Plot sentiment distribution
            st.subheader(f"Sentiment Distribution for {company_name} ({ticker})")
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.hist(articles_df['sentiment'], bins=30, edgecolor='black', color='steelblue', alpha=0.7)
            ax.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Neutral')
            ax.set_xlabel('Sentiment Score', fontsize=12)
            ax.set_ylabel('Frequency', fontsize=12)
            ax.set_title(f'Distribution of Sentiment Scores - {company_name} ({ticker})', fontsize=14, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            ax.legend()
            
            st.pyplot(fig)
            
            # Show article samples
            st.subheader("Recent Articles")
            
            # Add sentiment category
            articles_df['sentiment_category'] = articles_df['sentiment'].apply(
                lambda x: '😊 Positive' if x > 0.05 else ('😐 Neutral' if x >= -0.05 else '😞 Negative')
            )
            
            # Display articles
            display_df = articles_df[['publishedAt', 'title', 'sentiment', 'sentiment_category', 'url']].copy()
            display_df['publishedAt'] = pd.to_datetime(display_df['publishedAt']).dt.strftime('%Y-%m-%d %H:%M')
            display_df.columns = ['Published', 'Headline', 'Score', 'Sentiment', 'URL']
            display_df = display_df.sort_values('Published', ascending=False).head(10)
            
            st.dataframe(
                display_df,
                column_config={
                    "URL": st.column_config.LinkColumn("Article Link"),
                    "Score": st.column_config.NumberColumn("Score", format="%.3f")
                },
                hide_index=True,
                use_container_width=True
            )
    
    # Instructions when not analyzing
    else:
        st.info("👈 Enter a stock ticker in the sidebar and click 'Analyze Sentiment' to get started")
        
        st.markdown("""
        ### How it works:
        1. **Enter your NewsAPI key** - Get one free at [newsapi.org](https://newsapi.org)
        2. **Enter a stock ticker** - Any valid stock symbol (e.g., AAPL, MSFT, TSLA)
        3. **Click Analyze** - View sentiment analysis from recent news articles
        
        ### Sentiment Scoring:
        - **Positive**: Score > 0.05 😊
        - **Neutral**: Score between -0.05 and 0.05 😐
        - **Negative**: Score < -0.05 😞
        
        The sentiment score ranges from -1 (most negative) to +1 (most positive).
        """)

if __name__ == "__main__":
    main()
