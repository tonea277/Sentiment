import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import PercentFormatter
import yfinance as yf
from newsapi import NewsApiClient
from datetime import datetime, timedelta
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import numpy as np
import os
from dotenv import load_dotenv
import hashlib
import sqlite3
import uuid

# Load environment variables
load_dotenv()

# ─────────────────────────────────────────────
# NLTK / Sentiment
# ─────────────────────────────────────────────

@st.cache_resource
def download_nltk_data():
    nltk.download('vader_lexicon', quiet=True)
    return SentimentIntensityAnalyzer()

sia = download_nltk_data()
pd.set_option("display.max_colwidth", 1000)


# ─────────────────────────────────────────────
# Database / Auth
# ─────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS users
    (id TEXT PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT, api_usage INTEGER)
    ''')
    conn.commit()
    conn.close()

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
    return result and result[0] == hash_password(password)

def track_api_usage(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET api_usage = api_usage + 1 WHERE username = ?", (username,))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# Sentiment helpers
# ─────────────────────────────────────────────

def get_articles(query, from_date):
    try:
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

def calculate_sentiment(articles_df):
    sentiment_scores = []
    for text in articles_df['description']:
        if isinstance(text, str):
            sentiment_scores.append(sia.polarity_scores(text)['compound'])
        else:
            sentiment_scores.append(0)
    articles_df['sentiment'] = sentiment_scores
    return articles_df

@st.cache_data(ttl=86400)
def get_sp500_tickers():
    try:
        import urllib.request
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        with urllib.request.urlopen(req) as response:
            tables = pd.read_html(response.read())
        sp500_table = tables[0]
        tickers_dict = {}
        for _, row in sp500_table.iterrows():
            tickers_dict[row['Symbol']] = f"{row['Symbol']} - {row['Security']}"
        return tickers_dict
    except Exception:
        return get_popular_sp500_tickers()

def get_popular_sp500_tickers():
    return {
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

def get_company_name(ticker):
    try:
        return yf.Ticker(ticker).info.get('longName', ticker)
    except Exception:
        return ticker


# ─────────────────────────────────────────────
# HPR helpers (ported from notebook)
# ─────────────────────────────────────────────

def download_daily_prices(ticker, start_date, end_date):
    return yf.download(ticker, start=start_date, end=end_date,
                       interval="1d", auto_adjust=False, progress=False)

def extract_adjusted_close(df):
    x = df.copy()
    if isinstance(x.columns, pd.MultiIndex):
        x.columns = x.columns.get_level_values(0)
    return (
        x[["Adj Close"]]
        .rename(columns={"Adj Close": "adj_close"})
        .reset_index()
        .rename(columns={"Date": "date"})
    )

def add_daily_returns(df, price_col="adj_close"):
    df = df.copy()
    df["daily_return"] = df[price_col].pct_change()
    return df

def compute_event_hprs(prices, event_dates, horizons=(1, 5, 10, 20),
                       ticker=None, date_col="date", price_col="adj_close",
                       event_col="event_date", direction="backward"):
    df = prices[[date_col, price_col]].copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col).reset_index(drop=True)
    df["pos"] = df.index

    cal = df[[date_col]].drop_duplicates().sort_values(date_col).reset_index(drop=True)
    events = pd.DataFrame({event_col: pd.to_datetime(event_dates)}).sort_values(event_col)

    event_map = (
        pd.merge_asof(
            events,
            cal.rename(columns={date_col: "event_trading_date"}),
            left_on=event_col,
            right_on="event_trading_date",
            direction=direction,
        )
        .merge(
            df[[date_col, "pos"]].rename(columns={date_col: "event_trading_date"}),
            on="event_trading_date",
            how="left",
        )
        .dropna(subset=["pos"])
    )
    event_map["pos"] = event_map["pos"].astype(int)

    rows = []
    n_obs = len(df)

    for _, r in event_map.iterrows():
        t = r["pos"]
        for n in horizons:
            s, e = t - n, t - 1
            if s >= 0 and e >= 0:
                rows.append({
                    "ticker": ticker, event_col: r[event_col],
                    "event_trading_date": r["event_trading_date"],
                    "pre_post": "pre", "days": int(n),
                    "start_date": df.loc[s, date_col],
                    "end_date": df.loc[e, date_col],
                    "hpr": df.loc[e, price_col] / df.loc[s, price_col] - 1,
                })
            s, e = t, t + n
            if e < n_obs:
                rows.append({
                    "ticker": ticker, event_col: r[event_col],
                    "event_trading_date": r["event_trading_date"],
                    "pre_post": "post", "days": int(n),
                    "start_date": df.loc[s, date_col],
                    "end_date": df.loc[e, date_col],
                    "hpr": df.loc[e, price_col] / df.loc[s, price_col] - 1,
                })

    return (
        pd.DataFrame(rows)
        .sort_values([event_col, "pre_post", "days"])
        .reset_index(drop=True)
    )

def plot_event_hpr_overlay(hpr_table, horizons=(1, 5, 10, 20), pre_post="post",
                           event_col="earnings_date", horizon_col="days",
                           value_col="hpr", title="Event HPR Overlay"):
    df = hpr_table.copy()
    df[event_col] = pd.to_datetime(df[event_col])
    df[horizon_col] = df[horizon_col].astype(int)
    df = df[df["pre_post"] == pre_post]

    pivot = (
        df.pivot(index=event_col, columns=horizon_col, values=value_col)
        .sort_index()
    )
    horizons = [int(h) for h in horizons]
    pivot = pivot.reindex(columns=horizons)

    fig, ax = plt.subplots(figsize=(9, 5))
    for event_dt, row in pivot.iterrows():
        ax.plot(horizons, row.values, marker="o", label=event_dt.strftime("%Y-%m-%d"))

    ax.axhline(0, linewidth=1, color="black", linestyle="--", alpha=0.4)
    ax.set_xlabel("Holding period (trading days)")
    ax.set_ylabel("Holding Period Return (HPR)")
    ax.set_title(title)
    ax.legend(title="Event date", frameon=False)
    ax.grid(True, alpha=0.3)
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=1.0))
    fig.tight_layout()
    return fig


# ─────────────────────────────────────────────
# Main app
# ─────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="Stock Sentiment & HPR Analysis",
        page_icon="📈",
        layout="wide"
    )

    init_db()

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ""

    # ── Auth ──────────────────────────────────
    if not st.session_state.logged_in:
        st.title("Attaining Alpha/VP Analytics — Login")
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
        return

    # ── Logged-in ─────────────────────────────
    st.title("Stock Sentiment & HPR Analysis")
    st.markdown(f"Welcome, **{st.session_state.username}**!")

    # Sidebar
    st.sidebar.header("Configuration")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    # ══════════════════════════════════════════
    # SIDEBAR — HPR first, Sentiment second
    # ══════════════════════════════════════════

    # ── HPR stock selection ───────────────────
    st.sidebar.subheader("HPR — Stock Selection")
    hpr_input_method = st.sidebar.radio(
        "Input method:",
        ["S&P 500 Dropdown", "Manual Entry"],
        help="Choose from S&P 500 companies or enter any ticker manually",
        key="hpr_input_method"
    )
    hpr_ticker = ""
    if hpr_input_method == "S&P 500 Dropdown":
        sp500_tickers_hpr = get_sp500_tickers()
        if sp500_tickers_hpr:
            if len(sp500_tickers_hpr) < 100:
                st.sidebar.info("📋 Showing 50 popular S&P 500 stocks")
            hpr_ticker_options = list(sp500_tickers_hpr.values())
            hpr_ticker_symbols = list(sp500_tickers_hpr.keys())
            hpr_default_idx = hpr_ticker_symbols.index("NVDA") if "NVDA" in hpr_ticker_symbols else 0
            hpr_selected = st.sidebar.selectbox(
                "Choose a company:",
                options=hpr_ticker_options,
                index=hpr_default_idx,
                key="hpr_dropdown"
            )
            hpr_ticker = hpr_selected.split(" - ")[0]
        else:
            st.sidebar.warning("Could not load S&P 500 list. Please use manual entry.")
            hpr_ticker = st.sidebar.text_input(
                "Ticker (HPR)", value="NVDA", key="hpr_manual_fallback"
            ).upper()
    else:
        hpr_ticker = st.sidebar.text_input(
            "Stock Ticker Symbol", value="NVDA",
            help="Enter a stock ticker (e.g., AAPL, GOOGL, TSLA, NVDA)",
            key="hpr_manual"
        ).upper()

    # ── HPR configuration ─────────────────────
    st.sidebar.subheader("HPR — Configuration")
    hpr_years = st.sidebar.multiselect(
        "Years to display",
        options=[2023, 2024, 2025],
        default=[2023, 2024, 2025],
        key="hpr_years"
    )
    hpr_pre_post = st.sidebar.radio(
        "Pre or Post earnings",
        options=["post", "pre"],
        index=0,
        key="hpr_pre_post"
    )
    hpr_horizons = st.sidebar.multiselect(
        "Horizons (trading days)",
        options=[1, 5, 10, 20],
        default=[1, 5, 10, 20],
        key="hpr_horizons"
    )
    st.sidebar.subheader("Earnings Dates")
    default_dates = {
        2025: "2025-02-26\n2025-05-28\n2025-08-27\n2025-11-19",
        2024: "2024-02-21\n2024-05-22\n2024-08-28\n2024-11-20",
        2023: "2023-02-22\n2023-05-24\n2023-08-23\n2023-11-21",
    }
    earnings_inputs = {}
    for yr in [2023, 2024, 2025]:
        with st.sidebar.expander(f"{yr} dates", expanded=False):
            earnings_inputs[yr] = st.text_area(
                f"Dates ({yr})",
                value=default_dates[yr],
                height=110,
                key=f"hpr_dates_{yr}",
                label_visibility="collapsed"
            )
    run_hpr = st.sidebar.button(
        "📈 Run HPR Analysis", type="primary", use_container_width=True, key="hpr_btn"
    )

    st.sidebar.divider()

    # ── Sentiment stock selection ─────────────
    st.sidebar.subheader("Sentiment — Stock Selection")
    input_method = st.sidebar.radio(
        "Input method:",
        ["S&P 500 Dropdown", "Manual Entry"],
        help="Choose from S&P 500 companies or enter any ticker manually",
        key="sent_input_method"
    )
    ticker = ""
    if input_method == "S&P 500 Dropdown":
        sp500_tickers = get_sp500_tickers()
        if sp500_tickers:
            if len(sp500_tickers) < 100:
                st.sidebar.info("📋 Showing 50 popular S&P 500 stocks")
            ticker_options = list(sp500_tickers.values())
            ticker_symbols = list(sp500_tickers.keys())
            default_idx = ticker_symbols.index("NVDA") if "NVDA" in ticker_symbols else 0
            selected_option = st.sidebar.selectbox(
                "Choose a company:",
                options=ticker_options,
                index=default_idx,
                key="sent_dropdown"
            )
            ticker = selected_option.split(" - ")[0]
        else:
            st.sidebar.warning("Could not load S&P 500 list. Please use manual entry.")
            ticker = st.sidebar.text_input(
                "Stock Ticker Symbol", value="NVDA", key="sent_manual_fallback"
            ).upper()
    else:
        ticker = st.sidebar.text_input(
            "Stock Ticker Symbol", value="NVDA",
            help="Enter a stock ticker (e.g., AAPL, GOOGL, TSLA, NVDA)",
            key="sent_manual"
        ).upper()
    days = st.sidebar.slider("Days to analyse", min_value=7, max_value=30, value=30, key="sent_days")
    analyze_button = st.sidebar.button(
        "🔍 Analyse Sentiment", type="primary", use_container_width=True, key="sent_btn"
    )

    st.sidebar.divider()

    # Top-level tabs
    tab_hpr, tab_sentiment = st.tabs(["📊 HPR Overlay", "📰 Sentiment Analysis"])

    # ══════════════════════════════════════════
    # TAB 1 — SENTIMENT
    # ══════════════════════════════════════════
    with tab_sentiment:
        st.markdown(
            "Analyse sentiment distribution for the last 30 days from top news articles for any S&P 500 stock."
        )

        if analyze_button:
            if not ticker:
                st.error("⚠️ Please enter a stock ticker")
                return

            with st.spinner(f'Fetching news articles for {ticker}...'):
                track_api_usage(st.session_state.username)
                company_name = get_company_name(ticker)
                from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
                search_query = f"{ticker} stock OR {company_name} stock"
                articles = get_articles(search_query, from_date)

                if not articles:
                    st.warning(f"No articles found for {ticker} in the last {days} days")
                    return

                articles_df = pd.DataFrame(articles)
                articles_df = articles_df[['title', 'description', 'publishedAt', 'url', 'source']]
                articles_df['source'] = articles_df['source'].apply(lambda x: x['name'])
                articles_df = calculate_sentiment(articles_df)

                st.success(f"Found {len(articles_df)} articles for {company_name} ({ticker})")

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

                # Distribution chart
                st.subheader("Sentiment Distribution")
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.hist(articles_df['sentiment'], bins=30, color='steelblue', edgecolor='black', alpha=0.7)
                ax.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Neutral')
                ax.axvline(x=avg_sentiment, color='green', linestyle='--', linewidth=2,
                           label=f'Average ({avg_sentiment:.3f})')
                ax.set_xlabel('Sentiment Score', fontsize=12)
                ax.set_ylabel('Number of Articles', fontsize=12)
                ax.set_title(f'Sentiment Distribution for {company_name} ({ticker})',
                             fontsize=14, fontweight='bold')
                ax.legend()
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)

                # Sentiment over time
                st.subheader("Sentiment Over Time")
                articles_df['publishedAt'] = pd.to_datetime(articles_df['publishedAt'])
                articles_df = articles_df.sort_values('publishedAt')

                fig2, ax2 = plt.subplots(figsize=(12, 6))
                ax2.scatter(articles_df['publishedAt'], articles_df['sentiment'],
                            alpha=0.6, s=50,
                            c=articles_df['sentiment'], cmap='RdYlGn',
                            edgecolors='black')
                ax2.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.5)

                from scipy import stats
                x_numeric = (
                    articles_df['publishedAt'] - articles_df['publishedAt'].min()
                ).dt.total_seconds()
                slope, intercept, *_ = stats.linregress(x_numeric, articles_df['sentiment'])
                trend_line = slope * x_numeric + intercept
                ax2.plot(articles_df['publishedAt'], trend_line,
                         color='blue', linewidth=2, label='Trend', alpha=0.7)

                ax2.set_xlabel('Date', fontsize=12)
                ax2.set_ylabel('Sentiment Score', fontsize=12)
                ax2.set_title(f'Sentiment Timeline for {company_name} ({ticker})',
                              fontsize=14, fontweight='bold')
                ax2.legend()
                ax2.grid(True, alpha=0.3)
                plt.xticks(rotation=45)
                st.pyplot(fig2)

                # Articles table
                st.subheader("Recent Articles")

                def sentiment_label(score):
                    if score > 0.05:
                        return "🟢 Positive"
                    elif score < -0.05:
                        return "🔴 Negative"
                    else:
                        return "⚪ Neutral"

                articles_df['sentiment_label'] = articles_df['sentiment'].apply(sentiment_label)
                display_df = articles_df[
                    ['publishedAt', 'title', 'source', 'sentiment', 'sentiment_label', 'url']
                ].copy()
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
                        "url": st.column_config.LinkColumn("Link"),
                    },
                    hide_index=True,
                    use_container_width=True,
                )

    # ══════════════════════════════════════════
    # TAB 2 — HPR OVERLAY
    # ══════════════════════════════════════════
    with tab_hpr:
        st.markdown(
            "Post-earnings Holding Period Return (HPR) overlay for NVDA across 2023–2025. "
            "Each line represents one quarterly earnings event; horizons are +1, +5, +10, +20 trading days."
        )

        if run_hpr:
            if not hpr_ticker:
                st.error("Please enter a ticker.")
                st.stop()
            if not hpr_years:
                st.error("Please select at least one year.")
                st.stop()
            if not hpr_horizons:
                st.error("Please select at least one horizon.")
                st.stop()

            with st.spinner(f"Downloading price data for {hpr_ticker}..."):
                try:
                    raw = download_daily_prices(hpr_ticker, "2022-01-01", "2025-12-31")
                    if raw.empty:
                        st.error(f"No price data found for {hpr_ticker}.")
                        st.stop()
                    prices = add_daily_returns(extract_adjusted_close(raw))
                except Exception as e:
                    st.error(f"Failed to download price data: {e}")
                    st.stop()

            # Parse earnings dates per year
            parsed_dates = {}
            parse_errors = []
            for yr in hpr_years:
                raw_text = earnings_inputs.get(yr, "")
                lines = [l.strip() for l in raw_text.strip().splitlines() if l.strip()]
                try:
                    dates = pd.to_datetime(lines).tolist()
                    parsed_dates[yr] = [d.strftime("%Y-%m-%d") for d in dates]
                except Exception:
                    parse_errors.append(f"{yr}: could not parse dates — check format (YYYY-MM-DD)")

            if parse_errors:
                for err in parse_errors:
                    st.error(err)
                st.stop()

            # Build HPR tables and render one chart per year
            st.subheader(
                f"{'Post' if hpr_pre_post == 'post' else 'Pre'}-Earnings HPR Overlay — {hpr_ticker}"
            )

            for yr in sorted(hpr_years):
                dates_for_year = parsed_dates[yr]
                if not dates_for_year:
                    st.warning(f"No earnings dates found for {yr}.")
                    continue

                with st.spinner(f"Computing HPRs for {yr}..."):
                    try:
                        hpr_table = compute_event_hprs(
                            prices=prices,
                            event_dates=dates_for_year,
                            horizons=hpr_horizons,
                            ticker=hpr_ticker,
                            date_col="date",
                            price_col="adj_close",
                            event_col="earnings_date",
                        )

                        if hpr_table.empty:
                            st.warning(f"No HPR data computed for {yr} — dates may be outside price data range.")
                            continue

                        fig = plot_event_hpr_overlay(
                            hpr_table,
                            horizons=hpr_horizons,
                            pre_post=hpr_pre_post,
                            event_col="earnings_date",
                            title=(
                                f"{hpr_ticker} "
                                f"{'Post' if hpr_pre_post == 'post' else 'Pre'}-Earnings "
                                f"HPR Overlay by Quarter {yr}"
                            ),
                        )
                        st.pyplot(fig)
                        plt.close(fig)

                        # Summary table under each chart
                        with st.expander(f"Show HPR data table — {yr}"):
                            show_df = (
                                hpr_table[hpr_table["pre_post"] == hpr_pre_post]
                                [["earnings_date", "days", "hpr"]]
                                .copy()
                            )
                            show_df["earnings_date"] = pd.to_datetime(
                                show_df["earnings_date"]
                            ).dt.strftime("%Y-%m-%d")
                            show_df["hpr"] = show_df["hpr"].map(lambda x: f"{x:.2%}")
                            show_df.columns = ["Earnings Date", "Horizon (days)", "HPR"]
                            st.dataframe(show_df, hide_index=True, use_container_width=True)

                    except Exception as e:
                        st.error(f"Error computing HPR for {yr}: {e}")

            st.success("HPR analysis complete.")


if __name__ == "__main__":
    main()
