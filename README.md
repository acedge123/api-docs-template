# Scoring Engine - Integrated Solution

A modern scoring and recommendation engine with a beautiful admin interface, built with Django and React.

## 🚀 Features

### Backend (Django)
- **Question Management**: Create and manage different types of questions
- **Scoring Models**: Configure complex scoring formulas and value ranges
- **Recommendations**: Set up rule-based recommendations with affiliate links
- **Lead Processing**: Calculate scores and provide personalized recommendations
- **Analytics**: Comprehensive reporting and insights
- **REST API**: Full CRUD operations for all entities

### Frontend (React + TypeScript)
- **Modern Admin Interface**: Built with React, TypeScript, and Tailwind CSS
- **Real-time Updates**: Live data synchronization
- **Responsive Design**: Works on desktop and mobile
- **Authentication**: Secure token-based authentication
- **Analytics Dashboard**: Beautiful charts and insights
- **Documentation**: Built-in API documentation

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Django API    │    │   PostgreSQL    │
│   (Vercel)      │◄──►│   (Railway)     │◄──►│   (Railway)     │
│                 │    │                 │    │                 │
│ • React Admin   │    │ • Admin APIs    │    │ • Questions     │
│ • Authentication│    │ • Lead Scoring  │    │ • Scoring Models│
│ • Analytics     │    │ • Analytics     │    │ • Leads         │
│ • Documentation │    │ • CORS Enabled  │    │ • Users         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
scoring-engine-integrated/
├── frontend/                 # React + TypeScript admin interface
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/           # Page components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── lib/             # Utility functions
│   │   └── utils/           # Helper functions
│   ├── package.json
│   └── ...
├── backend/                  # Django API
│   ├── api/                 # API endpoints
│   ├── scoringengine/       # Core scoring logic
│   ├── users/               # User management
│   ├── manage.py
│   └── ...
├── README.md
├── API_DOCUMENTATION.md
├── DEPLOYMENT_GUIDE.md
└── IMPLEMENTATION_SUMMARY.md
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+ and pip
- PostgreSQL (for production)

### Local Development

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements/local.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Production Deployment

#### Backend (Railway)
1. Push backend code to GitHub
2. Connect to Railway
3. Set environment variables
4. Deploy

#### Frontend (Vercel)
1. Push frontend code to GitHub
2. Connect to Vercel
3. Set environment variables
4. Deploy

## 📚 Documentation

- [API Documentation](API_DOCUMENTATION.md) - Complete API reference
- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Step-by-step deployment instructions
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md) - Technical details

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```bash
DATABASE_URL=postgresql://...
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
```

#### Frontend (.env)
```bash
VITE_API_BASE_URL=https://your-backend-domain.railway.app/api/v1
```

## 🎯 Key Features

### Question Types
- **Open**: Text input questions
- **Choices**: Single selection from options
- **Multiple Choices**: Multiple selections allowed
- **Slider**: Numeric range input
- **Integer**: Numeric input
- **Date**: Date picker

### Scoring System
- **X-axis and Y-axis scoring**: Multi-dimensional scoring
- **Formula-based calculations**: Complex mathematical expressions
- **Value ranges**: Configurable point assignments
- **Weighted scoring**: Adjustable question weights

### Recommendations
- **Rule-based logic**: Conditional recommendations
- **Affiliate integration**: Links and tracking
- **Multi-channel**: Text, images, and redirects
- **A/B testing**: Multiple recommendation options

### Analytics
- **Lead summary**: Overview statistics
- **Question analytics**: Response distribution
- **Recommendation effectiveness**: Performance tracking
- **Score distribution**: Visual insights

## 🔒 Security

- **Token-based authentication**: Secure API access
- **User-scoped data**: Data isolation
- **CORS protection**: Cross-origin security
- **Input validation**: Comprehensive validation
- **SQL injection protection**: Django ORM security

## 💰 Cost Estimate

- **Railway (Backend)**: $10-20/month
- **Vercel (Frontend)**: Free tier available
- **Total**: $10-40/month depending on usage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
1. Check the documentation
2. Review the API documentation
3. Check deployment guides
4. Open an issue on GitHub

---

**Built with ❤️ using Django, React, TypeScript, and Tailwind CSS**
