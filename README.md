# Lead Scoring Engine - Subtree Bridge Architecture

<!-- Last updated: 2026-02-18 - Fixed onboarding path -->

A modern lead scoring system with a clean separation between frontend and backend, using a git subtree workflow for seamless collaboration.

## 🏗️ Architecture Overview

We run two repositories with a "Subtree Bridge" approach:

- **Frontend (FE)**: `acedge123/lead-scoring-documentation` (owned by Lovable, deployed on Vercel)
- **Backend (BE)**: `acedge123/api-docs-template` (owned by Cursor, deployed on Railway)

The frontend content is mirrored into the backend repo as a read-only convenience folder, maintaining clear ownership and deployment independence.

## 🎯 Core Principles

### **Single Source of Truth**
- **FE truth** = the FE repo (Lovable owns this)
- **BE truth** = the BE repo (Cursor owns this)
- **FE content in BE** = a mirror for convenience, never edited there

### **Predictable Location**
- Frontend content lives under `frontend/` in the BE repo
- Everyone assumes FE content is present but never edits it there
- Default flow: one-way pull from FE into BE

### **Deployment Independence**
- Railway deploys only the BE, reading from BE root
- Vercel deploys only the FE, reading from FE repo
- Changes in FE mirrored inside BE do not auto-deploy the frontend

## 👥 Roles & Responsibilities

### **Lovable (Frontend Team)**
- ✅ Own FE repo structure, build, and deployments
- ✅ Merge FE PRs in the FE repo as usual
- ✅ Notify Cursor when notable FE changes land
- ✅ Treat FE content inside BE repo as read-only

### **Cursor (Backend Team)**
- ✅ Own BE repo, Django app, migrations, and Railway deployment
- ✅ Maintain the vendored FE mirror under `frontend/` folder
- ✅ Refresh FE mirror on demand (before BE releases, when FE docs needed)
- ✅ Never assume BE mirror is ahead of FE

## 🔄 Lifecycle & Workflows

### **Day-to-Day Development**
1. **FE team** works exclusively in the FE repo
2. **BE team** works exclusively in the BE repo
3. **BE team** pulls latest FE into vendored folder when needed

### **Coordinated Releases**
1. **BE team** refreshes FE mirror before cutting release branch/tag
2. **FE deployment** remains independent
3. **No FE redeploy** triggered by BE actions

### **Exceptional "Push Back" to FE**
- **BE team** can propose small FE fixes (typos, doc tweaks)
- **Changes staged** in BE's vendored copy first
- **Then pushed upstream** to FE with clear communication
- **Lovable reviews/merges** in FE repo
- **BE mirror refreshed** afterward

## 🚀 Quick Start

### **For Lovable (Frontend)**
```bash
# Clone the frontend repository
git clone https://github.com/acedge123/lead-scoring-documentation.git
cd lead-scoring-documentation

# Install dependencies
npm install

# Start development server
npm run dev
```

### **For Cursor (Backend)**
```bash
# Clone the backend repository
git clone https://github.com/acedge123/api-docs-template.git
cd api-docs-template

# Frontend content is available in frontend/ folder
# Refresh with: git subtree pull --prefix=frontend origin main
```

## 📁 Project Structure

```
lead-scoring-documentation/          # Frontend Repo (Lovable)
├── src/                            # React components and pages
├── index.html                      # Main HTML file
├── vite.config.ts                  # Vite configuration
├── tsconfig.json                   # TypeScript configuration
├── tsconfig.node.json              # TypeScript configuration
├── package.json                    # Dependencies and scripts

api-docs-template/                   # Backend Repo (Cursor)
├── frontend/                       # Mirrored FE content (read-only)
├── api/                           # Django API endpoints
├── scoringengine/                 # Core scoring logic
├── manage.py                      # Django management
└── requirements/                  # Python dependencies
```

## 🔧 Available Scripts (Frontend)

| Script | Description |
|--------|-------------|
| `npm run dev` | Start development server |
| `npm run build:dev` | Build for development (skips TypeScript) |
| `npm run build` | Build for production (with TypeScript) |
| `npm run preview` | Preview production build |



## 🔄 Mirror Management

### **Refresh FE Mirror in BE (Cursor)**
```bash
# From BE repo root
git subtree pull --prefix=frontend origin main
```

### **Push FE Changes from BE (Coordinated)**
```bash
# Stage changes in BE's frontend/ folder
git add frontend/

# Commit with clear message
git commit -m "FE mirror changes for [specific purpose]"

# Push to FE repo (coordinated with Lovable)
git subtree push --prefix=frontend origin main
```

## 🚫 What NOT to Do

- ❌ **Never edit** FE content directly in BE repo
- ❌ **Never assume** BE mirror is current
- ❌ **Never mix** FE and BE changes in same PR
- ❌ **Never commit** secrets in either repo

## ✅ What Success Looks Like

- **Lovable ships** FE changes without touching BE
- **Cursor ships** BE changes without touching FE
- **BE team updates** FE mirror when needed (quick, low-risk sync)
- **No confusion** about "which repo is the real frontend"

## 📚 Documentation

- **API Documentation**: Available in the frontend documentation tabs
- **Backend API**: Django REST Framework with full CRUD operations

## 🤝 Support & Communication

### **For Frontend Issues**
- Check Vercel deployment logs
- Verify build process completes successfully
- Ensure Node.js version is 18+

### **For Backend Issues**
- Check Django logs and Railway deployment
- Verify database migrations
- Check API endpoint configurations

### **For Coordination**
- **FE changes**: Lovable notifies Cursor when mirror refresh needed
- **BE changes**: Cursor refreshes FE mirror before releases
- **Cross-team fixes**: Coordinate through clear communication

---

**🎯 TL;DR**: Frontend keeps its own repo and deployment. Backend keeps its own repo and deployment. We mirror the frontend into the backend repo as a read-only folder for convenience. Frontend is still the source of truth. No cross-repo surprises, no broken deploys.

**Built with ❤️ using Django, React, TypeScript, and Tailwind CSS**
# Trigger rebuild
