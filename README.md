# Stock Sentiment Analyzer

A web application that analyzes news sentiment for stock tickers using NewsAPI and NLTK's VADER sentiment analyzer.

## Features

- 🔐 User authentication with SQLite database
- 📰 Fetches news articles from NewsAPI
- 📊 Sentiment analysis using VADER
- 📈 Visual sentiment distribution charts
- ⏱️ Sentiment timeline with trend analysis
- 📋 Detailed article listings with sentiment scores

## Local Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get NewsAPI Key

1. Go to [https://newsapi.org/](https://newsapi.org/)
2. Sign up for a free account
3. Copy your API key

### 3. Configure Environment

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```
NEWSAPI_KEY=your_actual_api_key_here
```

### 4. Run the App

```bash
streamlit run stock_sentiment_app.py
```

The app will open in your browser at `http://localhost:8501`

## Deploy to Streamlit Cloud

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

### 2. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository and `stock_sentiment_app.py`
5. Click "Advanced settings"
6. Add your secrets:
   ```toml
   NEWSAPI_KEY = "your_actual_api_key_here"
   ```
7. Click "Deploy"

Your app will be live at: `https://your-app-name.streamlit.app`

## Usage

1. **Register**: Create an account on the login page
2. **Login**: Sign in with your credentials
3. **Analyze**: Enter a stock ticker (e.g., AAPL, GOOGL, NVDA)
4. **View Results**: See sentiment scores, charts, and article listings

## How It Works

1. **News Fetching**: Uses NewsAPI to fetch recent articles about the stock
2. **Sentiment Analysis**: VADER analyzes article descriptions for sentiment
3. **Visualization**: Creates charts showing sentiment distribution and trends
4. **User Tracking**: SQLite database tracks users and API usage

## Sentiment Scores

- **Positive**: Score > 0.05 (🟢)
- **Neutral**: Score between -0.05 and 0.05 (⚪)
- **Negative**: Score < -0.05 (🔴)

## API Limits

- NewsAPI free tier: 100 requests/day
- Each analysis counts as 1 request
- Consider upgrading for production use

## Technologies Used

- **Streamlit**: Web framework
- **NewsAPI**: News article source
- **NLTK VADER**: Sentiment analysis
- **yfinance**: Stock information
- **pandas/matplotlib**: Data processing and visualization
- **SQLite**: User authentication

## Security Notes

- Passwords are hashed with SHA-256
- Never commit `.env` or `secrets.toml` with real keys
- SQLite database is suitable for small-scale use
- For production, consider PostgreSQL and OAuth

## Troubleshooting

### "API key not found" error
- Make sure `.env` file exists (local) or secrets are configured (cloud)
- Check that `NEWSAPI_KEY` is spelled correctly

### "No articles found" error
- Try a more common ticker symbol
- Increase the number of days
- Check your NewsAPI quota

### Database errors
- Delete `users.db` and restart the app
- Check file permissions

## License

MIT License - feel free to modify and use for your projects!

## Contributing

Pull requests welcome! Please follow the existing code style.
