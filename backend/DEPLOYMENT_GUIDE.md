# Deployment Guide - Railway

This guide will help you deploy the Scoring Engine to Railway, a modern platform that's perfect for Django applications.

## Prerequisites

1. **GitHub Account** - Your code will be hosted on GitHub
2. **Railway Account** - Sign up at [railway.app](https://railway.app)
3. **Domain Name** (optional) - For custom domain

## Step 1: Prepare Your Repository

### 1.1 Fork/Copy the Repository
```bash
# Clone the repository to your local machine
git clone <original-repo-url>
cd hfc-scoring-engine

# Create a new repository on GitHub
# Then push to your new repository
git remote set-url origin <your-new-repo-url>
git push -u origin main
```

### 1.2 Update Environment Variables
Create a `.env` file for local development:
```bash
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/scoring_engine

# Django
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# CORS (update with your frontend domain)
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend-domain.vercel.app
```

### 1.3 Update CORS Settings
Edit `hfcscoringengine/settings/base.py` and update the CORS settings:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://your-frontend-domain.vercel.app",  # Your actual frontend domain
]
```

## Step 2: Deploy to Railway

### 2.1 Connect GitHub Repository
1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will automatically detect it's a Django project

### 2.2 Configure Environment Variables
In your Railway project dashboard, go to the "Variables" tab and add:

```bash
# Django Settings
DJANGO_SECRET_KEY=your-super-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-app-name.railway.app,your-custom-domain.com

# Database (Railway will provide this automatically)
DATABASE_URL=postgresql://...

# CORS Settings
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app,https://your-custom-domain.com

# Email (optional)
DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 2.3 Railway Configuration
Railway will automatically:
- Detect the Django project
- Install dependencies from `requirements/base.txt`
- Run migrations
- Start the application

### 2.4 Custom Domain (Optional)
1. In Railway dashboard, go to "Settings" tab
2. Click "Custom Domains"
3. Add your domain
4. Update DNS records as instructed

## Step 3: Database Setup

### 3.1 Run Migrations
Railway should automatically run migrations, but you can manually trigger them:
```bash
# In Railway dashboard, go to "Deployments" tab
# Click on the latest deployment
# Go to "Logs" and run:
python manage.py migrate
```

### 3.2 Create Superuser
```bash
# In Railway dashboard, go to "Deployments" tab
# Click on the latest deployment
# Go to "Logs" and run:
python manage.py createsuperuser
```

### 3.3 Create Admin Group
```bash
# In Railway dashboard, go to "Deployments" tab
# Click on the latest deployment
# Go to "Logs" and run:
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

## Step 4: Verify Deployment

### 4.1 Check API Endpoints
Test your API endpoints:
```bash
# Get your Railway app URL
curl https://your-app-name.railway.app/api/v1/questions/

# Should return authentication error (expected)
```

### 4.2 Test Authentication
```bash
# Get token
curl -X POST https://your-app-name.railway.app/api/token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your-username", "password": "your-password"}'

# Use token to access API
curl https://your-app-name.railway.app/api/v1/questions/ \
  -H "Authorization: Token your-token-here"
```

### 4.3 Check Admin Interface
Visit: `https://your-app-name.railway.app/admin/`

## Step 5: Frontend Integration

### 5.1 Update Frontend Configuration
In your React frontend, update the API base URL:
```javascript
// config/api.js
const API_BASE_URL = 'https://your-app-name.railway.app/api/v1';

export const apiClient = {
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
};
```

### 5.2 Test Frontend Connection
```javascript
// Test API connection
const response = await fetch(`${API_BASE_URL}/questions/`, {
  headers: {
    'Authorization': `Token ${token}`,
  },
});
```

## Step 6: Monitoring and Maintenance

### 6.1 Railway Dashboard
- **Deployments**: Monitor deployment status
- **Logs**: View application logs
- **Metrics**: Monitor performance
- **Variables**: Manage environment variables

### 6.2 Database Backups
Railway automatically handles PostgreSQL backups, but you can also:
1. Go to "Database" tab in Railway
2. Click "Backup" to create manual backup
3. Download backup file

### 6.3 Scaling
Railway automatically scales based on traffic, but you can:
1. Go to "Settings" tab
2. Adjust resource allocation
3. Enable auto-scaling

## Troubleshooting

### Common Issues

#### 1. Migration Errors
```bash
# Check migration status
python manage.py showmigrations

# Reset migrations if needed
python manage.py migrate --fake-initial
```

#### 2. CORS Issues
- Verify CORS_ALLOWED_ORIGINS includes your frontend domain
- Check that CORS middleware is properly configured
- Ensure frontend is sending proper headers

#### 3. Database Connection Issues
- Verify DATABASE_URL is correct
- Check if PostgreSQL service is running
- Ensure database exists and is accessible

#### 4. Static Files Not Loading
```bash
# Collect static files
python manage.py collectstatic --noinput
```

### Getting Help

1. **Railway Documentation**: [docs.railway.app](https://docs.railway.app)
2. **Railway Discord**: [discord.gg/railway](https://discord.gg/railway)
3. **Django Documentation**: [docs.djangoproject.com](https://docs.djangoproject.com)

## Cost Optimization

### Railway Pricing
- **Free Tier**: $5 credit monthly
- **Pay-as-you-go**: $0.000463 per GB-hour
- **Pro Plan**: $20/month for teams

### Optimization Tips
1. **Use free tier for development**
2. **Monitor resource usage**
3. **Optimize database queries**
4. **Use caching where appropriate**

## Security Considerations

### 1. Environment Variables
- Never commit secrets to Git
- Use Railway's secure variable storage
- Rotate secrets regularly

### 2. Database Security
- Use strong passwords
- Enable SSL connections
- Regular security updates

### 3. API Security
- Use HTTPS only
- Implement rate limiting
- Validate all inputs
- Use proper authentication

## Next Steps

1. **Set up monitoring** with Railway's built-in tools
2. **Configure custom domain** for production
3. **Set up CI/CD** for automated deployments
4. **Implement backup strategy**
5. **Add performance monitoring**

Your Django Scoring Engine is now deployed and ready to serve your frontend application!
