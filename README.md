# FontGen

FontGen turns handwriting templates and title images into installable TTF files. It also exports a transparent PNG cutout for compositing 3D title artwork in CapCut.

## Run locally

### Backend

```powershell
cd backend
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Set `GEMINI_API_KEY` to enable AI completion for the `ai` and `style` modes.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Set `VITE_API` when the backend is not running on `http://localhost:8000`.
