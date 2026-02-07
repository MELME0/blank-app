import json
from pathlib import Path
from datetime import datetime
import streamlit as st

# --------------------
# Configuration
# --------------------
DATA_FILE = Path(".help_data.json")
APP_TITLE = "🎈 M.I.S.O."
APP_SUBTITLE = "Module Information System Organizer"

# --------------------
# Utilities
# --------------------
def load_data() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            pass
    return {}

def save_data(data: dict):
    DATA_FILE.write_text(json.dumps(data, indent=2))

def normalize_section(name: str) -> str:
    return name.strip().title()

# --------------------
# Authentication
# --------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_name = None

if not st.session_state.authenticated:
    st.markdown("---")
    st.subheader("Access Required")

    with st.form("login"):
        name = st.text_input("Enter your name")
        submitted = st.form_submit_button("Submit")

    if submitted:
        if name.strip().lower() == "aj":
            st.session_state.authenticated = True
            st.session_state.user_name = name.strip()
            st.success("Welcome back, Creator!")
            st.rerun()
        else:
            st.error("Access denied.")

    st.stop()

# --------------------
# M.I.S.O. Bot Overlay (Full Page)
# --------------------
st.markdown("""
<style>
#miso-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    pointer-events: auto;
    z-index: 99999;
}
#miso-bot {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: white;
    border: 5px solid #ddd;
    position: absolute;
    top: 100px;
    left: 100px;
    cursor: grab;
    box-shadow: 0 6px 20px rgba(0,0,0,0.2);
    pointer-events: auto;
}
.eye {
    width: 25px;
    height: 25px;
    border-radius: 50%;
    background: black;
    position: absolute;
    top: 17px;
}
.eye.left { left: 6px; }
.eye.right { left: 29px; }
</style>

<div id="miso-overlay">
    <div id="miso-bot">
        <div class="eye left"></div>
        <div class="eye right"></div>
    </div>
</div>

<script>
const bot = document.getElementById('miso-bot');

// Dragging
let dragging=false, offsetX=0, offsetY=0;
bot.addEventListener('mousedown', e=>{
    dragging=true;
    offsetX = e.clientX - bot.offsetLeft;
    offsetY = e.clientY - bot.offsetTop;
    bot.style.cursor='grabbing';
});
document.addEventListener('mousemove', e=>{
    if(!dragging) return;
    bot.style.left=(e.clientX - offsetX)+'px';
    bot.style.top=(e.clientY - offsetY)+'px';
    // motion trail
    bot.style.boxShadow = '0 6px 20px rgba(0,0,0,0.15), 0 0 15px rgba(0,0,0,0.05)';
});
document.addEventListener('mouseup', ()=>{
    dragging=false;
    bot.style.cursor='grab';
    bot.style.boxShadow='0 6px 20px rgba(0,0,0,0.2)';
});

// Hover-away
document.addEventListener('mousemove', e=>{
    const rect = bot.getBoundingClientRect();
    const dx = rect.left + rect.width/2 - e.clientX;
    const dy = rect.top + rect.height/2 - e.clientY;
    const dist = Math.sqrt(dx*dx + dy*dy);
    if(!dragging && dist<100){
        const strength=(1 - dist/100)*40;
        bot.style.transform = `translate(${dx/dist*strength}px, ${dy/dist*strength}px)`;
    } else if(!dragging){
        bot.style.transform='';
    }
});

// Mini-toggle
let miniMode=false;
bot.addEventListener('dblclick', ()=>{
    miniMode = !miniMode;
    if(miniMode){
        bot.style.width='40px';
        bot.style.height='40px';
        document.querySelector('.eye.left').style.width='12px';
        document.querySelector('.eye.left').style.height='12px';
        document.querySelector('.eye.right').style.width='12px';
        document.querySelector('.eye.right').style.height='12px';
    } else {
        bot.style.width='60px';
        bot.style.height='60px';
        document.querySelector('.eye.left').style.width='25px';
        document.querySelector('.eye.left').style.height='25px';
        document.querySelector('.eye.right').style.width='25px';
        document.querySelector('.eye.right').style.height='25px';
    }
});

// Expressions
let expressions=['scale(1)','scale(1.2)','scale(0.8)'], exprIndex=0;
bot.addEventListener('click', ()=>{
    exprIndex=(exprIndex+1)%expressions.length;
    bot.style.transform=expressions[exprIndex];
});
</script>
""", unsafe_allow_html=True)

# --------------------
# Main App Interface
# --------------------
st.write(f"Welcome, **{st.session_state.user_name}** 👋")
data = load_data()

st.markdown("---")
section_input = st.text_input("Open or create a section")

if not section_input:
    st.info("Enter a section name to continue.")
    st.stop()

section = normalize_section(section_input)
items = data.setdefault(section, [])

# Add Item
st.markdown("---")
st.subheader(f"Add to {section}")
with st.form("add_item"):
    title = st.text_input("Title")
    notes = st.text_area("Notes (optional)")
    add = st.form_submit_button("Add")

if add and title.strip():
    entry = {
        "id": datetime.utcnow().isoformat(),
        "title": title.strip(),
        "notes": notes.strip(),
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    items.append(entry)
    save_data(data)
    st.success("Item added.")
    st.rerun()

# Display Items
st.markdown("---")
st.subheader(section)
if not items:
    st.info("No items yet.")
else:
    for item in items:
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
