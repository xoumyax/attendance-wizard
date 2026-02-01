# 🚀 Attendance Tracker Deployment Guide

This guide covers multiple deployment options for your attendance tracking application.

---

## 📋 Pre-Deployment Checklist

Before deploying, ensure you have:

- ✅ All code committed to a Git repository (GitHub recommended)
- ✅ Database seeded with students and sessions
- ✅ Environment variables configured
- ✅ Requirements.txt is up to date

---

## 🌐 Option 1: Render (Recommended - Free Tier Available)

**Pros:** Easy setup, free tier, automatic deployments, persistent storage
**Time:** ~5 minutes

### Steps:

1. **Push code to GitHub**
   ```bash
   cd /Users/soumyajyotidutta/Desktop/AttendanceTracker/attendanceWizard
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Create Render Account**
   - Go to https://render.com
   - Sign up with GitHub

3. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name:** attendance-tracker
     - **Runtime:** Python 3
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables**
   - `SECRET_KEY`: Generate a secure key
   - `DATABASE_URL`: `sqlite:///./attendance.db`
   - `ADMIN_PASSWORD`: Your admin password

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (~2-3 minutes)
   - Your app will be at: `https://attendance-tracker.onrender.com`

6. **Seed Database (First Time Only)**
   - Use Render Shell to run:
   ```bash
   python import_students_csv.py /path/to/csv
   python seed_sessions.py
   python seed_test_students.py
   ```

**Note:** Free tier sleeps after 15 min of inactivity. First request may take 30-60 seconds.

---

## 🚂 Option 2: Railway (Simple & Fast)

**Pros:** Very easy, generous free tier, automatic HTTPS
**Time:** ~3 minutes

### Steps:

1. **Push to GitHub** (same as above)

2. **Deploy to Railway**
   - Go to https://railway.app
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository

3. **Configure**
   - Railway auto-detects Python
   - Add environment variables in Settings
   - Railway provides a public URL automatically

4. **Seed Database**
   - Use Railway CLI or web shell

---

## 🐳 Option 3: Docker Deployment

**Pros:** Works anywhere, reproducible, easy scaling
**Time:** ~10 minutes

### Build and Run Locally:

```bash
cd /Users/soumyajyotidutta/Desktop/AttendanceTracker/attendanceWizard

# Build Docker image
docker build -t attendance-tracker .

# Run container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/attendance.db:/app/attendance.db \
  --name attendance-app \
  attendance-tracker

# Access at http://localhost:8000
```

### Deploy to Any Cloud with Docker:

**DigitalOcean App Platform:**
- Connect GitHub repo
- Select Dockerfile
- Deploy with one click

**AWS ECS / Azure Container Instances:**
- Push image to ECR/ACR
- Create container instance
- Configure port 8000

**Heroku:**
```bash
heroku container:login
heroku create attendance-tracker-app
heroku container:push web
heroku container:release web
```

---

## ☁️ Option 4: Azure App Service

**Pros:** Enterprise-grade, integrates with Azure services, good for .edu domains
**Time:** ~15 minutes

### Steps:

1. **Install Azure CLI**
   ```bash
   brew install azure-cli
   az login
   ```

2. **Create App Service**
   ```bash
   cd /Users/soumyajyotidutta/Desktop/AttendanceTracker/attendanceWizard
   
   # Create resource group
   az group create --name attendance-rg --location eastus
   
   # Create App Service plan
   az appservice plan create \
     --name attendance-plan \
     --resource-group attendance-rg \
     --sku B1 \
     --is-linux
   
   # Create web app
   az webapp create \
     --resource-group attendance-rg \
     --plan attendance-plan \
     --name attendance-tracker-tamu \
     --runtime "PYTHON:3.11"
   
   # Deploy code
   az webapp up \
     --resource-group attendance-rg \
     --name attendance-tracker-tamu \
     --runtime "PYTHON:3.11"
   ```

3. **Configure Environment**
   ```bash
   az webapp config appsettings set \
     --resource-group attendance-rg \
     --name attendance-tracker-tamu \
     --settings SECRET_KEY="your-secret-key"
   ```

4. **Enable SSH and access shell to seed database**

---

## 🖥️ Option 5: VPS (DigitalOcean, Linode, AWS EC2)

**Pros:** Full control, cost-effective for long-term
**Time:** ~30 minutes

### Steps:

1. **Create VPS** (Ubuntu 22.04 recommended)

2. **SSH into server**
   ```bash
   ssh root@your-server-ip
   ```

3. **Install dependencies**
   ```bash
   # Update system
   apt update && apt upgrade -y
   
   # Install Python & pip
   apt install python3.11 python3.11-venv python3-pip nginx -y
   
   # Install supervisor for process management
   apt install supervisor -y
   ```

4. **Setup application**
   ```bash
   # Create app directory
   mkdir -p /var/www/attendance
   cd /var/www/attendance
   
   # Clone repo
   git clone YOUR_REPO_URL .
   
   # Create virtual environment
   python3.11 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Seed database
   python import_students_csv.py /path/to/csv
   python seed_sessions.py
   python seed_test_students.py
   ```

