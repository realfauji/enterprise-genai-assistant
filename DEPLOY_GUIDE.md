# 🚀 Enterprise GenAI Assistant — Deployment Guide
## PART 1: Run CMD in Local
### Step 1 — Install Dependencies
```bash
cd enterprise-genai-assistant
python -m venv .venv

# Mac/Linux:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate

pip install -r requirements.txt
```

### Step 2 — Start PostgreSQL (Docker se, easiest hai)
```bash
docker run --name genai-db \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=genaidb \
  -p 5432:5432 \
  -d postgres:15
```

> If not have docker, then install postgresql:
> https://www.postgresql.org/download/


### Step 3 — Create .env file
```bash
cp .env.example .env
```
Put values into `.env` file:

```env
DATABASE_URL=postgresql+asyncpg://admin:secret@localhost:5432/genaidb
JWT_SECRET=create_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

DEFAULT_LLM_PROVIDER=groq

OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...        # FREE:Create by going console.groq.com

HF_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
HF_API_KEY=hf_...           # FREE: huggingface.co/settings/tokens

DAILY_TOKEN_LIMIT=100000
BACKEND_URL=http://localhost:8000
```

### Step 4 — Create Database tables (Only first time)
```bash
python init_tables.py
```

Output should be: `All tables created successfully!`

### Step 5 — Run Backend
```bash
uvicorn app.main:app --reload --port 8000
```

Browser mein check karo: http://localhost:8000
Response should be: `{"status": "Running"}`

### Step 6 — Run Frontend (On new terminal)
```bash
streamlit run frontend/app.py
```

Browser open: http://localhost:8501

## PART 2: Deploy on Railway Platform
### Step 1 — Push code into GitHub
```bash
cd enterprise-genai-assistant

git init
git add .
git commit -m "initial commit"

git remote add origin https://github.com/{your_username}/enterprise-genai-assistant.git
git branch -M main
git push -u origin main
```

### Step 2 — Create Railway account
1. Go To: **railway.app**
2. **"Login with GitHub"**
3. Connect GitHub account

### Step 3 — Create PostgreSQL Database
1. Go to Railway Dashboard and click **"New Project"**
2. Select **"Add Service"** → **"Database"** → **"PostgreSQL"**
3. After creation of Database, open **"Variables"**
4. Copy `DATABASE_URL` (format: `postgresql+asyncpg://username:password@host:port/db_name`)

### Step 4 — Deploy Backend Service
1. Click **"Add Service"** → **"GitHub Repo"** into Project
2. Select your repo
3. After the creation of service, go to **"Settings"** tab:
   - **Dockerfile Path:** `Dockerfile.backend`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Go to **"Variables"** tab, add below variables:

```
DATABASE_URL          = postgresql+asyncpg://... (Step 3)
JWT_SECRET            = your_secret_key
JWT_ALGORITHM         = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 60
DEFAULT_LLM_PROVIDER  = groq
OPENAI_API_KEY        = sk-...
GROQ_API_KEY          = gsk_...
HF_EMBEDDING_MODEL    = sentence-transformers/all-MiniLM-L6-v2
HF_API_KEY            = hf_...
DAILY_TOKEN_LIMIT     = 100000
BACKEND_URL           = (keep it blank, and update later)
```

5. Start **"Deployments"** tab and see logs.
6. After Deployment, go to **"Settings"** → **"Networking"** → **"Generate Domain"** and click
7. Copy the URL, e.g.: `https://enterprise-backend-abc123.railway.app`


### Step 5 — Create DB Tables (Only First time on Railway)
Go to Backend service **"Settings"** and **"Deploy"** section:
- change the Temporarily Start Command: `python init_tables.py`
- Do Deploy, and see logs
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 6 — Frontend Service Deploy
1. Again go to **"Add Service"** → **"GitHub Repo"** → same repo
2. **"Settings"** tab:
   - **Dockerfile Path:** `Dockerfile.frontend`
   - **Start Command:** `streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
3. Go to **"Variables"** tab and add below variables:

```
DATABASE_URL          = postgresql+asyncpg://... (same as backend)
JWT_SECRET            = same as backend
JWT_ALGORITHM         = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 60
DEFAULT_LLM_PROVIDER  = groq
OPENAI_API_KEY        = sk-...
GROQ_API_KEY          = gsk_...
HF_EMBEDDING_MODEL    = sentence-transformers/all-MiniLM-L6-v2
HF_API_KEY            = hf_...
DAILY_TOKEN_LIMIT     = 100000
BACKEND_URL           = https://enterprise-backend-abc123.railway.app  ← Step 4 URL
```

4. Wait to complete deploy.
5. Create Frontend **"Generate Domain"**.
6. Open the Url - app ready! 🎉

### Step 7 — Update BACKEND_URL into Backend
1. Backend service → **"Variables"**
2. `BACKEND_URL` = Paste Backend URL
3. It will redeploy automatically.

## Quick Reference — Where to get API Keys?
| Key | Website | Cost |
|-----|---------|------|
| GROQ_API_KEY | console.groq.com | FREE |
| OPENAI_API_KEY | platform.openai.com | Paid |
| HF_API_KEY | huggingface.co/settings/tokens | FREE |

## Common Errors & Fix
| Error | Fix |
|-------|-----|
| `asyncpg` connection error | change URL `postgresql://` → `postgresql+asyncpg://` |
| Tables not found | `python init_tables.py` run this |
| CORS error on frontend | Allow frontend URL into Backend `main.py` |
| HF model download slow | First time it will take time because model creates a cache |
