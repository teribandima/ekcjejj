from flask import Flask, jsonify, request, Response, render_string_template
import pymongo
from pymongo.errors import ConnectionFailure
from bson.errors import InvalidId
from bson import ObjectId
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)

# MongoDB connection
try:
    client = pymongo.MongoClient(
        os.environ.get('MONGO_URI', "mongodb+srv://elvishyadav_opm:naman1811421@cluster0.uxuplor.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"),
        serverSelectionTimeoutMS=5000
    )
    client.admin.command('ping')
    print("Connected to MongoDB successfully!")
except ConnectionFailure:
    print("Failed to connect to MongoDB. Please check your connection string or network.")
    exit(1)

db = client["unacademy_db"]
educators_col = db["educators"]

# HTML Template
HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Educators · Batches · Courses</title>
  <style>
    :root{
      --bg: #0b1020;
      --surface: #121832;
      --text: #e8ecf8;
      --muted: #9aa3b2;
      --primary: #2ea8ff;
      --accent: #ff6b6b;
      --success: #33ff66;
      --radius: 12px;
    }
    * { box-sizing: border-box; }
    html, body { height: 100%; }
    body{
      margin:0;
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height:1.5;
      overflow-x: hidden;
    }
    a { color: var(--primary); text-decoration: none; }
    a:hover { text-decoration: underline; }

    #bg-canvas{
      position: fixed;
      inset: 0;
      z-index: -1;
      display:block;
      background: radial-gradient(1000px 600px at 80% -10%, rgba(46,168,255,0.12), transparent),
                  radial-gradient(800px 500px at 10% -20%, rgba(255,255,255,0.06), transparent),
                  var(--bg);
    }

    .container{
      max-width: 1100px;
      margin-inline:auto;
      padding: 16px;
    }
    header{
      display:flex;
      flex-direction: column;
      gap: 12px;
      padding-block: 16px;
    }
    .brand{
      display:flex;
      align-items:center;
      gap:12px;
    }
    .brand-badge{
      width:36px; height:36px; border-radius:999px;
      display:grid; place-items:center;
      background: var(--primary);
      color:#001122; font-weight:800;
      box-shadow: 0 0 0 6px rgba(46,168,255,0.15);
    }
    .title{
      font-size: clamp(20px, 2.5vw, 28px);
      font-weight: 800;
      letter-spacing: -0.01em;
    }
    .subtitle { color: var(--muted); font-size: 14px; }

    .search-row{
      display:flex; gap:8px; flex-wrap:wrap;
      align-items:center;
      background: color-mix(in oklab, var(--surface) 92%, black 0%);
      padding: 8px;
      border-radius: var(--radius);
      border: 1px solid rgba(255,255,255,0.06);
    }
    .search-row input{
      flex:1 1 260px;
      padding: 10px 12px;
      border-radius: 10px;
      border: 1px solid rgba(255,255,255,0.08);
      background: #0f1530;
      color: var(--text);
      outline: none;
    }
    .search-row input::placeholder { color: #7b8496; }

    .tabs{
      display:flex; gap:8px; flex-wrap: wrap;
      background: color-mix(in oklab, var(--surface) 92%, black 0%);
      padding: 8px;
      border-radius: var(--radius);
      border: 1px solid rgba(255,255,255,0.06);
    }
    .tab-btn{
      appearance: none; border: 1px solid rgba(255,255,255,0.08); background: #0f1530;
      padding: 8px 12px; border-radius: 999px; cursor: pointer;
      color: var(--text); font-weight: 700;
      transition: all 0.2s ease;
    }
    .tab-btn[aria-selected="true"]{
      background: var(--primary);
      color: #001122;
      border-color: transparent;
      box-shadow: 0 4px 20px rgba(46,168,255,0.25);
    }

    .section-head{
      display:flex; align-items:center; justify-content:space-between;
      margin-top: 16px;
      margin-bottom: 8px;
    }
    .section-head h2{
      margin:0; font-size: 18px; font-weight: 800;
    }
    .sub-tabs{
      display: flex;
      gap: 8px;
      margin-top: 12px;
      margin-bottom: 8px;
    }
    .sub-tab-btn{
      appearance: none;
      border: 1px solid rgba(255,255,255,0.08);
      background: #0f1530;
      padding: 8px 16px;
      border-radius: 999px;
      cursor: pointer;
      color: var(--text);
      font-weight: 600;
      font-size: 14px;
      transition: all 0.2s ease;
    }
    .sub-tab-btn.active{
      background: var(--primary);
      color: #001122;
      border-color: transparent;
    }
    .grid{
      display:grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap:16px;
      margin-top:16px;
    }
    .card{
      background: linear-gradient(180deg, #0f1530, #0e1429);
      border-radius: var(--radius);
      padding: 16px;
      display:flex; flex-direction: column; gap: 12px;
      border: 1px solid rgba(255,255,255,0.06);
      transform: perspective(800px) translateZ(0);
      transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;
      position: relative;
      cursor: pointer;
    }
    .card:hover{
      transform: perspective(800px) rotateX(2deg) rotateY(-2deg);
      border-color: rgba(46,168,255,0.35);
      box-shadow: 0 8px 30px rgba(46,168,255,0.15);
    }

    .status-badge{
      position: absolute;
      top: 12px;
      left: 12px;
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 4px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      z-index: 1;
    }

    .status-badge.live{
      background: rgba(255, 51, 51, 0.2);
      border: 1px solid rgba(255, 51, 51, 0.5);
      color: #ff6b6b;
    }

    .status-badge.completed{
      background: rgba(51, 255, 102, 0.2);
      border: 1px solid rgba(51, 255, 102, 0.5);
      color: #33ff66;
    }

    .status-dot{
      width: 6px;
      height: 6px;
      border-radius: 50%;
      display: inline-block;
    }

    .status-dot.live{
      background: #ff6b6b;
      animation: pulse-red 1.5s ease-in-out infinite;
    }

    .status-dot.completed{
      background: #33ff66;
    }

    @keyframes pulse-red {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }

    .row { display:flex; align-items:center; gap:12px; }
    .avatar{
      width:64px; height:64px; border-radius: 999px; flex: 0 0 64px;
      object-fit: cover; border: 1px solid rgba(255,255,255,0.08);
      background: #1a2142;
    }
    .thumb{
      width:100%; height:140px; object-fit: cover; border-radius: 10px;
      border: 1px solid rgba(255,255,255,0.06); background:#10152c;
    }
    .meta h3 { margin:0; font-size:18px; font-weight:800; }
    .meta p { margin:0; color: var(--muted); font-size: 13px; }

    .dates{
      display: flex; flex-direction: column; gap: 6px;
      font-size: 12px; color: var(--muted);
      border-top: 1px dashed rgba(255,255,255,0.08);
      padding-top: 8px;
      margin-top: 8px;
    }
    .date-item{
      display: flex; justify-content: space-between; gap: 8px;
    }
    .date-label { font-weight: 600; color: var(--text); }

    .teachers-section {
      margin-top: 8px;
    }
    .teacher-box {
      background: rgba(46,168,255,0.2);
      color: var(--text);
      padding: 8px 12px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 500;
      border: 1px solid rgba(46,168,255,0.3);
    }

    .actions{ 
      display:flex; 
      gap:8px; 
      flex-wrap: wrap; 
      margin-top: 8px;
    }
    .pill{
      flex:1 1 auto; 
      min-width: 120px;
      display:flex; 
      align-items:center; 
      justify-content:center;
      padding: 10px 12px; 
      border-radius: 10px;
      background: #0f1530; 
      border: 1px solid rgba(255,255,255,0.08);
      color: var(--text); 
      font-weight: 700; 
      cursor: pointer;
      position: relative;
      transition: all 0.2s ease;
    }
    .pill:hover{ 
      border-color: rgba(46,168,255,0.45);
      background: #121832;
    }
    .pill.active{
      background: var(--primary);
      color: #001122;
      border-color: transparent;
    }

    .panel{
      border-top: 1px dashed rgba(255,255,255,0.08);
      padding-top: 12px;
      margin-top: 12px;
      display: none;
    }
    .panel.show { display:block; }
    .list{
      display:flex; 
      flex-direction: column; 
      gap:8px;
    }
    .list-item{
      background:#0f1530; 
      border:1px solid rgba(255,255,255,0.08);
      padding:10px 12px; 
      border-radius: 8px;
      display:grid; 
      grid-template-columns: 56px 1fr auto; 
      gap:10px; 
      align-items:center;
      text-decoration:none; 
      color: var(--text);
      cursor: pointer;
      transition: border-color .2s ease;
      position: relative;
    }
    .list-item:hover { border-color: rgba(46,168,255,0.35); }

    .mini{
      width:56px; 
      height:40px; 
      object-fit: cover; 
      border-radius: 6px; 
      background:#0e1328;
      border: 1px solid rgba(255,255,255,0.06);
    }
    .list .right-hint{ 
      color: var(--muted); 
      font-size: 12px; 
    }

    .load-more-wrap{
      display:flex; 
      justify-content:center; 
      margin-top: 16px;
    }
    .load-more{
      appearance:none; 
      border:1px solid rgba(255,255,255,0.12);
      background:#0f1530; 
      color:var(--text); 
      font-weight:700;
      padding:10px 20px; 
      border-radius: 10px; 
      cursor:pointer;
      transition: all 0.2s ease;
    }
    .load-more:hover{ 
      border-color: rgba(46,168,255,0.5);
      background: #121832;
    }

    footer{
      margin-top: 40px; 
      padding: 24px 0; 
      color: var(--muted); 
      font-size: 14px; 
      text-align:center;
    }

    .sr-only{
      position: absolute; 
      width: 1px; 
      height: 1px; 
      padding: 0; 
      margin: -1px;
      overflow: hidden; 
      clip: rect(0, 0, 0, 0); 
      white-space: nowrap; 
      border: 0;
    }

    .loading-indicator {
      text-align: center;
      padding: 20px;
      color: var(--muted);
    }
  </style>
</head>
<body>
  <canvas id="bg-canvas" aria-hidden="true"></canvas>

  <div class="container">
    <header>
      <div class="brand">
        <div class="brand-badge" aria-hidden="true">ED</div>
        <div>
          <div class="title">Educators · Batches · Courses</div>
          <p class="subtitle">Explore educators, batches, and courses with intelligent search and filtering.</p>
        </div>
      </div>

      <div class="search-row" role="search">
        <label class="sr-only" for="search">Search</label>
        <input id="search" placeholder="Search keyword (e.g., 'Rahul', 'Physics', 'Batch A')" />
      </div>

      <nav class="tabs" role="tablist" aria-label="Sections">
        <button class="tab-btn" role="tab" aria-selected="true" id="tab-educators">Educators</button>
        <button class="tab-btn" role="tab" aria-selected="false" id="tab-batches">Batches</button>
        <button class="tab-btn" role="tab" aria-selected="false" id="tab-courses">Courses</button>
      </nav>
    </header>

    <main id="main">
      <section id="panel-educators" role="tabpanel">
        <div class="section-head">
          <h2>Educators</h2>
        </div>
        <div id="edu-grid" class="grid"></div>
        <div id="edu-load" class="load-more-wrap"></div>
      </section>

      <section id="panel-batches" role="tabpanel" hidden>
        <div class="section-head">
          <h2>Batches</h2>
        </div>
        <div class="sub-tabs">
          <button class="sub-tab-btn active" data-filter="live">Live Running</button>
          <button class="sub-tab-btn" data-filter="completed">Completed</button>
        </div>
        <div id="batch-grid" class="grid"></div>
        <div id="batch-load" class="load-more-wrap"></div>
      </section>

      <section id="panel-courses" role="tabpanel" hidden>
        <div class="section-head">
          <h2>Courses</h2>
        </div>
        <div class="sub-tabs">
          <button class="sub-tab-btn active" data-filter="live">Live Running</button>
          <button class="sub-tab-btn" data-filter="completed">Completed</button>
        </div>
        <div id="course-grid" class="grid"></div>
        <div id="course-load" class="load-more-wrap"></div>
      </section>

      <section id="panel-search" hidden>
        <div class="section-head">
          <h2>Search Results</h2>
        </div>
        <div id="search-edu" class="grid"></div>
        <div id="search-edu-load" class="load-more-wrap"></div>
      </section>
    </main>

    <footer>
      API-powered realtime search and pagination
    </footer>
  </div>

  <script>
    const API_BASE = window.location.origin;
    const IMG_USER = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='64' height='64'%3E%3Crect fill='%231a2142' width='64' height='64'/%3E%3Ctext x='50%25' y='50%25' font-size='24' text-anchor='middle' dy='.3em' fill='%239aa3b2'%3E👤%3C/text%3E%3C/svg%3E";
    const IMG_PH = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='200'%3E%3Crect fill='%2310152c' width='400' height='200'/%3E%3Ctext x='50%25' y='50%25' font-size='20' text-anchor='middle' dy='.3em' fill='%239aa3b2'%3E📚%3C/text%3E%3C/svg%3E";
    const PAGE_SIZE = 5;

    const state = {
      currentTab: 'educators',
      educatorsPage: 1,
      searchQuery: '',
      searchPage: 1,
      batchFilter: 'live',
      courseFilter: 'live',
      educators: [],
      searchResults: [],
      educatorPanels: {}
    };

    function formatDate(dateStr) {
      if (!dateStr) return 'N/A';
      try {
        const date = new Date(dateStr);
        const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        const day = date.getDate();
        const month = monthNames[date.getMonth()];
        const year = date.getFullYear();
        const hours = String(date.getHours()).padStart(2, '0');
        const mins = String(date.getMinutes()).padStart(2, '0');
        return `${day}-${month}-${year} [${hours}:${mins}]`;
      } catch (e) {
        return dateStr;
      }
    }

    function getStatus(startDate, endDate) {
      if (!startDate || !endDate) return null;
      const start = new Date(startDate);
      const end = new Date(endDate);
      const today = new Date();
      if (today >= start && today <= end) return 'live';
      if (today > end) return 'completed';
      return null;
    }

    function createStatusBadge(status) {
      const badge = document.createElement("div");
      badge.className = `status-badge ${status}`;
      const dot = document.createElement("span");
      dot.className = `status-dot ${status}`;
      const text = status === 'live' ? 'Live Running' : 'Completed';
      badge.appendChild(dot);
      badge.appendChild(document.createTextNode(text));
      return badge;
    }

    async function fetchEducators(page = 1) {
      try {
        const response = await fetch(`${API_BASE}/data?page=${page}&limit=${PAGE_SIZE}`);
        const data = await response.json();
        return data;
      } catch (e) {
        console.error('Error fetching educators:', e);
        return { status: 'error', data: [] };
      }
    }

    async function fetchEducatorById(id) {
      try {
        const response = await fetch(`${API_BASE}/data_id=${id}`);
        const data = await response.json();
        return data.data || {};
      } catch (e) {
        console.error('Error fetching educator:', e);
        return {};
      }
    }

    async function searchEducators(keyword, page = 1) {
      try {
        const response = await fetch(`${API_BASE}/search=${keyword}?page=${page}&limit=${PAGE_SIZE}`);
        const data = await response.json();
        return data;
      } catch (e) {
        console.error('Error searching:', e);
        return { status: 'error', data: [] };
      }
    }

    function createEducatorCard(educator) {
      const card = document.createElement("article");
      card.className = "card";

      const row = document.createElement("div");
      row.className = "row";
      const img = document.createElement("img");
      img.className = "avatar";
      img.src = educator.avatar || IMG_USER;
      img.alt = educator.first_name || 'Educator';
      row.appendChild(img);

      const meta = document.createElement("div");
      meta.className = "meta";
      const h3 = document.createElement("h3");
      h3.textContent = `${educator.first_name} ${educator.last_name}`.trim();
      const p = document.createElement("p");
      p.textContent = `@${educator.username}`;
      meta.appendChild(h3);
      meta.appendChild(p);
      row.appendChild(meta);

      const actions = document.createElement("div");
      actions.className = "actions";
      const bBtn = document.createElement("button");
      bBtn.className = "pill";
      bBtn.textContent = "Batches";
      const cBtn = document.createElement("button");
      cBtn.className = "pill";
      cBtn.textContent = "Courses";
      actions.appendChild(bBtn);
      actions.appendChild(cBtn);

      const panel = document.createElement("div");
      panel.className = "panel";
      const list = document.createElement("div");
      list.className = "list";
      panel.appendChild(list);
      const loadWrap = document.createElement("div");
      loadWrap.className = "load-more-wrap";
      panel.appendChild(loadWrap);

      if (!state.educatorPanels[educator._id]) {
        state.educatorPanels[educator._id] = { batches: [], courses: [], mode: null, page: 1 };
      }

      async function renderPanelItems(kind) {
        const pstate = state.educatorPanels[educator._id];
        if (pstate.mode !== kind) {
          pstate.mode = kind;
          pstate.page = 1;
          list.innerHTML = "";
          loadWrap.innerHTML = "";
        }

        const allItems = kind === 'batches' ? educator.batches || [] : educator.courses || [];
        const start = (pstate.page - 1) * PAGE_SIZE;
        const end = start + PAGE_SIZE;
        const items = allItems.slice(start, end);

        items.forEach(item => {
          const itemEl = document.createElement("div");
          itemEl.className = "list-item";
          const status = getStatus(item.starts_at || item.startDate, item.completed_at || item.ends_at || item.endDate);
          itemEl.innerHTML = `
            <img class="mini" src="${item.thumbnail || item.cover_photo || IMG_PH}" alt="">
            <div>${item.name}</div>
            <div class="right-hint">${kind === 'batches' ? 'Batch' : 'Course'}</div>
          `;
          list.appendChild(itemEl);
        });

        loadWrap.innerHTML = "";
        if (end < allItems.length) {
          const btn = document.createElement("button");
          btn.className = "load-more";
          btn.textContent = `Load More (${allItems.length - end} remaining)`;
          btn.addEventListener("click", () => {
            pstate.page++;
            renderPanelItems(kind);
          });
          loadWrap.appendChild(btn);
        }
      }

      function togglePanel(kind) {
        const isOpen = panel.classList.contains("show") && state.educatorPanels[educator._id].mode === kind;
        if (isOpen) {
          panel.classList.remove("show");
          bBtn.classList.remove("active");
          cBtn.classList.remove("active");
        } else {
          panel.classList.add("show");
          bBtn.classList.toggle("active", kind === "batches");
          cBtn.classList.toggle("active", kind === "courses");
          renderPanelItems(kind);
        }
      }

      bBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        togglePanel("batches");
      });
      cBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        togglePanel("courses");
      });

      card.appendChild(row);
      card.appendChild(actions);
      card.appendChild(panel);
      return card;
    }

    async function renderEducators() {
      const eduGrid = document.getElementById("edu-grid");
      const eduLoad = document.getElementById("edu-load");
      eduGrid.innerHTML = '<div class="loading-indicator">Loading educators...</div>';
      eduLoad.innerHTML = "";

      const data = await fetchEducators(state.educatorsPage);
      if (data.data && data.data.length > 0) {
        eduGrid.innerHTML = "";
        for (const edId of data.data) {
          const educator = await fetchEducatorById(edId);
          if (educator._id) {
            eduGrid.appendChild(createEducatorCard(educator));
          }
        }

        eduLoad.innerHTML = "";
        if (state.educatorsPage < Math.ceil(data.total / PAGE_SIZE)) {
          const btn = document.createElement("button");
          btn.className = "load-more";
          btn.textContent = "Load More Educators";
          btn.addEventListener("click", () => {
            state.educatorsPage++;
            renderEducators();
          });
          eduLoad.appendChild(btn);
        }
      }
    }

    async function renderSearch() {
      const searchEdu = document.getElementById("search-edu");
      const searchLoad = document.getElementById("search-edu-load");
      searchEdu.innerHTML = '<div class="loading-indicator">Searching...</div>';
      searchLoad.innerHTML = "";

      const data = await searchEducators(state.searchQuery, state.searchPage);
      if (data.data && data.data.length > 0) {
        searchEdu.innerHTML = "";
        data.data.forEach(educator => {
          searchEdu.appendChild(createEducatorCard(educator));
        });

        searchLoad.innerHTML = "";
        if (state.searchPage < Math.ceil(data.total / PAGE_SIZE)) {
          const btn = document.createElement("button");
          btn.className = "load-more";
          btn.textContent = "Load More Results";
          btn.addEventListener("click", () => {
            state.searchPage++;
            renderSearch();
          });
          searchLoad.appendChild(btn);
        }
      } else {
        searchEdu.innerHTML = '<div class="loading-indicator">No results found</div>';
      }
    }

    document.getElementById("search").addEventListener("input", (e) => {
      state.searchQuery = e.target.value.trim();
      state.searchPage = 1;
      const panelSearch = document.getElementById("panel-search");
      const panelEdu = document.getElementById("panel-educators");
      const panelBat = document.getElementById("panel-batches");
      const panelCou = document.getElementById("panel-courses");

      if (state.searchQuery) {
        panelSearch.hidden = false;
        panelEdu.hidden = true;
        panelBat.hidden = true;
        panelCou.hidden = true;
        renderSearch();
      } else {
        panelSearch.hidden = true;
        panelEdu.hidden = state.currentTab !== 'educators';
        panelBat.hidden = state.currentTab !== 'batches';
        panelCou.hidden = state.currentTab !== 'courses';
      }
    });

    document.getElementById("tab-educators").addEventListener("click", () => {
      state.currentTab = 'educators';
      document.getElementById("panel-educators").hidden = false;
      document.getElementById("panel-batches").hidden = true;
      document.getElementById("panel-courses").hidden = true;
      document.getElementById("panel-search").hidden = true;
      renderEducators();
    });

    (function bg() {
      const c = document.getElementById("bg-canvas");
      const ctx = c.getContext("2d");
      let w = 0, h = 0, t = 0;
      function resize() {
        w = c.width = window.innerWidth;
        h = c.height = window.innerHeight;
      }
      function draw() {
        ctx.clearRect(0, 0, w, h);
        ctx.globalAlpha = 1;
        const grd = ctx.createLinearGradient(0, 0, w, h);
        grd.addColorStop(0, "rgba(46,168,255,0.04)");
        grd.addColorStop(1, "rgba(255,255,255,0.02)");
        ctx.fillStyle = grd;
        ctx.fillRect(0, 0, w, h);
        ctx.lineWidth = 1;
        ctx.strokeStyle = "rgba(255,255,255,0.06)";
        const spacing = 42;
        const offset = (t * 12) % spacing;
        for (let x = -w; x < w * 2; x += spacing) {
          ctx.beginPath();
          ctx.moveTo(x + offset, 0);
          ctx.lineTo(x - h + offset, h);
          ctx.stroke();
        }
        for (let y = -h; y < h * 2; y += spacing) {
          ctx.beginPath();
          ctx.moveTo(0, y + offset);
          ctx.lineTo(w, y - w + offset);
          ctx.stroke();
        }
        t += 0.002;
        requestAnimationFrame(draw);
      }
      resize();
      window.addEventListener("resize", resize);
      draw();
    })();

    renderEducators();
  </script>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    """Serve the HTML page"""
    return HTML_TEMPLATE