5. **Configure Supervisor**
   ```bash
   nano /etc/supervisor/conf.d/attendance.conf
   ```
   
   Add:
   ```ini
   [program:attendance]
   directory=/var/www/attendance
   command=/var/www/attendance/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
   user=www-data
   autostart=true
   autorestart=true
   stderr_logfile=/var/log/attendance.err.log
   stdout_logfile=/var/log/attendance.out.log
   ```
   
   Start:
   ```bash
   supervisorctl reread
   supervisorctl update
   supervisorctl start attendance
   ```

6. **Configure Nginx**
   ```bash
   nano /etc/nginx/sites-available/attendance
   ```
   
   Add:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
       
       location /static {
           alias /var/www/attendance/static;
       }
   }
   ```
   
   Enable:
   ```bash
   ln -s /etc/nginx/sites-available/attendance /etc/nginx/sites-enabled/
   nginx -t
   systemctl restart nginx
   ```

7. **Setup SSL (Optional but recommended)**
   ```bash
   apt install certbot python3-certbot-nginx -y
   certbot --nginx -d your-domain.com
   ```

---

## 🔒 Production Checklist

Before going live, ensure:

### Security:
- [ ] Change `SECRET_KEY` to a random 32+ character string
- [ ] Set strong admin password
- [ ] Enable HTTPS/SSL
- [ ] Set `CORS` origins to your domain only
- [ ] Review and update `.env` file (don't commit it!)

### Database:
- [ ] Consider PostgreSQL for production (SQLite has limitations with concurrent writes)
- [ ] Setup automated backups
- [ ] Run all seed scripts

### Performance:
- [ ] Use a production ASGI server (uvicorn with multiple workers)
- [ ] Enable caching if needed
- [ ] Setup monitoring (Sentry, New Relic)

### Configuration:
```python
# In app/main.py, update CORS for production:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  # Specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🎓 Texas A&M Specific Deployment

If deploying for TAMU courses:

1. **Contact IT Services:**
   - Request a subdomain: `attendance.cse.tamu.edu`
   - Get access to TAMU hosting or approved cloud services

2. **Use TAMU CAS Authentication (Advanced):**
   - Integrate with TAMU's Single Sign-On
   - Replace UIN verification with CAS login

3. **Data Privacy:**
   - Ensure FERPA compliance
   - Store database securely
   - Setup regular backups
   - Consider encryption at rest

---

## 📊 Database Considerations

### SQLite (Current - Good for < 100 concurrent users)
- ✅ Simple, no setup needed
- ✅ Works for small to medium classes
- ❌ Limited concurrent writes
- ❌ File-based (backup carefully)

### PostgreSQL (Recommended for Production)
- ✅ Better concurrency
- ✅ More reliable for production
- ✅ Easy to setup on cloud platforms

**To switch to PostgreSQL:**

1. Update `requirements.txt`:
   ```
   psycopg2-binary==2.9.9
   ```

2. Update `config.py`:
   ```python
   DATABASE_URL: str = "postgresql://user:pass@host:5432/dbname"
   ```

3. Models work the same (SQLAlchemy handles it)

---

## 🔧 Deployment Commands Reference

### Render:
```bash
# Deploy on git push (automatic)
git push origin main
```

### Railway:
```bash
# Deploy on git push (automatic)
git push origin main
```

### Docker:
```bash
# Build
docker build -t attendance-tracker .

# Run
docker run -p 8000:8000 attendance-tracker

# Push to registry
docker tag attendance-tracker your-registry/attendance-tracker
docker push your-registry/attendance-tracker
```

### Heroku:
```bash
heroku login
heroku create
git push heroku main
heroku ps:scale web=1
heroku open
```

---

## 📱 Testing Your Deployment

After deployment:

1. **Test URLs:**
   - Student login: `https://your-app.com/`
   - Admin login: `https://your-app.com/admin/login`
   - Registration: `https://your-app.com/student/register`

2. **Test Flows:**
   - [ ] Admin can login (xoumyax / adminwizards@csce439704)
   - [ ] Admin can create sessions
   - [ ] Admin can generate tokens
   - [ ] Test student can login (999999991 / test123)
   - [ ] Student can mark attendance
   - [ ] Excel export works
   - [ ] Password reset works

3. **Check Logs:**
   - Look for any errors in application logs
   - Verify database connections
   - Test during peak usage time

---

## 🆘 Troubleshooting

### "Application Error" or 500 errors:
- Check logs for Python errors
- Verify all dependencies installed
- Check environment variables are set
- Ensure database file has write permissions

### Static files not loading:
- Check `STATIC_URL` configuration
- Verify static files are included in deployment
- Check Nginx configuration if using VPS

### Database not persisting:
- Ensure volume mounting (Docker)
- Check file permissions
- Verify DATABASE_URL path

### Slow performance:
- Use production ASGI server with workers
- Enable caching
- Consider PostgreSQL instead of SQLite
- Check database queries

---

## 📞 Support

For deployment issues:
- Check platform documentation (Render, Railway, etc.)
- Review error logs carefully
- Test locally first with `uvicorn app.main:app --host 0.0.0.0 --port 8000`

---

## 🎉 Quick Start (Render - Fastest)

1. Push to GitHub
2. Go to Render.com
3. Connect repo → Create Web Service
4. Wait 2 minutes
5. Done! 🚀

Your attendance tracker will be live at `https://your-app.onrender.com`
