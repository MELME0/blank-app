import json
from pathlib import Path
from datetime import datetime
import streamlit as st

# =========================================================
# Configuration
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
# M.I.S.O. Bot (Floating + Mini-Widget)
# =========================================================

def render_miso_bot():
    st.markdown(
        """
<style>
#miso-container {
  position: fixed;
  top: 30px;
  left: 30px;
  z-index: 999999;
  user-select: none;
}

#miso-bot {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: white;
  border: 5px solid #ddd;
  box-shadow: 0 6px 20px rgba(0,0,0,0.15);
  cursor: grab;
  position: relative;
  transition: all 0.2s ease;
}

.eye {
  width: 25px;
  height: 25px;
  background: black;
  border-radius: 50%;
  position: absolute;
  top: 17px;
}

.eye.left { left: 6px; }
.eye.right { left: 29px; }

.mini #miso-bot {
  width: 40px;
  height: 40px;
  border-width: 3px;
}

#miso-toggle-widget {
  position: absolute;
  top: -10px;
  right: -10px;
  font-size: 14px;
  padding: 2px 5px;
  cursor: pointer;
}
</style>

<div id="miso-container">
  <div id="miso-bot">
    <div class="eye left"></div>
    <div class="eye right"></div>
  </div>
  <button id="miso-toggle-widget">🗔</button>
</div>

<script>
const container = document.getElementById('miso-container');
const bot = document.getElementById('miso-bot');
const toggle = document.getElementById('miso-toggle-widget');

let dragging = false;
let offsetX = 0;
let offsetY = 0;

// Restore saved position
const saved = localStorage.getItem('miso-pos');
if(saved) {
  const pos = JSON.parse(saved);
  container.style.left = pos.x + 'px';
  container.style.top = pos.y + 'px';
} else {
  container.style.left = '30px';
  container.style.top = '30px';
}

// Drag logic
bot.addEventListener('mousedown', e => {
  dragging = true;
  const rect = container.getBoundingClientRect();
  offsetX = e.clientX - rect.left;
  offsetY = e.clientY - rect.top;
  bot.style.cursor = 'grabbing';
  e.preventDefault();
});

document.addEventListener('mousemove', e => {
  if (!dragging) return;
  container.style.left = (e.clientX - offsetX) + 'px';
  container.style.top = (e.clientY - offsetY) + 'px';
});

document.addEventListener('mouseup', () => {
  if (!dragging) return;
  dragging = false;
  bot.style.cursor = 'grab';
  // Save position
  localStorage.setItem('miso-pos', JSON.stringify({
    x: container.offsetLeft,
    y: container.offsetTop
  }));
});

// Toggle mini-widget mode
toggle.addEventListener('click', () => {
  container.classList.toggle('mini');
});
</script>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# Streamlit Setup
# =========================================================

st.set_page_config(page_title="M.I.S.O.", layout="centered")
st.title(APP_TITLE)
st.caption(APP_SUBTITLE)

# =========================================================
# Authentication
# =========================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_name = None

if not st.session_state.authenticated:
    st.markdown("---")
    st.subheader("Access Required")
    with st.form("login"):
        name = st.text_input("Enter your name")
        submit = st.form_submit_button("Submit")
    if submit:
        if name.strip().lower() == "aj":
            st.session_state.authenticated = True
            st.session_state.user_name = name.strip()
            st.success("Welcome back, Creator!")
            st.rerun()
        else:
            st.error("Access denied.")
    st.stop()

# =========================================================
# Main App
# =========================================================

render_miso_bot()
st.markdown(f"### Welcome, **{st.session_state.user_name}** 👋")

data = load_data()

# =========================================================
# Section selection
# =========================================================

st.markdown("---")
section_input = st.text_input("Open or create a section")
if not section_input:
    st.info("Enter a section name to continue.")
    st.stop()

section = normalize_section(section_input)
items = data.setdefault(section, [])

# =========================================================
# Add Item
# =========================================================

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
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    items.append(entry)
    save_data(data)
    st.success("Item added.")
    st.rerun()

# =========================================================
# Display Items
# =========================================================

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

# =========================================================
# Sidebar
# =========================================================

st.sidebar.markdown("---")
st.sidebar.write("Data file:", DATA_FILE)
st.sidebar.caption("⚠️ Data may reset on Streamlit Community Cloud")
