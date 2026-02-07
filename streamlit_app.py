import json
from pathlib import Path
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components

DATA_FILE = Path(".help_data.json")

# Define search categories
CATEGORIES = {
    "modules": "Modules",
    "docs": "Documentation",
    "help": "Help & Support",
    "settings": "Settings",
    "about": "About"
}


def load_data() -> dict:
    if not DATA_FILE.exists():
        return {}
    try:
        return json.loads(DATA_FILE.read_text())
    except Exception:
        return {}


def save_data(data: dict):
    DATA_FILE.write_text(json.dumps(data, indent=2))


def render_miso_bot():
    """Render the M.I.S.O. bot widget with eye-tracking and dragging functionality."""
    html_code = """
    <style>
        * { box-sizing: border-box; }
        #miso-container {
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 9999;
            font-family: Arial, sans-serif;
            will-change: transform, opacity;
        }

        /* Body (head) is a white circle 60px with 5px light-grey outline */
        #miso-bot { position: relative; width: 60px; height: 60px; cursor: grab; user-select: none; touch-action: none; }
        #miso-bot:active { cursor: grabbing; }

        .miso-body {
            position: absolute;
            width: 60px;
            height: 60px;
            border: 5px solid #dcdcdc; /* light grey outline */
            border-radius: 50%;
            background: #ffffff; /* white body */
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
            transition: all 0.12s ease;
        }

        /* Two black eyes, 25px each, centered vertically inside the 60px head */
        .miso-eye {
            --expr-transform: none;
            --gaze-x: 0px;
            --gaze-y: 0px;
            position: absolute;
            width: 25px;
            height: 25px;
            background: #000;
            border-radius: 50%;
            top: 18px; /* centered vertically: (60-25)/2 = 17.5 */
            overflow: hidden;
            transition: transform 0.12s ease, height 0.12s ease;
            transform: var(--expr-transform) translate(var(--gaze-x), var(--gaze-y));
        }

        /* Horizontal placement so eyes sit comfortably inside the 60px head */
        .miso-eye-left { left: 6px; }
        .miso-eye-right { left: 29px; }

        /* Expression helpers — change the eye SHAPE to convey emotion */
        .expr-normal .miso-eye { --expr-transform: none; }
        .expr-surprised .miso-eye { --expr-transform: scale(1.15); }
        .expr-sleepy .miso-eye { height: 10px; top: 25px; --expr-transform: none; border-radius: 12px / 6px; }
        .expr-angry .miso-eye { --expr-transform: rotate(-8deg) scale(1); border-radius: 50% 40% 40% 50%; }

        /* Blink animation for quick feedback (squash eyes) */
        #miso-bot.blinking .miso-eye { height: 6px; top: 28px; }
        
        #miso-search-modal {
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            border: 2px solid #888;
            border-radius: 8px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            z-index: 10000;
            min-width: 300px;
            backdrop-filter: blur(2px);
        }
        
        #miso-modal-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.3);
            z-index: 9999;
        }
        
        .miso-modal-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
        }
        
        .miso-modal-input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 14px;
            box-sizing: border-box;
            margin-bottom: 15px;
        }
        
        .miso-modal-buttons {
            display: flex;
            gap: 10px;
            justify-content: flex-end;
        }
        
        .miso-modal-btn {
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
        }
        
        .miso-modal-btn-primary {
            background: #4CAF50;
            color: white;
        }
        
        .miso-modal-btn-primary:hover {
            background: #45a049;
        }
        
        .miso-modal-btn-cancel {
            background: #f0f0f0;
            color: #333;
        }
        
        .miso-modal-btn-cancel:hover {
            background: #ddd;
        }
        
        .miso-category-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        
        .miso-category-item {
            padding: 10px;
            margin: 5px 0;
            background: #f9f9f9;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .miso-category-item:hover {
            background: #e8f5e9;
            border-color: #4CAF50;
        }
    </style>
    
    <div id="miso-modal-overlay"></div>
    <div id="miso-search-modal">
        <div class="miso-modal-title">🤖 M.I.S.O. - What do you need?</div>
        <input type="text" id="miso-search-input" class="miso-modal-input" 
               placeholder="Search or select category..." />
        <ul class="miso-category-list" id="miso-category-list">
        </ul>
        <div class="miso-modal-buttons">
            <button class="miso-modal-btn miso-modal-btn-cancel" id="miso-close-btn">Close</button>
        </div>
    </div>
    
    <div id="miso-container">
        <div id="miso-bot" class="miso-body">
            <div class="miso-eye miso-eye-left"></div>
            <div class="miso-eye miso-eye-right"></div>
        </div>
    </div>
    
    <script>
        const misoBot = document.getElementById('miso-bot');
        const misoContainer = document.getElementById('miso-container');
        const modalOverlay = document.getElementById('miso-modal-overlay');
        const searchModal = document.getElementById('miso-search-modal');
        const closeBtn = document.getElementById('miso-close-btn');
        const searchInput = document.getElementById('miso-search-input');
        const categoryList = document.getElementById('miso-category-list');
        const leftEye = document.querySelector('.miso-eye-left');
        const rightEye = document.querySelector('.miso-eye-right');

        // Expression state - will be applied on the container as classes
        const expressions = ['expr-normal', 'expr-surprised', 'expr-sleepy', 'expr-angry'];
        let exprIndex = 0;
        function applyExpression() {
            expressions.forEach(c => misoContainer.classList.remove(c));
            misoContainer.classList.add(expressions[exprIndex]);
        }
        applyExpression();

        // Store bot position in localStorage (keeps previous behaviour)
        const savedPosition = localStorage.getItem('miso-position');
        if (savedPosition) {
            try {
                const pos = JSON.parse(savedPosition);
                if (pos.bottom !== undefined) misoContainer.style.bottom = pos.bottom + 'px';
                if (pos.right !== undefined) misoContainer.style.right = pos.right + 'px';
            } catch (e) {
                // ignore parse errors
            }
        }

        // Categories (unchanged)
        const categories = {
            'modules': 'Modules',
            'docs': 'Documentation',
            'help': 'Help & Support',
            'settings': 'Settings',
            'about': 'About'
        };

        function renderCategories(filter = '') {
            categoryList.innerHTML = '';
            Object.entries(categories).forEach(([key, label]) => {
                if (filter === '' || label.toLowerCase().includes(filter.toLowerCase()) || key.includes(filter.toLowerCase())) {
                    const li = document.createElement('li');
                    li.className = 'miso-category-item';
                    li.textContent = label;
                    li.onclick = () => selectCategory(key);
                    categoryList.appendChild(li);
                }
            });
        }

        // Dragging functionality (unchanged behaviour)
        let isDragging = false;
        let startX, startY, startLeft, startTop;

        misoBot.addEventListener('mousedown', (e) => {
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            startLeft = misoContainer.offsetLeft;
            startTop = misoContainer.offsetTop;
            misoBot.style.cursor = 'grabbing';
            misoContainer.style.transform = '';
        });

        document.addEventListener('mousemove', (e) => {
            if (isDragging) {
                const deltaX = e.clientX - startX;
                const deltaY = e.clientY - startY;
                misoContainer.style.left = (startLeft + deltaX) + 'px';
                misoContainer.style.bottom = 'auto';
                misoContainer.style.right = 'auto';
                misoContainer.style.top = (startTop + deltaY) + 'px';
            } else {
                trackMouse(e.clientX, e.clientY);
                avoidIfNeeded(e.clientX, e.clientY);
            }
        });

        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                misoBot.style.cursor = 'grab';
                const rect = misoContainer.getBoundingClientRect();
                localStorage.setItem('miso-position', JSON.stringify({
                    bottom: window.innerHeight - rect.bottom,
                    right: window.innerWidth - rect.right
                }));
            }
        });

        // Eye tracking - smaller travel for inner pupils (suitable for 25px eyes)
        function trackMouse(mouseX, mouseY) {
            const leftEye = document.querySelector('.miso-eye-left');
            const rightEye = document.querySelector('.miso-eye-right');
            if (!leftEye || !rightEye) return;

            const leftRect = leftEye.getBoundingClientRect();
            const rightRect = rightEye.getBoundingClientRect();

            const leftCenterX = leftRect.left + leftRect.width / 2;
            const leftCenterY = leftRect.top + leftRect.height / 2;
            const rightCenterX = rightRect.left + rightRect.width / 2;
            const rightCenterY = rightRect.top + rightRect.height / 2;

            const distance = 3; // how far the eye shifts to indicate gaze

            const angleL = Math.atan2(mouseY - leftCenterY, mouseX - leftCenterX);
            const lx = Math.cos(angleL) * distance;
            const ly = Math.sin(angleL) * distance;
            leftEye.style.setProperty('--gaze-x', `${lx}px`);
            leftEye.style.setProperty('--gaze-y', `${ly}px`);

            const angleR = Math.atan2(mouseY - rightCenterY, mouseX - rightCenterX);
            const rx = Math.cos(angleR) * distance;
            const ry = Math.sin(angleR) * distance;
            rightEye.style.setProperty('--gaze-x', `${rx}px`);
            rightEye.style.setProperty('--gaze-y', `${ry}px`);
        }

        // Hover-away behaviour tuned for smaller bot
        const avoidThreshold = 80;
        let isAvoiding = false;
        function avoidIfNeeded(mouseX, mouseY) {
            const rect = misoBot.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;
            const dx = centerX - mouseX;
            const dy = centerY - mouseY;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (!isDragging && dist < avoidThreshold) {
                const strength = (1 - dist / avoidThreshold) * 40; // px to move
                const nx = dist === 0 ? 0 : (dx / dist);
                const ny = dist === 0 ? 0 : (dy / dist);
                misoContainer.style.transform = `translate(${nx * strength}px, ${ny * strength}px)`;
                misoContainer.style.transition = 'transform 0.14s ease';
                misoContainer.style.opacity = '0.95';
                isAvoiding = true;
            } else if (isAvoiding) {
                misoContainer.style.transform = '';
                misoContainer.style.transition = 'transform 0.22s ease';
                misoContainer.style.opacity = '1';
                isAvoiding = false;
            }
        }

        // Click interactions: single-click cycles expression, double-click opens modal
        let clickTimeout = null;
        misoBot.addEventListener('click', (e) => {
            if (isDragging) { e.stopPropagation(); return; }
            if (clickTimeout) {
                // double-click detected -> open modal
                clearTimeout(clickTimeout);
                clickTimeout = null;
                openModal();
                misoContainer.classList.add('blinking');
                setTimeout(() => misoContainer.classList.remove('blinking'), 300);
            } else {
                // schedule single-click action (cycle expression)
                clickTimeout = setTimeout(() => {
                    exprIndex = (exprIndex + 1) % expressions.length;
                    applyExpression();
                    // small blink on change
                    misoContainer.classList.add('blinking');
                    setTimeout(() => misoContainer.classList.remove('blinking'), 220);
                    clickTimeout = null;
                }, 220);
            }
            e.stopPropagation();
        });
        
        // Modal functions
        function openModal() {
            modalOverlay.style.display = 'block';
            searchModal.style.display = 'block';
            searchInput.value = '';
            renderCategories();
            searchInput.focus();
        }
        
        function closeModal() {
            modalOverlay.style.display = 'none';
            searchModal.style.display = 'none';
        }
        
        // Close modal button
        closeBtn.addEventListener('click', closeModal);
        
        // Close modal on overlay click
        modalOverlay.addEventListener('click', closeModal);
        
        // Search input filter
        searchInput.addEventListener('input', (e) => {
            renderCategories(e.target.value);
        });
        
        // Enter key to select first category
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const firstItem = categoryList.querySelector('.miso-category-item');
                if (firstItem) {
                    firstItem.click();
                }
            }
        });
        
        function selectCategory(category) {
            // Send message to Streamlit
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                data: category
            }, '*');
            closeModal();
        }
        
        // Prevent text selection while dragging
        document.addEventListener('selectstart', (e) => {
            if (isDragging) e.preventDefault();
        });
    </script>
    """
    st.markdown(html_code, unsafe_allow_html=True)


