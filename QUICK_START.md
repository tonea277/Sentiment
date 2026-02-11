# 🚀 QUICK START GUIDE

## Run Locally in 3 Steps

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get your NewsAPI key:**
   - Go to https://newsapi.org
   - Sign up (free)
   - Copy your API key

3. **Run the app:**
   ```bash
   streamlit run sentiment_app.py
   ```
   The app will open in your browser at http://localhost:8501

---

## Deploy Online (FREE) - Share with Anyone! 🌐

### GitHub + Streamlit Cloud

1. **Upload to GitHub:**
   - Create a new repository
   - Upload all these files:
     - sentiment_app.py
     - requirements.txt
     - README.md
     - .gitignore

2. **Deploy to Streamlit:**
   - Go to https://share.streamlit.io
   - Sign in with GitHub
   - Click "New app"
   - Select your repository and sentiment_app.py
   - Click "Deploy"

3. **Add API Key Securely:**
   - In Streamlit Cloud dashboard, go to Settings → Secrets
   - Add:
     ```
     NEWSAPI_KEY = "your_api_key_here"
     ```
   - Save

✅ Done! Your app is now live and shareable!

---

## What Changed from Your Notebook?

✨ **New Features:**
- Interactive ticker input (instead of hardcoded stocks)
- Slider to choose number of days (7-30)
- Live metrics (average sentiment, % positive/negative)
- Clickable article links
- Better visualization with color coding
- Security: API key stored safely (not in code)

📊 **Same Core Logic:**
- NewsAPI for fetching articles
- VADER for sentiment analysis
- Matplotlib for visualization
- All your original analysis preserved!

---

## Example Usage

1. Enter ticker: **TSLA**
2. Click "Analyze Sentiment"
3. See sentiment distribution for Tesla news
4. View recent headlines with sentiment scores

---

## Need Help?

Check the full README.md for:
- Detailed deployment instructions
- Troubleshooting guide
- Example tickers to try
- Understanding sentiment scores
