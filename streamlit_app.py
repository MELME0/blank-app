import json
from pathlib import Path
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components

# --------------------
# Config
# --------------------
DATA_FILE = Path(".help_data.json")
APP_TITLE = "🎈 M.I.S.O."
APP_SUBTITLE = "Module Information System Organizer"

# --------------------
# Utils
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
# Streamlit App Setup
# --------------------
st.set_page_config(page_title=APP_TITLE)
st.title(APP_TITLE)
st.write(APP_SUBTITLE)

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
# Mini Tab Launcher
# --------------------
st.markdown("---")
st.subheader("Launch Mini M.I.S.O Tab")
if st.button("Open Mini Tab"):
    # This JS opens a separate browser window and injects the bot
    components.html("""
    <script>
    const miniWin = window.open(
        '',
        'MISO Mini',
        'width=400,height=400,top=100,left=100,scrollbars=no,resizable=yes'
    );

    miniWin.document.write(`
        <style>
        body { margin:0; overflow:hidden; background:#f0f0f0; }
        #miso-bot {
            width:60px; height:60px; border-radius:50%;
            background:white; border:5px solid #ddd;
            position:absolute; top:100px; left:100px;
            box-shadow:0 6px 20px rgba(0,0,0,0.2);
            cursor:grab; z-index:9999;
        }
        .eye { width:25px; height:25px; border-radius:50%; background:black; position:absolute; top:17px; }
        .eye.left { left:6px; } .eye.right { left:29px; }
        .trail { position:absolute; width:60px; height:60px; border-radius:50%; background:rgba(200,200,200,0.2); pointer-events:none; filter:blur(2px);}
        </style>

        <div id="miso-bot">
            <div class="eye left"></div>
            <div class="eye right"></div>
        </div>

        <script>
        const bot = document.getElementById('miso-bot');
        const leftEye = bot.querySelector('.eye.left');
        const rightEye = bot.querySelector('.eye.right');

        let dragging=false, offsetX=0, offsetY=0;
        let exprIndex=0;
        const expressions=['scale(1)','scale(1.2)','scale(0.8)','scale(1.1)'];

        bot.addEventListener('mousedown', e=>{
            dragging=true;
            offsetX=e.clientX - bot.offsetLeft;
            offsetY=e.clientY - bot.offsetTop;
            bot.style.cursor='grabbing';
        });

        document.addEventListener('mousemove', e=>{
            if(dragging){
                const x=e.clientX - offsetX;
                const y=e.clientY - offsetY;

                const trail=document.createElement('div');
                trail.className='trail';
                trail.style.left=bot.offsetLeft+'px';
                trail.style.top=bot.offsetTop+'px';
                document.body.appendChild(trail);
                setTimeout(()=>trail.remove(),400);

                bot.style.left=x+'px';
                bot.style.top=y+'px';
            } else {
                // hover-away
                const rect=bot.getBoundingClientRect();
                const dx=(rect.left+rect.width/2 - e.clientX);
                const dy=(rect.top+rect.height/2 - e.clientY);
                const dist=Math.sqrt(dx*dx+dy*dy);
                if(dist<80){
                    const strength=(1-dist/80)*30;
                    bot.style.transform='translate('+dx/dist*strength+'px,'+dy/dist*strength+'px)';
                } else {
                    bot.style.transform='';
                }
            }

            // eyes track mouse
            const bx=bot.offsetLeft+30;
            const by=bot.offsetTop+30;
            const distance=3;
            const angle=Math.atan2(e.clientY-by,e.clientX-bx);
            const dx=Math.cos(angle)*distance;
            const dy=Math.sin(angle)*distance;
            leftEye.style.transform='translate('+dx+'px,'+dy+'px)';
            rightEye.style.transform='translate('+dx+'px,'+dy+'px)';
        });

        document.addEventListener('mouseup', e=>{
            dragging=false;
            bot.style.cursor='grab';
        });

        bot.addEventListener('click', e=>{
            exprIndex=(exprIndex+1)%expressions.length;
            bot.style.transform=expressions[exprIndex];
        });
        </script>
    `);
    </script>
    """, height=0)

# --------------------
# Main M.I.S.O Section Management
# --------------------
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
