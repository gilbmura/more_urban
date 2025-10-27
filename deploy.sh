#!/bin/bash

# NYC Taxi Analytics - One-Click Render Deployment Script
# This script prepares your application for Render deployment

echo "🚀 NYC Taxi Analytics - Render Deployment Setup"
echo "================================================"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ] || [ ! -f "backend/app.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "✅ Project structure verified"

# Check if render.yaml exists
if [ ! -f "render.yaml" ]; then
    echo "❌ Error: render.yaml not found. Please ensure all deployment files are present."
    exit 1
fi

echo "✅ Deployment configuration found"

# Verify PostgreSQL schema exists
if [ ! -f "db/schema_postgresql.sql" ]; then
    echo "❌ Error: PostgreSQL schema not found. Please ensure db/schema_postgresql.sql exists."
    exit 1
fi

echo "✅ PostgreSQL schema verified"

# Check if frontend is configured for Render
if ! grep -q "onrender.com" frontend/main.js; then
    echo "❌ Error: Frontend not configured for Render. Please update frontend/main.js"
    exit 1
fi

echo "✅ Frontend Render configuration verified"

echo ""
echo "🎉 Your application is ready for Render deployment!"
echo ""
echo "Next steps:"
echo "1. Push all changes to GitHub:"
echo "   git add ."
echo "   git commit -m 'Add Render deployment configuration'"
echo "   git push"
echo ""
echo "2. Go to https://render.com and create a new Blueprint"
echo "3. Connect your GitHub repository"
echo "4. Render will automatically:"
echo "   - Create PostgreSQL database with schema"
echo "   - Deploy backend API service"
echo "   - Deploy frontend static site"
echo "   - Configure all environment variables"
echo ""
echo "5. Your app will be available at:"
echo "   - Backend: https://nyc-taxi-backend.onrender.com"
echo "   - Frontend: https://nyc-taxi-frontend.onrender.com"
echo ""
echo "✨ Happy deploying!"
