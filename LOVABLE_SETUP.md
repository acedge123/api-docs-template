# 🚀 Lovable Setup Guide

## **Quick Start for Lovable Team**

This guide will get you up and running with the Lead Scoring Engine frontend in minutes!

### **Prerequisites**
- ✅ Node.js 18+ and npm 8+
- ✅ Git

---

## **📋 Setup Steps**

### **1. Clone the Repository**
```bash
git clone https://github.com/acedge123/lead-scoring-documentation.git
cd lead-scoring-documentation
```

### **2. Install Dependencies**
```bash
npm install
```
**This will generate the required `package-lock.json` file.**

### **3. Start Development Server**
```bash
npm run dev
```

### **4. Build Commands**
```bash
npm run build:dev    # Development build (fast)
npm run build        # Production build (with TypeScript)
npm run preview      # Preview production build
```

---

## **✅ What's Already Fixed**

### **TypeScript Configuration**
- ✅ `tsconfig.node.json` properly configured with `"noEmit": false`
- ✅ Project references working correctly
- ✅ No compilation issues

### **Project Structure**
- ✅ Root-level frontend project (not a workspace)
- ✅ All dependencies in `package.json`
- ✅ Vite configuration ready
- ✅ Tailwind CSS configured

---

## **🚨 Troubleshooting**

### **If you get TypeScript errors:**
1. **Verify `tsconfig.node.json` contains:**
   ```json
   {
     "compilerOptions": {
       "composite": true,
       "skipLibCheck": true,
       "module": "ESNext",
       "moduleResolution": "bundler",
       "allowSyntheticDefaultImports": true,
       "noEmit": false  // ← This is crucial!
     },
     "include": ["vite.config.*"]
   }
   ```

2. **Run `npm install`** to ensure all dependencies are installed
3. **Check that `node_modules` directory exists**

### **If build fails:**
1. **Verify Node.js version is 18+**
2. **Clear `node_modules` and run `npm install` again**
3. **Check for any syntax errors in source files**

---

## **🎯 Available Scripts**

| Script | Description |
|--------|-------------|
| `npm run dev` | Start development server |
| `npm run build:dev` | Build for development (skips TypeScript) |
| `npm run build` | Build for production (with TypeScript) |
| `npm run preview` | Preview production build |

---

## **�� Project Structure**

```
lead-scoring-documentation/
├── src/                    # React components and pages
├── index.html             # Main HTML file
├── vite.config.ts         # Vite configuration
├── tsconfig.json          # TypeScript configuration
├── tsconfig.node.json     # Node-specific TypeScript config ✅
├── tailwind.config.js     # Tailwind CSS configuration
├── postcss.config.js      # PostCSS configuration
└── package.json           # Dependencies and scripts
```

---

## **🔧 Key Features**

- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **Responsive design** for all devices
- **Documentation tabs** for easy navigation
- **Admin interface** integration

---

## **📞 Need Help?**

If you encounter any issues:

1. **Check this guide first**
2. **Verify Node.js version is 18+**
3. **Ensure `tsconfig.node.json` has `"noEmit": false`**
4. **Run `npm install` to regenerate dependencies**

---

**🎉 You're all set! The TypeScript configuration issues have been resolved, and you should be able to run `npm run dev` without any problems.**
