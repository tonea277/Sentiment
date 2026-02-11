import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from newsapi import NewsApiClient
from datetime import datetime, timedelta
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import os
from dotenv import load_dotenv
import hashlib
import sqlite3
import uuid

# Load environment variables
load_dotenv()

# Download VADER lexicon (only runs once)
@st.cache_resource
def download_nltk_data():
    nltk.download('vader_lexicon', quiet=True)
    return SentimentIntensityAnalyzer()

# Initialize sentiment analyzer
sia = download_nltk_data()

# Set pandas display option
pd.set_option("display.max_colwidth", 1000)

# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS users
    (id TEXT PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT, api_usage INTEGER)
    ''')
    conn.commit()
    conn.close()

# User authentication functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    user_id = str(uuid.uuid4())
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", 
                 (user_id, username, hash_password(password), 0))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    if result and result[0] == hash_password(password):
        return True
    return False

def track_api_usage(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET api_usage = api_usage + 1 WHERE username = ?", (username,))
    conn.commit()
    conn.close()

# Function to get articles from NewsAPI
def get_articles(query, from_date):
    try:
        # Use the admin API key from environment variables
        api_key = os.getenv("NEWSAPI_KEY")
        if not api_key:
            st.error("Server configuration error: API key not found")
            return []
            
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

# Function to get S&P 500 tickers
@st.cache_data(ttl=86400)  # Cache for 24 hours
def get_sp500_tickers():
    try:
        import urllib.request
        
        # Add user agent to avoid 403 errors
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        # Read HTML with user agent
        with urllib.request.urlopen(req) as response:
            tables = pd.read_html(response.read())
        
        sp500_table = tables[0]
        
        # Create a dictionary with ticker and company name
        tickers_dict = {}
        for _, row in sp500_table.iterrows():
            ticker = row['Symbol']
            company = row['Security']
            tickers_dict[ticker] = f"{ticker} - {company}"
        
        return tickers_dict
    except Exception as e:
        # Fallback: Return a curated list of popular S&P 500 stocks
        return get_popular_sp500_tickers()

# Fallback function with popular S&P 500 stocks
def get_popular_sp500_tickers():
    """Returns a curated list of popular S&P 500 stocks as fallback"""
    popular_stocks = {
        'AAPL': 'AAPL - Apple Inc.',
        'MSFT': 'MSFT - Microsoft Corporation',
        'GOOGL': 'GOOGL - Alphabet Inc. Class A',
        'AMZN': 'AMZN - Amazon.com Inc.',
        'NVDA': 'NVDA - NVIDIA Corporation',
        'META': 'META - Meta Platforms Inc.',
        'TSLA': 'TSLA - Tesla Inc.',
        'BRK.B': 'BRK.B - Berkshire Hathaway Inc. Class B',
        'JPM': 'JPM - JPMorgan Chase & Co.',
        'JNJ': 'JNJ - Johnson & Johnson',
        'V': 'V - Visa Inc.',
        'UNH': 'UNH - UnitedHealth Group Inc.',
        'XOM': 'XOM - Exxon Mobil Corporation',
        'PG': 'PG - Procter & Gamble Co.',
        'MA': 'MA - Mastercard Inc.',
        'HD': 'HD - Home Depot Inc.',
        'CVX': 'CVX - Chevron Corporation',
        'BAC': 'BAC - Bank of America Corp.',
        'ABBV': 'ABBV - AbbVie Inc.',
        'KO': 'KO - Coca-Cola Co.',
        'PEP': 'PEP - PepsiCo Inc.',
        'COST': 'COST - Costco Wholesale Corporation',
        'AVGO': 'AVGO - Broadcom Inc.',
        'MRK': 'MRK - Merck & Co. Inc.',
        'TMO': 'TMO - Thermo Fisher Scientific Inc.',
        'WMT': 'WMT - Walmart Inc.',
        'CSCO': 'CSCO - Cisco Systems Inc.',
        'DIS': 'DIS - Walt Disney Co.',
        'ABT': 'ABT - Abbott Laboratories',
        'ACN': 'ACN - Accenture plc',
        'ADBE': 'ADBE - Adobe Inc.',
        'AMD': 'AMD - Advanced Micro Devices Inc.',
        'NFLX': 'NFLX - Netflix Inc.',
        'NKE': 'NKE - NIKE Inc.',
        'ORCL': 'ORCL - Oracle Corporation',
        'CRM': 'CRM - Salesforce Inc.',
        'INTC': 'INTC - Intel Corporation',
        'QCOM': 'QCOM - QUALCOMM Inc.',
        'TXN': 'TXN - Texas Instruments Inc.',
        'UPS': 'UPS - United Parcel Service Inc.',
        'BA': 'BA - Boeing Co.',
        'CAT': 'CAT - Caterpillar Inc.',
        'GE': 'GE - General Electric Co.',
        'IBM': 'IBM - International Business Machines Corp.',
        'MMM': 'MMM - 3M Co.',
        'GS': 'GS - Goldman Sachs Group Inc.',
        'SPGI': 'SPGI - S&P Global Inc.',
        'BLK': 'BLK - BlackRock Inc.',
        'AXP': 'AXP - American Express Co.',
        'NOW': 'NOW - ServiceNow Inc.',
    }
    return popular_stocks

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
    
    # Initialize database
    init_db()
    
    # Session state initialization
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    
    # Authentication UI
    if not st.session_state.logged_in:
        st.title("VP Analytics Stock Sentiment Analyzer - Login")
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login"):
                if verify_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        with tab2:
            new_username = st.text_input("Choose Username", key="reg_username")
            new_password = st.text_input("Choose Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
            
            if st.button("Register"):
                if new_password != confirm_password:
                    st.error("Passwords don't match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    if create_user(new_username, new_password):
                        st.success("Registration successful! Please login.")
                    else:
                        st.error("Username already exists")
    
    # Main application (only shown when logged in)
    else:
        st.title("Stock Sentiment Analysis")
        st.markdown(f"Welcome, {st.session_state.username}! Analyze sentiment distribution for the last 30 days from top news articles for any stock in the S&P 500.")
        
        # Sidebar for inputs
        st.sidebar.header("Configuration")
        
        # Logout button
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()
        
        # Ticker selection method
        st.sidebar.subheader("Select Stock")
        input_method = st.sidebar.radio(
            "Input method:",
            ["S&P 500 Dropdown", "Manual Entry"],
            help="Choose from S&P 500 companies or enter any ticker manually"
        )
        
        ticker = ""
        
        if input_method == "S&P 500 Dropdown":
            # Load S&P 500 tickers
            sp500_tickers = get_sp500_tickers()
            
            if sp500_tickers:
                # Show info if using fallback list
                if len(sp500_tickers) < 100:
                    st.sidebar.info("📋 Showing 50 popular S&P 500 stocks")
                
                # Create list of display options
                ticker_options = list(sp500_tickers.values())
                ticker_symbols = list(sp500_tickers.keys())
                
                # Default to NVDA if available
                default_idx = ticker_symbols.index("NVDA") if "NVDA" in ticker_symbols else 0
                
                selected_option = st.sidebar.selectbox(
                    "Choose a company:",
                    options=ticker_options,
                    index=default_idx
                )
                
                # Extract ticker symbol from selection
                ticker = selected_option.split(" - ")[0]
            else:
                st.sidebar.warning("Could not load S&P 500 list. Please use manual entry.")
                ticker = st.sidebar.text_input(
                    "Stock Ticker Symbol",
                    value="NVDA",
                    help="Enter a stock ticker"
                ).upper()
        else:
            # Manual entry
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
            if not ticker:
                st.error("⚠️ Please enter a stock ticker")
                return
            
            # Show loading spinner
            with st.spinner(f'Fetching news articles for {ticker}...'):
                # Track API usage
                track_api_usage(st.session_state.username)
                
                # Get company name
                company_name = get_company_name(ticker)
                
                # Calculate date range
                from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
                
                # Fetch articles
                search_query = f"{ticker} stock OR {company_name} stock"
                articles = get_articles(search_query, from_date)
                
                if not articles:
                    st.warning(f"No articles found for {ticker} in the last {days} days")
                    return
                
                # Create dataframe
                articles_df = pd.DataFrame(articles)
                articles_df = articles_df[['title', 'description', 'publishedAt', 'url', 'source']]
                articles_df['source'] = articles_df['source'].apply(lambda x: x['name'])
                
                # Calculate sentiment
                articles_df = calculate_sentiment(articles_df)
                
                # Display results
                st.success(f"Found {len(articles_df)} articles for {company_name} ({ticker})")
                
                # Create columns for metrics
                col1, col2, col3, col4 = st.columns(4)
                
                avg_sentiment = articles_df['sentiment'].mean()
                positive_count = len(articles_df[articles_df['sentiment'] > 0.05])
                negative_count = len(articles_df[articles_df['sentiment'] < -0.05])
                neutral_count = len(articles_df) - positive_count - negative_count
                
                with col1:
                    st.metric("Average Sentiment", f"{avg_sentiment:.3f}")
                with col2:
                    st.metric("Positive Articles", positive_count)
                with col3:
                    st.metric("Neutral Articles", neutral_count)
                with col4:
                    st.metric("Negative Articles", negative_count)
                
                # Sentiment distribution chart
                st.subheader("Sentiment Distribution")
                
                fig, ax = plt.subplots(figsize=(10, 6))
                
                # Create histogram
                ax.hist(articles_df['sentiment'], bins=30, color='steelblue', edgecolor='black', alpha=0.7)
                ax.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Neutral')
                ax.axvline(x=avg_sentiment, color='green', linestyle='--', linewidth=2, label=f'Average ({avg_sentiment:.3f})')
                
                ax.set_xlabel('Sentiment Score', fontsize=12)
                ax.set_ylabel('Number of Articles', fontsize=12)
                ax.set_title(f'Sentiment Distribution for {company_name} ({ticker})', fontsize=14, fontweight='bold')
                ax.legend()
                ax.grid(True, alpha=0.3)
                
                st.pyplot(fig)
                
                # Sentiment over time
                st.subheader("Sentiment Over Time")
                
                articles_df['publishedAt'] = pd.to_datetime(articles_df['publishedAt'])
                articles_df = articles_df.sort_values('publishedAt')
                
                fig2, ax2 = plt.subplots(figsize=(12, 6))
                
                ax2.scatter(articles_df['publishedAt'], articles_df['sentiment'], 
                           alpha=0.6, s=50, c=articles_df['sentiment'], cmap='RdYlGn', edgecolors='black')
                ax2.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.5)
                
                # Add trend line
                from scipy import stats
                x_numeric = (articles_df['publishedAt'] - articles_df['publishedAt'].min()).dt.total_seconds()
                slope, intercept, r_value, p_value, std_err = stats.linregress(x_numeric, articles_df['sentiment'])
                trend_line = slope * x_numeric + intercept
                ax2.plot(articles_df['publishedAt'], trend_line, color='blue', linewidth=2, label='Trend', alpha=0.7)
                
                ax2.set_xlabel('Date', fontsize=12)
                ax2.set_ylabel('Sentiment Score', fontsize=12)
                ax2.set_title(f'Sentiment Timeline for {company_name} ({ticker})', fontsize=14, fontweight='bold')
                ax2.legend()
                ax2.grid(True, alpha=0.3)
                plt.xticks(rotation=45)
                
                st.pyplot(fig2)
                
                # Show articles table
                st.subheader("Recent Articles")
                
                # Add sentiment label
                def sentiment_label(score):
                    if score > 0.05:
                        return "🟢 Positive"
                    elif score < -0.05:
                        return "🔴 Negative"
                    else:
                        return "⚪ Neutral"
                
                articles_df['sentiment_label'] = articles_df['sentiment'].apply(sentiment_label)
                
                # Display table
                display_df = articles_df[['publishedAt', 'title', 'source', 'sentiment', 'sentiment_label', 'url']].copy()
                display_df['publishedAt'] = display_df['publishedAt'].dt.strftime('%Y-%m-%d %H:%M')
                display_df = display_df.sort_values('publishedAt', ascending=False)
                
                st.dataframe(
                    display_df,
                    column_config={
                        "publishedAt": "Published",
                        "title": "Title",
                        "source": "Source",
                        "sentiment": st.column_config.NumberColumn("Score", format="%.3f"),
                        "sentiment_label": "Sentiment",
                        "url": st.column_config.LinkColumn("Link")
                    },
                    hide_index=True,
                    use_container_width=True
                )

if __name__ == "__main__":
    main()
