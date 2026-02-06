import json
from pathlib import Path
from datetime import datetime
import streamlit as st

DATA_FILE = Path(".help_data.json")


def load_data() -> dict:
    if not DATA_FILE.exists():
        return {}
    try:
        return json.loads(DATA_FILE.read_text())
    except Exception:
        return {}


def save_data(data: dict):
    DATA_FILE.write_text(json.dumps(data, indent=2))


st.set_page_config(page_title="M.I.S.O. — Module Information System Organizer")
st.title("🎈 M.I.S.O.")
st.write("Module Information System Organizer")

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