@app.route('/data', methods=['GET'])
def get_educators_ids():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 5))
        skip = (page - 1) * limit
        
        cursor = educators_col.find({}, {'_id': 1}).skip(skip).limit(limit)
        ids = [str(doc['_id']) for doc in cursor]
        
        total = educators_col.count_documents({})
        
        return jsonify({
            'status': 'success',
            'count': len(ids),
            'total': total,
            'page': page,
            'limit': limit,
            'data': ids
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error fetching IDs: {str(e)}'
        }), 500

@app.route('/data_id=<object_id>', methods=['GET'])
def get_educator_by_id(object_id):
    try:
        try:
            oid = ObjectId(object_id)
        except InvalidId:
            return jsonify({
                'status': 'error',
                'message': 'Invalid ObjectId format'
            }), 400
        
        educator = educators_col.find_one({'_id': oid})
        if not educator:
            return jsonify({
                'status': 'error',
                'message': f'Educator with ID {object_id} not found'
            }), 404
        
        educator['_id'] = str(educator['_id'])
        
        return jsonify({
            'status': 'success',
            'data': educator
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error fetching educator data: {str(e)}'
        }), 500

@app.route('/search=<keyword>', methods=['GET'])
def search_educators(keyword):
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 5))
        skip = (page - 1) * limit
        
        regex_pattern = {'$regex': keyword, '$options': 'i'}
        
        pipeline = [
            {
                '$match': {
                    '$or': [
                        {'first_name': regex_pattern},
                        {'last_name': regex_pattern},
                        {'username': regex_pattern},
                        {'courses.name': regex_pattern},
                        {'batches.name': regex_pattern}
                    ]
                }
            },
            {'$skip': skip},
            {'$limit': limit}
        ]
        
        cursor = educators_col.aggregate(pipeline)
        educators = list(cursor)
        
        for educator in educators:
            educator['_id'] = str(educator['_id'])
        
        count_pipeline = pipeline[:-2]
        count_pipeline.append({'$count': 'total'})
        total_result = list(educators_col.aggregate(count_pipeline))
        total = total_result[0]['total'] if total_result else 0
        
        return jsonify({
            'status': 'success',
            'count': len(educators),
            'total': total,
            'page': page,
            'limit': limit,
            'data': educators
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error searching educators: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Route not found'
    }), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
