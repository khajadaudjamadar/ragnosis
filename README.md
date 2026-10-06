# RAGnosis

Medical report RAG + hospital portal.
**Stack:** Flask 3 · React 18 + Vite · MongoDB Atlas · MiniLM + FAISS (retrieval) · Groq LLaMA-3 (answers) · optional BioBERT (entities) and BART (summary).

Patients and doctors sign in, upload a report (PDF/TXT), and ask questions about it. Answers are generated only from the retrieved report passages, with sources shown.

## 1. Prerequisites (Mac and Windows)
| Tool | Version | Check |
|---|---|---|
| Python | 3.10 - 3.12 | `python3 --version` (Windows: `python --version`) |
| Node.js | 18+ | `node --version` |
| Git | any | `git --version` |

Free accounts: [MongoDB Atlas](https://www.mongodb.com/atlas) (database) and [Groq](https://console.groq.com) (API key).

## 2. Install
**Mac / Linux:** `bash setup_mac.sh`
**Windows:** `setup_windows.bat`

Manual alternative (same on both, activation differs):
```
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # Windows: copy .env.example .env
cd ../frontend
npm install
```
The first install downloads PyTorch (large). Be patient.

## 3. Configure `backend/.env`
- `GROQ_API_KEY` : paste your Groq key. Without it the app still runs and returns the most relevant passages instead of an AI answer.
- `MONGO_URI` : Atlas > Connect > Drivers > copy the `mongodb+srv://...` string and put your password in it. In Atlas, also add your IP under Network Access.
- No Atlas yet? Leave `MONGO_URI` empty to use a temporary in-memory database (data lost on restart).
- `ENABLE_NER` / `ENABLE_SUMMARY` : set to `true` later to turn on BioBERT entities and BART summaries (extra model downloads).
- Set long random values for `SECRET_KEY` and `JWT_SECRET_KEY`.

## 4. Run (two terminals)
**Terminal 1, backend**
```
cd backend
source venv/bin/activate          # Windows: venv\Scripts\activate
python app.py
```
Runs at http://localhost:5000 (check http://localhost:5000/api/health).

**Terminal 2, frontend**
```
cd frontend
npm run dev
```
Open http://localhost:5173, register as patient or doctor, and upload a report. The first upload is slow because the MiniLM model downloads once.

## 5. Project layout
```
backend/
  app.py  config.py  extensions.py
  routes/    auth.py  reports.py  chat.py
  services/  pdf_utils chunker embedder vector_store llm rag ner summarizer
  data/      uploads/ (files)  indexes/ (FAISS per report)
frontend/src/
  App.jsx  api.js  pages/ Login Dashboard ReportChat
```

## 6. API
| Method | Path | Purpose |
|---|---|---|
| POST | /api/auth/register, /api/auth/login | Auth (returns JWT) |
| GET | /api/auth/me | Current user |
| POST | /api/reports | Upload report (multipart: file, title, patient_email for doctors) |
| GET | /api/reports | Patients: own reports. Doctors: all |
| GET / DELETE | /api/reports/:id | Report details / delete |
| POST | /api/reports/:id/ask | `{question}` returns answer and sources |
| GET | /api/reports/:id/history | Chat history |

## 7. Put it on GitHub
1. Create an empty repo on github.com (no README, no .gitignore).
2. In the project root:
```
git init
git add .
git commit -m "Initial commit: RAGnosis"
git branch -M main
git remote add origin https://github.com/<your-username>/ragnosis.git
git push -u origin main
```
3. `.gitignore` already excludes `.env`, `venv`, `node_modules` and uploaded reports. Never commit your keys.
4. Teammates clone the repo, run the setup script, and create their own `backend/.env`.
Suggested workflow for a team of 4: one branch per feature (`git checkout -b feature/name`), then open a Pull Request into `main`.

## 8. Troubleshooting
- **Atlas connection or SSL error:** whitelist your IP in Atlas Network Access and check the password in the URI (URL-encode special characters).
- **`faiss` or `torch` install fails:** use Python 3.10 - 3.12, not 3.13.
- **Port 5000 busy on Mac:** AirPlay uses it. Change the port in `app.py` and the proxy in `frontend/vite.config.js`.
- **Scanned PDF rejected:** only text-based PDFs are supported (no OCR).

> Informational tool only. Not a substitute for professional medical advice.
