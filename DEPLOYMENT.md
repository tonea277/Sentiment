# 🚀 Quick Deployment Guide

## Option 1: Run Locally (5 minutes)

1. **Install dependencies**:
   ```bash
   pip install streamlit pandas matplotlib yfinance newsapi-python nltk python-dotenv scipy
   ```

2. **Get API key**:
   - Visit https://newsapi.org/register
   - Copy your API key

3. **Create .env file**:
   ```bash
   echo "NEWSAPI_KEY=your_key_here" > .env
   ```

4. **Run**:
   ```bash
   streamlit run stock_sentiment_app.py
   ```

   Opens at http://localhost:8501

---

## Option 2: Deploy to Streamlit Cloud (10 minutes)

### Step 1: Prepare GitHub Repository

```bash
# Initialize git
git init

# Add files
git add stock_sentiment_app.py requirements.txt README.md .gitignore

# Commit
git commit -m "Stock sentiment analyzer"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io
2. Click "New app"
3. Connect your GitHub account
4. Select your repository
5. Main file: `stock_sentiment_app.py`
6. Click "Advanced settings" → "Secrets"
7. Add:
   ```toml
   NEWSAPI_KEY = "your_actual_api_key"
   ```
8. Click "Deploy"

**Done!** Your app will be live at `https://your-app.streamlit.app`

---

## Option 3: Deploy to Other Platforms

### Heroku

1. Create `Procfile`:
   ```
   web: sh setup.sh && streamlit run stock_sentiment_app.py
   ```

2. Create `setup.sh`:
   ```bash
   mkdir -p ~/.streamlit/
   echo "[server]
   headless = true
   port = $PORT
   enableCORS = false
   " > ~/.streamlit/config.toml
   ```

3. Deploy:
   ```bash
   heroku create
   heroku config:set NEWSAPI_KEY=your_key
   git push heroku main
   ```

### Railway

1. Push to GitHub
2. Go to https://railway.app
3. "New Project" → "Deploy from GitHub"
4. Add environment variable: `NEWSAPI_KEY`
5. Railway auto-detects Streamlit

### Render

1. Push to GitHub
2. Go to https://render.com
3. "New" → "Web Service"
4. Connect repository
5. Build: `pip install -r requirements.txt`
6. Start: `streamlit run stock_sentiment_app.py`
7. Add environment variable: `NEWSAPI_KEY`

---

## Quick Test

After deployment, test with these tickers:
- **AAPL** (Apple)
- **NVDA** (NVIDIA)
- **TSLA** (Tesla)
- **GOOGL** (Google)

---

## Troubleshooting

**App won't start?**
- Check Python version (3.8+)
- Verify all dependencies installed
- Check API key is set

**No articles found?**
- Use major company tickers
- Check NewsAPI quota (100/day free)
- Try increasing days range

**Database errors?**
- Delete `users.db` file
- Restart the app

---

## Next Steps

- [ ] Get NewsAPI key
- [ ] Test locally
- [ ] Push to GitHub
- [ ] Deploy to Streamlit Cloud
- [ ] Share your app! 🎉
