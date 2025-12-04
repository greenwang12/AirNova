# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from .db import create_db_and_tables

# Routers
from .routes.customers import router as customers_router
from .routes.flights import router as flights_router
from .routes.bookings import router as bookings_router
from .routes import auth
from .routes.groups import router as groups_router
from .routes.notifications import router as notifications_router
from .routes.price_evaluate import router as price_eval_router
from .routes.companies import router as companies_router
from .routes.price_predict import router as price_predict_router


app = FastAPI(
    title="Flights API",
    version="1.0",
    openapi_url="/_openapi.json",  # internal schema for Swagger only
    docs_url="/docs",
    redoc_url=None,
)

@app.on_event("startup")
def startup_event():
    create_db_and_tables()

@app.get("/", response_class=HTMLResponse, tags=["Home"])
def homepage():
    return """
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width,initial-scale=1" />
      <title>Flights Management • API</title>
      <style>
        /* Base (light) theme variables */
        :root{
          --page-bg: #f4f7fb;
          --card-bg: #ffffff;
          --muted: #6b7280;
          --accent: #2f6fff;
          --title-color: #071025;
          --shadow: 0 10px 30px rgba(19,30,66,0.06);
          --footer-bg: transparent;
          --link-color: var(--accent);
          --toggle-bg: #fff;
          --toggle-border: rgba(11,105,255,0.08);
        }

        /* Dark theme variables (applied when body.dark-mode exists) */
        body.dark-mode{
          --page-bg: #071024;          /* overall page background */
          --card-bg: #0b1220;          /* card background */
          --muted: #9aa3b3;            /* muted text on dark */
          --accent: #7c9cff;           /* slightly brighter accent */
          --title-color: #ffffff;      /* title becomes white */
          --shadow: 0 24px 60px rgba(2,6,23,0.6);
          --footer-bg: rgba(255,255,255,0.02);
          --link-color: #9fb6ff;
          --toggle-bg: transparent;
          --toggle-border: rgba(255,255,255,0.06);
        }

        html,body{height:100%;margin:0;background:var(--page-bg);font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,"Helvetica Neue",Arial;color:var(--title-color);transition:background .24s ease,color .18s ease}
        .wrap{min-height:100vh;display:flex;align-items:center;justify-content:center;padding:48px;}
        .card{background:var(--card-bg);border-radius:14px;box-shadow:var(--shadow);padding:36px;width:900px;max-width:96%;display:flex;gap:28px;align-items:center;transition:background .24s ease, box-shadow .24s ease, color .18s ease}
        .left{flex:1}
        h1{margin:0;font-size:28px;color:var(--title-color);font-weight:700;transition:color .18s ease;}
        .lead{color:var(--muted);margin-top:10px;margin-bottom:18px;line-height:1.5}
        .actions{display:flex;gap:12px;align-items:center;margin-top:10px}
        .btn{background:var(--accent);color:white;padding:12px 18px;border-radius:10px;text-decoration:none;font-weight:600;border:0;cursor:pointer;box-shadow:none}
        .meta{font-size:13px;color:var(--muted);margin-top:14px}
        .right{width:200px;text-align:right}
        .status-title{font-size:13px;color:var(--muted)}
        .status{font-size:20px;font-weight:700;color:var(--accent);margin-top:6px}
        .footer{width:100%;text-align:center;margin-top:20px;color:var(--muted);font-size:13px;padding:18px 0;background:var(--footer-bg);border-top-left-radius:0;border-top-right-radius:0;transition:background .24s ease}
        .theme-toggle{background:var(--toggle-bg);border:1px solid var(--toggle-border);padding:10px;border-radius:8px;cursor:pointer;color:var(--title-color)}
        a { color: var(--link-color); transition: color .18s ease; }

        @media (max-width:820px){
          .card{flex-direction:column;align-items:flex-start}
          .right{text-align:left;width:100%}
        }
      </style>
    </head>
    <body>
      <div class="wrap">
        <div class="card" id="mainCard" role="main" aria-labelledby="title">
          <div class="left">
            <h1 id="title">Flights Management System</h1>
            <div class="lead">A minimal, production-style API backend for managing flights, customers and bookings.</div>

            <div class="actions">
              <a class="btn" href="/docs">Open API Docs</a>
              <button id="themeToggle" class="theme-toggle" aria-pressed="false" title="Toggle dark theme">Toggle dark theme</button>
            </div>

            <div class="meta">
              <span style="font-weight:600;color:var(--accent)">v1.0</span> · Last updated: <span id="updated">2025-11-16</span>
            </div>
          </div>

          <div class="right">
            <div class="status-title">Status</div>
            <div class="status">Server running</div>
            <div style="margin-top:12px;color:var(--muted)">Docs: <a href="/docs">/docs</a></div>
          </div>
        </div>
      </div>

      <div class="footer">© 2025 Flights Management System — Built with FastAPI</div>

      <script>
        (function(){
          const KEY = 'flights_theme_dark';
          const btn = document.getElementById('themeToggle');
          const body = document.body;

          // set updated date
          const d = new Date();
          document.getElementById('updated').textContent = d.toISOString().split('T')[0];

          // initialize from storage
          const saved = localStorage.getItem(KEY);
          const isDark = saved === '1';
          if (isDark) {
            body.classList.add('dark-mode');
            btn.textContent = 'Switch to light theme';
            btn.setAttribute('aria-pressed','true');
          } else {
            btn.textContent = 'Toggle dark theme';
            btn.setAttribute('aria-pressed','false');
          }

          // keyboard accessible toggle (space/enter will also toggle)
          btn.addEventListener('click', toggle);
          btn.addEventListener('keyup', (e) => { if (e.key === 'Enter' || e.key === ' ') toggle(); });

          function toggle(){
            const nowDark = body.classList.toggle('dark-mode');
            localStorage.setItem(KEY, nowDark ? '1' : '0');
            btn.textContent = nowDark ? 'Switch to light theme' : 'Toggle dark theme';
            btn.setAttribute('aria-pressed', String(nowDark));
          }
        })();
      </script>
    </body>
    </html>
    """
# Hide the default /openapi.json
@app.get("/openapi.json")
def block_openapi_json():
    raise HTTPException(status_code=404, detail="Not Found")

# Routers
app.include_router(customers_router)
app.include_router(flights_router)
app.include_router(bookings_router)
app.include_router(auth.router)
app.include_router(groups_router)
app.include_router(notifications_router)
app.include_router(price_eval_router)
app.include_router(price_predict_router)
app.include_router(companies_router)
