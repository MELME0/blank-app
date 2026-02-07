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
        * {
            box-sizing: border-box;
        }
        #miso-container {
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 9999;
            font-family: Arial, sans-serif;
        }
        
        #miso-bot {
            position: relative;
            width: 44px;
            height: 44px;
            cursor: grab;
            user-select: none;
        }
        
        #miso-bot:active {
            cursor: grabbing;
        }
        
        .miso-body {
            position: absolute;
            width: 44px;
            height: 44px;
            border: 2px solid #d0d0d0;
            border-radius: 50%;
            background: #f5f5f5;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            transition: all 0.1s ease;
        }
        
        .miso-eye {
            position: absolute;
            width: 5px;
            height: 5px;
            background: #000;
            border-radius: 50%;
            top: 14px;
        }
        
        .miso-eye-left {
            left: 12px;
        }
        
        .miso-eye-right {
            right: 12px;
        }
        
        .miso-pupil {
            position: absolute;
            width: 3px;
            height: 3px;
            background: #000;
            border-radius: 50%;
            top: 1px;
            left: 1px;
        }
        
        #miso-bot.blinking .miso-eye {
            height: 1px;
            top: 15.5px;
        }
        
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
            <div class="miso-eye miso-eye-left">
                <div class="miso-pupil" id="pupil-left"></div>
            </div>
            <div class="miso-eye miso-eye-right">
                <div class="miso-pupil" id="pupil-right"></div>
            </div>
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
        const pupilLeft = document.getElementById('pupil-left');
        const pupilRight = document.getElementById('pupil-right');
        
        // Store bot position in localStorage
        const savedPosition = localStorage.getItem('miso-position');
        if (savedPosition) {
            const pos = JSON.parse(savedPosition);
            misoContainer.style.bottom = pos.bottom + 'px';
            misoContainer.style.right = pos.right + 'px';
        }
        
        // Categories
        const categories = {
            'modules': 'Modules',
            'docs': 'Documentation',
            'help': 'Help & Support',
            'settings': 'Settings',
            'about': 'About'
        };
        
        // Render categories
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
        
        // Dragging functionality
        let isDragging = false;
        let startX, startY, startLeft, startTop;
        
        misoBot.addEventListener('mousedown', (e) => {
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            startLeft = misoContainer.offsetLeft;
            startTop = misoContainer.offsetTop;
            misoBot.style.cursor = 'grabbing';
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
                // Eye tracking - look at mouse
                trackMouse(e.clientX, e.clientY);
            }
        });
        
        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                misoBot.style.cursor = 'grab';
                
                // Save position
                const rect = misoContainer.getBoundingClientRect();
                localStorage.setItem('miso-position', JSON.stringify({
                    bottom: window.innerHeight - rect.bottom,
                    right: window.innerWidth - rect.right
                }));
            }
        });
        
        // Eye tracking function
        function trackMouse(mouseX, mouseY) {
            const botRect = misoBot.getBoundingClientRect();
            const botCenterX = botRect.left + botRect.width / 2;
            const botCenterY = botRect.top + botRect.height / 2;
            
            // Calculate angle to mouse
            const angle = Math.atan2(mouseY - botCenterY, mouseX - botCenterX);
            const distance = 1.5; // How far the pupil moves
            
            // Move left pupil
            const leftPupilX = Math.cos(angle) * distance;
            const leftPupilY = Math.sin(angle) * distance;
            pupilLeft.style.transform = `translate(${leftPupilX}px, ${leftPupilY}px)`;
            
            // Move right pupil
            const rightPupilX = Math.cos(angle) * distance;
            const rightPupilY = Math.sin(angle) * distance;
            pupilRight.style.transform = `translate(${rightPupilX}px, ${rightPupilY}px)`;
        }
        
        // Click to open modal
        misoBot.addEventListener('click', (e) => {
            if (!isDragging) {
                openModal();
                // Blink effect
                misoBot.classList.add('blinking');
                setTimeout(() => misoBot.classList.remove('blinking'), 300);
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
