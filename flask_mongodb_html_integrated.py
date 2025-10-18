from flask import Flask, jsonify, request, render_template_string
import pymongo
from pymongo.errors import ConnectionFailure
from bson.errors import InvalidId
from bson import ObjectId
from flask_cors import CORS
import os

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
    print("Failed to connect to MongoDB.")
    exit(1)

db = client["unacademy_db"]
educators_col = db["educators"]

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
    }
    a { color: var(--primary); text-decoration: none; }
    #bg-canvas{
      position: fixed;
      inset: 0;
      z-index: -1;
      background: radial-gradient(1000px 600px at 80% -10%, rgba(46,168,255,0.12), transparent),
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
    }
    .title{
      font-size: clamp(20px, 2.5vw, 28px);
      font-weight: 800;
    }
    .subtitle { color: var(--muted); font-size: 14px; }
    .search-row{
      display:flex;
      gap:8px;
      align-items:center;
      background: #121832;
      padding: 8px;
      border-radius: var(--radius);
      border: 1px solid rgba(255,255,255,0.06);
    }
    .search-row input{
      flex:1;
      padding: 10px 12px;
      border-radius: 10px;
      border: 1px solid rgba(255,255,255,0.08);
      background: #0f1530;
      color: var(--text);
      outline: none;
    }
    .tabs{
      display:flex;
      gap:8px;
      background: #121832;
      padding: 8px;
      border-radius: var(--radius);
      border: 1px solid rgba(255,255,255,0.06);
    }
    .tab-btn{
      appearance: none;
      border: 1px solid rgba(255,255,255,0.08);
      background: #0f1530;
      padding: 8px 12px;
      border-radius: 999px;
      cursor: pointer;
      color: var(--text);
      font-weight: 700;
      transition: all 0.2s ease;
    }
    .tab-btn[aria-selected="true"]{
      background: var(--primary);
      color: #001122;
      border-color: transparent;
    }
    .section-head{
      margin-top: 16px;
      margin-bottom: 8px;
    }
    .section-head h2{
      margin:0;
      font-size: 18px;
      font-weight: 800;
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
      display:flex;
      flex-direction: column;
      gap: 12px;
      border: 1px solid rgba(255,255,255,0.06);
      transition: all 0.2s ease;
    }
    .card:hover{
      border-color: rgba(46,168,255,0.35);
      box-shadow: 0 8px 30px rgba(46,168,255,0.15);
    }
    .row { display:flex; align-items:center; gap:12px; }
    .avatar{
      width:64px;
      height:64px;
      border-radius: 999px;
      flex: 0 0 64px;
      object-fit: cover;
      border: 1px solid rgba(255,255,255,0.08);
      background: #1a2142;
    }
    .meta h3 { margin:0; font-size:18px; font-weight:800; }
    .meta p { margin:0; color: var(--muted); font-size: 13px; }
    .actions { display:flex; gap:8px; flex-wrap: wrap; margin-top: 8px; }
    .pill{
      flex:1;
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
      transition: all 0.2s ease;
    }
    .pill:hover { border-color: rgba(46,168,255,0.45); }
    .pill.active{
      background: var(--primary);
      color: #001122;
    }
    .panel{
      border-top: 1px dashed rgba(255,255,255,0.08);
      padding-top: 12px;
      margin-top: 12px;
      display: none;
    }
    .panel.show { display:block; }
    .list{ display:flex; flex-direction: column; gap:8px; }
    .list-item{
      background:#0f1530;
      border:1px solid rgba(255,255,255,0.08);
      padding:10px 12px;
      border-radius: 8px;
      display:grid;
      grid-template-columns: 56px 1fr auto;
      gap:10px;
      align-items:center;
      color: var(--text);
      cursor: pointer;
      transition: border-color 0.2s;
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
    .right-hint { color: var(--muted); font-size: 12px; }
    .load-more-wrap{ display:flex; justify-content:center; margin-top: 16px; }
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
    .load-more:hover { border-color: rgba(46,168,255,0.5); }
    footer{ margin-top: 40px; padding: 24px 0; color: var(--muted); font-size: 14px; text-align:center; }
  </style>
</head>
<body>
  <canvas id="bg-canvas" aria-hidden="true"></canvas>
  <div class="container">
    <header>
      <div class="brand">
        <div class="brand-badge">ED</div>
        <div>
          <div class="title">Educators · Batches · Courses</div>
          <p class="subtitle">Explore educators, batches, and courses</p>
        </div>
      </div>
      <div class="search-row">
        <input id="search" placeholder="Search by name, username, course or batch..." />
      </div>
      <nav class="tabs">
        <button class="tab-btn" id="tab-educators" aria-selected="true">Educators</button>
        <button class="tab-btn" id="tab-search" aria-selected="false" style="display:none;">Search Results</button>
      </nav>
    </header>
    <main id="main">
      <section id="panel-educators">
        <div class="section-head"><h2>Educators</h2></div>
        <div id="edu-grid" class="grid"></div>
        <div id="edu-load" class="load-more-wrap"></div>
      </section>
      <section id="panel-search" hidden>
        <div class="section-head"><h2>Search Results</h2></div>
        <div id="search-grid" class="grid"></div>
        <div id="search-load" class="load-more-wrap"></div>
      </section>
    </main>
    <footer>Click on any educator to explore batches and courses</footer>
  </div>
  <script>
    const IMG_USER = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='64' height='64'%3E%3Crect fill='%231a2142' width='64' height='64'/%3E%3Ctext x='50%25' y='50%25' font-size='24' text-anchor='middle' dy='.3em' fill='%239aa3b2'%3E👤%3C/text%3E%3C/svg%3E";
    const IMG_PH = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='200'%3E%3Crect fill='%2310152c' width='400' height='200'/%3E%3Ctext x='50%25' y='50%25' font-size='20' text-anchor='middle' dy='.3em' fill='%239aa3b2'%3E📚%3C/text%3E%3C/svg%3E";
    const state = { educatorsPage: 1, searchPage: 1, searchQuery: '', isSearching: false };
    const lazyObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting && entry.target.dataset.src) {
          entry.target.src = entry.target.dataset.src;
          lazyObserver.unobserve(entry.target);
        }
      });
    }, { rootMargin: "200px" });

    async function fetchEducators(page = 1) {
      try {
        const response = await fetch(`/api/educators?page=${page}&limit=5`);
        const data = await response.json();
        return data;
      } catch (e) {
        console.error('Error:', e);
        return { data: [], total: 0, count: 0 };
      }
    }

    async function searchEducators(query, page = 1) {
      if (!query.trim()) return { data: [], total: 0, count: 0 };
      try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&page=${page}&limit=5`);
        const data = await response.json();
        return data;
      } catch (e) {
        console.error('Error:', e);
        return { data: [], total: 0, count: 0 };
      }
    }

    function createEducatorCard(edu) {
      const card = document.createElement("article");
      card.className = "card";
      const row = document.createElement("div");
      row.className = "row";
      const img = document.createElement("img");
      img.className = "avatar";
      img.alt = edu.first_name;
      img.dataset.src = edu.avatar || IMG_USER;
      img.loading = "lazy";
      lazyObserver.observe(img);
      const meta = document.createElement("div");
      meta.className = "meta";
      const h3 = document.createElement("h3");
      h3.textContent = `${edu.first_name} ${edu.last_name}`;
      const p = document.createElement("p");
      p.textContent = `@${edu.username}`;
      meta.append(h3, p);
      row.append(img, meta);
      const actions = document.createElement("div");
      actions.className = "actions";
      const batchBtn = document.createElement("button");
      batchBtn.className = "pill";
      batchBtn.textContent = `Batches (${edu.batches?.length || 0})`;
      const courseBtn = document.createElement("button");
      courseBtn.className = "pill";
      courseBtn.textContent = `Courses (${edu.courses?.length || 0})`;
      actions.append(batchBtn, courseBtn);
      const panel = document.createElement("div");
      panel.className = "panel";
      const list = document.createElement("div");
      list.className = "list";
      const loadWrap = document.createElement("div");
      loadWrap.className = "load-more-wrap";
      panel.append(list, loadWrap);
      let itemsOffset = { batches: 0, courses: 0 };

      function renderItems(kind) {
        const items = edu[kind] || [];
        const offset = itemsOffset[kind];
        const end = Math.min(offset + 5, items.length);
        for (let i = offset; i < end; i++) {
          const item = items[i];
          const el = document.createElement("div");
          el.className = "list-item";
          const mini = document.createElement("img");
          mini.className = "mini";
          mini.alt = "";
          mini.dataset.src = item.image || item.thumbnail || IMG_PH;
          mini.loading = "lazy";
          lazyObserver.observe(mini);
          const label = document.createElement("div");
          label.textContent = item.name;
          const hint = document.createElement("div");
          hint.className = "right-hint";
          hint.textContent = kind === "batches" ? "Batch" : "Course";
          el.append(mini, label, hint);
          list.append(el);
        }
        itemsOffset[kind] = end;
        loadWrap.innerHTML = "";
        if (end < items.length) {
          const btn = document.createElement("button");
          btn.className = "load-more";
          btn.textContent = `Load more (${items.length - end} remaining)`;
          btn.addEventListener("click", () => renderItems(kind));
          loadWrap.append(btn);
        }
      }

      function togglePanel(kind) {
        const isOpen = panel.classList.contains("show");
        if (isOpen) {
          panel.classList.remove("show");
          batchBtn.classList.remove("active");
          courseBtn.classList.remove("active");
        } else {
          panel.classList.add("show");
          batchBtn.classList.toggle("active", kind === "batches");
          courseBtn.classList.toggle("active", kind === "courses");
          list.innerHTML = "";
          itemsOffset[kind] = 0;
          renderItems(kind);
        }
      }

      batchBtn.addEventListener("click", (e) => { e.stopPropagation(); togglePanel("batches"); });
      courseBtn.addEventListener("click", (e) => { e.stopPropagation(); togglePanel("courses"); });
      card.append(row, actions, panel);
      return card;
    }

    async function renderEducators(page = 1, append = false) {
      const eduGrid = document.getElementById("edu-grid");
      const eduLoad = document.getElementById("edu-load");
      if (!append) { eduGrid.innerHTML = ""; eduLoad.innerHTML = ""; }
      const data = await fetchEducators(page);
      data.data.forEach(edu => { eduGrid.append(createEducatorCard(edu)); });
      eduLoad.innerHTML = "";
      if (data.count === 5 && page * 5 < data.total) {
        const btn = document.createElement("button");
        btn.className = "load-more";
        btn.textContent = "Load more educators";
        btn.addEventListener("click", () => {
          state.educatorsPage++;
          renderEducators(state.educatorsPage, true);
        });
        eduLoad.append(btn);
      }
    }

    async function renderSearch(page = 1, append = false) {
      const searchGrid = document.getElementById("search-grid");
      const searchLoad = document.getElementById("search-load");
      if (!append) { searchGrid.innerHTML = ""; searchLoad.innerHTML = ""; }
      const data = await searchEducators(state.searchQuery, page);
      data.data.forEach(edu => { searchGrid.append(createEducatorCard(edu)); });
      searchLoad.innerHTML = "";
      if (data.count === 5 && page * 5 < data.total) {
        const btn = document.createElement("button");
        btn.className = "load-more";
        btn.textContent = "Load more results";
        btn.addEventListener("click", () => {
          state.searchPage++;
          renderSearch(state.searchPage, true);
        });
        searchLoad.append(btn);
      }
    }

    const tabEdu = document.getElementById("tab-educators");
    const tabSearch = document.getElementById("tab-search");
    const panelEdu = document.getElementById("panel-educators");
    const panelSearch = document.getElementById("panel-search");
    const searchInput = document.getElementById("search");

    tabEdu.addEventListener("click", () => {
      panelEdu.hidden = false;
      panelSearch.hidden = true;
      tabEdu.setAttribute("aria-selected", "true");
      tabSearch.setAttribute("aria-selected", "false");
    });

    tabSearch.addEventListener("click", () => {
      panelEdu.hidden = true;
      panelSearch.hidden = false;
      tabEdu.setAttribute("aria-selected", "false");
      tabSearch.setAttribute("aria-selected", "true");
    });

    searchInput.addEventListener("input", (e) => {
      const q = e.target.value.trim();
      if (q) {
        state.isSearching = true;
        state.searchQuery = q;
        state.searchPage = 1;
        tabSearch.style.display = "inline-block";
        tabSearch.click();
        renderSearch(1, false);
      } else {
        state.isSearching = false;
        state.searchQuery = '';
        tabSearch.style.display = "none";
        tabEdu.click();
      }
    });

    (function bg() {
      const c = document.getElementById("bg-canvas");
      if (!c) return;
      const ctx = c.getContext("2d");
      let w = 0, h = 0, t = 0;
      function resize() { w = c.width = window.innerWidth; h = c.height = window.innerHeight; }
      function draw() {
        ctx.clearRect(0, 0, w, h);
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

    renderEducators(1);
  </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/educators', methods=['GET'])
def get_educators():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 5))
        skip = (page - 1) * limit
        cursor = educators_col.find({}).skip(skip).limit(limit)
        educators = []
        for doc in cursor:
            doc['_id'] = str(doc['_id'])
            educators.append(doc)
        total = educators_col.count_documents({})
        return jsonify({
            'status': 'success',
            'data': educators,
            'total': total,
            'count': len(educators),
            'page': page,
            'limit': limit
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search_api():
    try:
        query = request.args.get('q', '')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 5))
        skip = (page - 1) * limit
        regex_pattern = {'$regex': query, '$options': 'i'}
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
        educators = list(educators_col.aggregate(pipeline))
        for edu in educators:
            edu['_id'] = str(edu['_id'])
        count_pipeline = [
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
            {'$count': 'total'}
        ]
        count_result = list(educators_col.aggregate(count_pipeline))
        total = count_result[0]['total'] if count_result else 0
        return jsonify({
            'status': 'success',
            'data': educators,
            'total': total,
            'count': len(educators),
            'page': page,
            'limit': limit
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/data', methods=['GET'])
def get_educators_ids():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
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
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error fetching IDs: {str(e)}'}), 500

@app.route('/data_id=<object_id>', methods=['GET'])
def get_educator_by_id(object_id):
    try:
        try:
            oid = ObjectId(object_id)
        except InvalidId:
            return jsonify({'status': 'error', 'message': 'Invalid ObjectId format'}), 400
        educator = educators_col.find_one({'_id': oid})
        if not educator:
            return jsonify({'status': 'error', 'message': f'Educator not found'}), 404
        educator['_id'] = str(educator['_id'])
        return jsonify({'status': 'success', 'data': educator}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500

@app.route('/search=<keyword>', methods=['GET'])
def search_educators(keyword):
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        skip = (page - 1) * limit
        regex_pattern = {'$regex': keyword, '$options': 'i'}
        pipeline = [
            {
                '$match': {
                    '$or': [
                        {'first_name': regex_pattern},
                        {'last_name': regex_pattern},
                        {'username': regex_pattern}
                    ]
                }
            },
            {'$skip': skip},
            {'$limit': limit}
        ]
        educators = list(educators_col.aggregate(pipeline))
        for educator in educators:
            educator['_id'] = str(educator['_id'])
        count_pipeline = [
            {
                '$match': {
                    '$or': [
                        {'first_name': regex_pattern},
                        {'last_name': regex_pattern},
                        {'username': regex_pattern}
                    ]
                }
            },
            {'$count': 'total'}
        ]
        total_result = list(educators_col.aggregate(count_pipeline))
        total = total_result[0]['total'] if total_result else 0
        return jsonify({
            'status': 'success',
            'data': educators,
            'total': total,
            'count': len(educators),
            'page': page,
            'limit': limit
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Route not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)