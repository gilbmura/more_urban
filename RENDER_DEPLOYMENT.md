# Render Deployment Guide

## ✅ Your app is now ready for Render deployment!

### Changes Made:
1. **Updated requirements.txt** - Replaced MySQL dependencies with PostgreSQL
2. **Updated DATABASE_URL** - Changed to PostgreSQL format
3. **Updated SQL queries** - Changed MySQL DATE_FORMAT to PostgreSQL DATE_TRUNC

### Deployment Steps:

#### 1. Create PostgreSQL Database on Render
- Go to Render Dashboard
- Click "New" → "PostgreSQL"
- Choose a name (e.g., "nyc-taxi-db")
- Note the connection details

#### 2. Deploy Backend as Web Service
- Go to Render Dashboard
- Click "New" → "Web Service"
- Connect your GitHub repository
- Configure:
  - **Build Command:** `pip install -r requirements.txt`
  - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 4 backend.app:app`
  - **Environment Variables:**
    - `DATABASE_URL` = Your PostgreSQL connection string from step 1
    - `FLASK_DEBUG` = `false`

#### 3. Deploy Frontend as Static Site
- Go to Render Dashboard
- Click "New" → "Static Site"
- Connect your GitHub repository
- Set **Root Directory:** `frontend`
- Set **Build Command:** (leave empty)
- Set **Publish Directory:** `frontend`

#### 4. Update Frontend API URL
- In `frontend/main.js`, update the API_BASE logic to point to your deployed backend URL

### Environment Variables Needed:
- `DATABASE_URL` - PostgreSQL connection string from Render
- `FLASK_DEBUG` - Set to `false` for production
- `PORT` - Automatically set by Render

### Database Schema:
Make sure to run your database schema (`db/schema.sql`) on the PostgreSQL database after creating it.

### Testing:
- Backend health check: `https://your-app.onrender.com/health`
- API endpoints: `https://your-app.onrender.com/api/summary`

Your app is now fully compatible with Render! 🚀
