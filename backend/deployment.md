# Deployment Guide - Integrated Scoring Engine

This guide will help you deploy the integrated scoring engine with both Django backend and React frontend.

## 🏗️ Project Structure

```
scoring-engine-integrated/
├── frontend/          # React + TypeScript admin interface
├── backend/           # Django API
├── README.md
├── API_DOCUMENTATION.md
├── DEPLOYMENT_GUIDE.md
└── deployment.md (this file)
```

## 🚀 Deployment Options

### Option 1: Separate Repositories (Recommended)

#### Backend Repository
1. **Create a new GitHub repository** for the backend
2. **Copy the backend folder** to the new repository
3. **Deploy to Railway** following the backend deployment guide

#### Frontend Repository
1. **Create a new GitHub repository** for the frontend
2. **Copy the frontend folder** to the new repository
3. **Deploy to Vercel** following the frontend deployment guide

### Option 2: Monorepo (Advanced)

Keep both frontend and backend in the same repository and deploy separately.

## 📋 Step-by-Step Deployment

### Step 1: Backend Deployment (Railway)

#### 1.1 Create Backend Repository
```bash
# Create a new directory for backend
mkdir scoring-engine-backend
cd scoring-engine-backend

# Copy backend files
cp -r ../scoring-engine-integrated/backend/* .

# Initialize git
git init
git add .
git commit -m "Initial commit: Django scoring engine backend"

# Create GitHub repository and push
git remote add origin https://github.com/YOUR_USERNAME/scoring-engine-backend.git
git push -u origin main
```

#### 1.2 Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your backend repository
5. Railway will automatically detect Django and deploy

#### 1.3 Configure Environment Variables
In Railway dashboard, add these environment variables:
```bash
DJANGO_SECRET_KEY=your-super-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-app-name.railway.app,your-custom-domain.com
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
```

#### 1.4 Database Setup
```bash
# In Railway dashboard, run:
python manage.py migrate
python manage.py createsuperuser
```

### Step 2: Frontend Deployment (Vercel)

#### 2.1 Create Frontend Repository
```bash
# Create a new directory for frontend
mkdir scoring-engine-frontend
cd scoring-engine-frontend

# Copy frontend files
cp -r ../scoring-engine-integrated/frontend/* .

# Initialize git
git init
git add .
git commit -m "Initial commit: React scoring engine frontend"

# Create GitHub repository and push
git remote add origin https://github.com/YOUR_USERNAME/scoring-engine-frontend.git
git push -u origin main
```

#### 2.2 Configure Environment Variables
Create a `.env` file in the frontend directory:
```bash
VITE_API_BASE_URL=https://your-backend-domain.railway.app/api/v1
```

#### 2.3 Deploy to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your frontend repository
4. Set environment variables in Vercel dashboard
5. Deploy

### Step 3: Update CORS Settings

In your Railway backend, update the CORS settings to include your Vercel frontend domain:

```python
# In backend/hfcscoringengine/settings/base.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://your-frontend-domain.vercel.app",  # Your actual frontend domain
]
```

## 🔧 Configuration

### Backend Configuration

#### Environment Variables
```bash
# Required
DATABASE_URL=postgresql://...  # Railway provides this
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com

# CORS
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app

# Optional
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

#### Database Setup
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Create admin group
python manage.py shell
```

Then execute:
```python
from django.contrib.auth.models import Group, Permission

permissions = []
for model in ['question', 'choice', 'recommendation', 'scoringmodel', 'valuerange']:
    for permission in ['add', 'change', 'delete', 'view']:
        permissions.append(Permission.objects.get_by_natural_key(f'{permission}_{model}', 'scoringengine', model))

for model in ['lead']:
    for permission in ['delete', 'view']:
        permissions.append(Permission.objects.get_by_natural_key(f'{permission}_{model}', 'scoringengine', model))

for model in ['answer', 'tokenproxy']:
    for permission in ['view']:
        permissions.append(Permission.objects.get_by_natural_key(f'{permission}_{model}', 'scoringengine', model))

g = Group.objects.create(name='Regular admin')
g.permissions.set(permissions)
g.save()
```

### Frontend Configuration

#### Environment Variables
```bash
# Required
VITE_API_BASE_URL=https://your-backend-domain.railway.app/api/v1

# Optional
VITE_APP_NAME=Scoring Engine Admin
VITE_APP_VERSION=1.0.0
```

#### Build Configuration
The frontend uses Vite, which is already configured for production builds.

## 🧪 Testing Deployment

### Backend Testing
```bash
# Test API endpoints
curl https://your-backend-domain.railway.app/api/v1/questions/

# Should return authentication error (expected)
```

### Frontend Testing
1. Visit your Vercel frontend URL
2. Try to log in with your superuser credentials
3. Test the dashboard and navigation
4. Verify API connections

## 🔒 Security Considerations

### Backend Security
- ✅ HTTPS enabled (Railway provides this)
- ✅ CORS protection configured
- ✅ Token-based authentication
- ✅ User-scoped data access
- ✅ Input validation

### Frontend Security
- ✅ Environment variables for sensitive data
- ✅ Token storage in localStorage (consider httpOnly cookies for production)
- ✅ Protected routes
- ✅ Error handling

## 📊 Monitoring

### Railway Monitoring
- **Logs**: View application logs in Railway dashboard
- **Metrics**: Monitor resource usage
- **Deployments**: Track deployment status

### Vercel Monitoring
- **Analytics**: Built-in analytics
- **Performance**: Core Web Vitals
- **Deployments**: Automatic deployments from Git

## 🚨 Troubleshooting

### Common Issues

#### CORS Errors
- Verify CORS_ALLOWED_ORIGINS includes your frontend domain
- Check that CORS middleware is properly configured
- Ensure frontend is sending proper headers

#### Authentication Issues
- Verify API token is being sent correctly
- Check that user has proper permissions
- Ensure token is not expired

#### Database Connection Issues
- Verify DATABASE_URL is correct
- Check if PostgreSQL service is running
- Ensure database exists and is accessible

#### Build Issues
- Check that all dependencies are installed
- Verify environment variables are set
- Check for TypeScript errors

### Getting Help
1. Check the logs in Railway/Vercel dashboards
2. Review the API documentation
3. Test endpoints with Postman or similar
4. Check browser developer tools for frontend issues

## 💰 Cost Optimization

### Railway Costs
- **Free Tier**: $5 credit monthly
- **Production**: ~$10-20/month depending on usage
- **Database**: Included in Railway pricing

### Vercel Costs
- **Free Tier**: Unlimited for personal projects
- **Pro Plan**: $20/month for teams

### Total Estimated Cost: $10-40/month

## 🎯 Next Steps

1. **Set up monitoring** with Railway's built-in tools
2. **Configure custom domains** for both frontend and backend
3. **Set up CI/CD** for automated deployments
4. **Implement backup strategy** for database
5. **Add performance monitoring**
6. **Set up error tracking** (Sentry, etc.)

## 📞 Support

For deployment issues:
1. Check Railway documentation: [docs.railway.app](https://docs.railway.app)
2. Check Vercel documentation: [vercel.com/docs](https://vercel.com/docs)
3. Review the API documentation
4. Check deployment logs

---

**Your integrated scoring engine is now ready for production!** 🚀