st.set_page_config(page_title="M.I.S.O. — Module Information System Organizer")
st.title("🎈 M.I.S.O.")
st.write("Module Information System Organizer")

# Render the M.I.S.O. bot (appears on all pages)
render_miso_bot()

# Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_name = None

# Authentication check
if not st.session_state.authenticated:
    st.markdown("---")
    st.subheader("Access Required")
    st.write("Who are you?")
    
    with st.form(key="login_form"):
        name = st.text_input("Enter your name:")
        login_submit = st.form_submit_button("Submit")
    
    if login_submit:
        if name.strip().lower() == "aj":
            st.session_state.authenticated = True
            st.session_state.user_name = name.strip()
            st.success("Welcome back, Creator!")
            st.rerun()
        else:
            st.error(f"Sorry, {name}. You can't continue. Only [Censored] can access M.I.S.O.")
    st.stop()

# Main M.I.S.O. interface (only shown if authenticated)
st.write(f"Welcome, {st.session_state.user_name}! 👋")

data = load_data()

# Ask which section to open
st.markdown("---")
st.write("Which section would you like to open?")
section_name = st.text_input("Enter section name:")

if section_name:
    section = section_name.strip()
    
    # Add new item form
    st.markdown("---")
    st.write("Add a new item to this section")
    with st.form(key="add_item"):
        title = st.text_input("Title")
        notes = st.text_area("Notes (optional)")
        submitted = st.form_submit_button("Add")
    
    if submitted and title:
        entry = {
            "title": title.strip(),
            "notes": notes.strip(),
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
        data.setdefault(section, []).append(entry)
        save_data(data)
        st.success(f"Added to {section}: {entry['title']}")
        st.rerun()
    
    # Display items in section
    st.markdown("---")
    st.subheader(section)
    items = data.get(section, [])
    
    if not items:
        st.info("No items in this section yet. Add one above.")
    else:
        for i, item in enumerate(items):
            with st.expander(f"{i+1}. {item['title']}"):
                st.write(item.get("notes", ""))
                st.write("Created:", item.get("created_at"))
                if st.button(f"Delete", key=f"del_{section}_{i}"):
                    items.pop(i)
                    data[section] = items
                    save_data(data)
                    st.rerun()

st.sidebar.markdown("---")
st.sidebar.write("Data file:", DATA_FILE)
