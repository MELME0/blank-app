import json
from pathlib import Path
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components

# =========================================================
# Config
# =========================================================
DATA_FILE = Path(".help_data.json")
APP_TITLE = "🎈 M.I.S.O."
APP_SUBTITLE = "Module Information System Organizer"

# =========================================================
# Utilities
# =========================================================
def load_data() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            return {}
    return {}

def save_data(data: dict):
    DATA_FILE.write_text(json.dumps(data, indent=2))

def normalize_section(name: str) -> str:
    return name.strip().title()

# =========================================================
# M.I.S.O. Bot Component
# =========================================================
def render_miso_bot():
    html_code = """
<style>
/* Full-page overlay */
#miso-overlay {
    position: fixed;
    top:0; left:0;
    width:100vw; height:100vh;
    pointer-events:none;
    z-index:999999;
}

/* Bot container */
#miso-container {
    position:absolute;
    width:60px; height:60px;
    pointer-events:auto;
    cursor:grab;
    user-select:none;
}

/* Mini mode */
.mini { width:40px !important; height:40px !important; }

/* Bot body */
#miso-bot {
    width:100%; height:100%;
    border-radius:50%;
    background:white;
    border:5px solid #ddd;
    box-shadow:0 6px 20px rgba(0,0,0,0.15);
    position:relative;
    overflow:hidden;
}

/* Eyes */
.eye {
    position:absolute;
    top:17px;
    border-radius:50%;
    background:black;
    transition: transform 0.1s ease, width 0.1s ease, height 0.1s ease;
}
.eye.left { left:6px; }
.eye.right { left:29px; }

/* Expressions using eclipse */
.expr-normal .eye { transform:scale(1); }
.expr-surprised .eye { transform:scale(1.3); }
.expr-sleepy .eye { height:8px; top:25px; border-radius:12px/6px; }
.expr-angry .eye { transform:rotate(-8deg) scale(1); border-radius:50% 40% 40% 50%; }

/* Shadow trail */
.shadow {
    position:absolute;
    border-radius:50%;
    background:rgba(200,200,200,0.15);
    pointer-events:none;
    filter:blur(4px);
    animation:fadeShadow 0.5s forwards;
}
@keyframes fadeShadow {
    to { opacity:0; transform:translate(0,0) scale(0.8); }
}

/* Mini toggle button */
#toggle-widget {
    position:absolute; top:-10px; right:-10px;
    font-size:14px; padding:2px 5px; cursor:pointer;
}
</style>

<div id="miso-overlay">
    <div id="miso-container">
        <div id="miso-bot" class="expr-normal">
            <div class="eye left"></div>
            <div class="eye right"></div>
        </div>
        <button id="toggle-widget">🗔</button>
    </div>
</div>

<script>
const container = document.getElementById('miso-container');
const bot = document.getElementById('miso-bot');
const toggle = document.getElementById('toggle-widget');

let dragging = false;
let offsetX=0, offsetY=0;
let expressions=['expr-normal','expr-surprised','expr-sleepy','expr-angry'];
let exprIndex=0;

// Position
let botX = 50, botY = 50;
let targetX = botX, targetY = botY;

// Restore saved state
const saved = localStorage.getItem('miso-state');
if(saved){
    const state = JSON.parse(saved);
    botX = state.x||50; botY=state.y||50;
    container.style.left=botX+'px';
    container.style.top=botY+'px';
    if(state.mini) container.classList.add('mini');
    exprIndex=state.exprIndex||0;
    bot.className=expressions[exprIndex];
}

// Drag
bot.addEventListener('mousedown', e=>{
    dragging=true;
    const rect=container.getBoundingClientRect();
    offsetX=e.clientX-rect.left;
    offsetY=e.clientY-rect.top;
    bot.style.cursor='grabbing';
    e.preventDefault();
});

document.addEventListener('mousemove', e=>{
    if(dragging){
        // Shadow trail
        const shadow = document.createElement('div');
        shadow.className='shadow';
        shadow.style.left=container.offsetLeft+'px';
        shadow.style.top=container.offsetTop+'px';
        shadow.style.width=container.offsetWidth+'px';
        shadow.style.height=container.offsetHeight+'px';
        document.body.appendChild(shadow);
        setTimeout(()=>shadow.remove(),500);

        botX = e.clientX-offsetX;
        botY = e.clientY-offsetY;
    } else {
        // Hover-away
        const rect=container.getBoundingClientRect();
        const cx=rect.left+rect.width/2;
        const cy=rect.top+rect.height/2;
        const dx=cx-e.clientX;
        const dy=cy-e.clientY;
        const dist=Math.sqrt(dx*dx+dy*dy);
        const threshold=80;
        if(dist<threshold){
            const strength=(1-dist/threshold)*30;
            targetX = botX + dx/dist*strength;
            targetY = botY + dy/dist*strength;
        } else {
            targetX = botX;
            targetY = botY;
        }
    }
});

// Drag end
document.addEventListener('mouseup', ()=>{
    if(dragging){
        dragging=false;
        bot.style.cursor='grab';
        saveState();
    }
});

// Mini toggle
toggle.addEventListener('click', ()=>{
    container.classList.toggle('mini');
    scaleEyes();
    saveState();
});

// Expression change
bot.addEventListener('dblclick', ()=>{
    exprIndex=(exprIndex+1)%expressions.length;
    bot.className=expressions[exprIndex];
    saveState();
});

// Eye scale on mini mode
function scaleEyes(){
    const eyes = bot.querySelectorAll('.eye');
    if(container.classList.contains('mini')){
        eyes.forEach(e=>{ e.style.width='18px'; e.style.height='18px'; });
    } else {
        eyes.forEach(e=>{ e.style.width='25px'; e.style.height='25px'; });
    }
}

// Save state
function saveState(){
    localStorage.setItem('miso-state', JSON.stringify({
        x:botX, y:botY,
        mini: container.classList.contains('mini'),
        exprIndex: exprIndex
    }));
}

// Idle / animate bot
function animate(){
    // Move bot toward target
    botX += (targetX-botX)*0.1;
    botY += (targetY-botY)*0.1;
    container.style.left = botX+'px';
    container.style.top = botY+'px';
    requestAnimationFrame(animate);
}
animate();

// Random patrol when idle
setInterval(()=>{
    if(!dragging){
        targetX = Math.random()*(window.innerWidth-60);
        targetY = Math.random()*(window.innerHeight-60);
    }
},5000);
</script>
"""
    components.html(html_code, height=400, width=400)  # iframe, bot floats full page

