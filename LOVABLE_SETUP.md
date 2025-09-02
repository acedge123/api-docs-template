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

### **2. ⚠️ CRITICAL: Manual TypeScript Configuration Fix Required**

**The TypeScript configuration files are read-only in this environment and require manual fixes outside of Lovable to resolve the project reference error.**

**You must manually edit `tsconfig.node.json` before proceeding:**

1. **Open `tsconfig.node.json` in your code editor**
2. **Replace the entire content with:**
   ```json
   {
     "compilerOptions": {
       "composite": true,
       "skipLibCheck": true,
       "module": "ESNext",
       "moduleResolution": "bundler",
       "allowSyntheticDefaultImports": true,
       "noEmit": false
     },
     "include": ["vite.config.*"]
   }
   ```
3. **Save the file and commit to git**

### **3. Install Dependencies**
```bash
npm install
```
**This will generate the required `package-lock.json` file.**

### **4. Start Development Server**
```bash
npm run dev
```

### **5. Build Commands**
```bash
npm run build:dev    # Development build (fast)
npm run build        # Production build (with TypeScript)
npm run preview      # Preview production build
```

---

## **🚨 Why Manual Fix is Critical**

The `"noEmit": false` setting in `tsconfig.node.json` resolves TypeScript project reference requirements. Without this fix:

- ❌ `npm run dev` will fail with compilation errors
- ❌ TypeScript project references won't work
- ❌ Build process will be blocked

**This is a one-time manual fix that cannot be automated in this environment.**

---

## **✅ What's Already Fixed**

### **Project Structure**
- ✅ Root-level frontend project (not a workspace)
- ✅ All dependencies in `package.json`
- ✅ Vite configuration ready
- ✅ Tailwind CSS configured

---

## **🔧 Troubleshooting**

### **If you still get TypeScript errors after the manual fix:**
1. **Verify `tsconfig.node.json` contains the exact configuration above**
2. **Run `npm install` to ensure all dependencies are installed**
3. **Check that `node_modules` directory exists**
4. **Clear `node_modules` and run `npm install` again if needed**

### **If build fails:**
1. **Verify Node.js version is 18+**
2. **Ensure the manual TypeScript fix was applied**
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

## **📁 Project Structure**

```
lead-scoring-documentation/
├── src/                    # React components and pages
├── index.html             # Main HTML file
├── vite.config.ts         # Vite configuration
├── tsconfig.json          # TypeScript configuration
├── tsconfig.node.json     # Node-specific TypeScript config ⚠️ MANUAL FIX REQUIRED
├── tailwind.config.js     # Tailwind CSS configuration
├── postcss.config.js      # PostCSS configuration
└── package.json           # Dependencies and scripts
```

---

## **🔒 Manual Fix Process for Lovable**

1. **Clone the repository** to their local machine
2. **Manually edit `tsconfig.node.json`** with the correct configuration
3. **Commit and push** the fixed configuration
4. **Then run** `npm install` and `npm run dev`

This ensures the TypeScript project reference error is resolved before attempting to run the development server.

---

## **📞 Need Help?**

If you encounter any issues:

1. **Check this guide first**
2. **Verify the manual TypeScript fix was applied**
3. **Ensure Node.js version is 18+**
4. **Run `npm install` to regenerate dependencies**

---

**🎉 After applying the manual TypeScript fix, you should be able to run `npm run dev` without any problems!**