# =========================================================
# Streamlit App
# =========================================================
st.set_page_config(page_title="M.I.S.O.", layout="centered")
st.title(APP_TITLE)
st.caption(APP_SUBTITLE)

# Authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated=False
    st.session_state.user_name=None

if not st.session_state.authenticated:
    st.markdown("---")
    st.subheader("Access Required")
    with st.form("login"):
        name = st.text_input("Enter your name")
        submit = st.form_submit_button("Submit")
    if submit:
        if name.strip().lower()=="aj":
            st.session_state.authenticated=True
            st.session_state.user_name=name.strip()
            st.success("Welcome back, Creator!")
            st.rerun()
        else:
            st.error("Access denied.")
    st.stop()

# Render M.I.S.O. Bot
render_miso_bot()

# Main content
st.markdown(f"### Welcome, **{st.session_state.user_name}** 👋")
data = load_data()

# Section input
st.markdown("---")
section_input = st.text_input("Open or create a section")
if not section_input:
    st.info("Enter a section name to continue.")
    st.stop()

section = normalize_section(section_input)
items = data.setdefault(section, [])

# Add new item
st.markdown("---")
st.subheader(f"Add to {section}")
with st.form("add_item", clear_on_submit=True):
    title = st.text_input("Title")
    notes = st.text_area("Notes (optional)")
    add = st.form_submit_button("Add")

if add and title.strip():
    entry = {
        "id": datetime.utcnow().isoformat(),
        "title": title.strip(),
        "notes": notes.strip(),
        "created_at": datetime.utcnow().isoformat()+'Z'
    }
    items.append(entry)
    save_data(data)
    st.success("Item added.")
    st.rerun()

# Display items
st.markdown("---")
st.subheader(section)
if not items:
    st.info("No items yet.")
else:
    for item in list(items):
        with st.expander(item["title"]):
            if item["notes"]:
                st.write(item["notes"])
            st.caption(f"Created: {item['created_at']}")
            if st.button("Delete", key=f"del_{item['id']}"):
                items.remove(item)
                save_data(data)
                st.rerun()

# Sidebar
st.sidebar.markdown("---")
st.sidebar.write("Data file:", DATA_FILE)
st.sidebar.caption("⚠️ Data may reset on Streamlit Community Cloud")
