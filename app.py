import streamlit as st
import psycopg2
import os
import html as html_escape
import pandas as pd
from datetime import datetime
from contextlib import contextmanager

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Support Hub",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------------------------
# Global styling — modern SaaS look (Linear / Intercom direction)
#
# Colors are hardcoded (not CSS variables) and applied to every nested
# Streamlit container, because the host page's own theme can otherwise
# win the cascade and leave text the same color as its background.
# ---------------------------------------------------------------------------
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden;}

    html, body,
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stHeader"],
    [data-testid="stVerticalBlock"],
    [data-testid="stHorizontalBlock"],
    [data-testid="column"],
    .main {
        background-color: #fafafa !important;
        color: #18181b !important;
        color-scheme: light !important;
    }

    [data-testid="stHeader"] { background-color: transparent !important; }

    * { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 1200px;
    }

    [data-testid="stSidebar"],
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e5e7eb;
        width: 240px !important;
        color: #18181b !important;
    }
    [data-testid="stSidebar"] > div:first-child { padding: 1.5rem 0.9rem; }
    [data-testid="stSidebar"] * { color: #18181b !important; }

    .sidebar-brand {
        font-size: 0.95rem;
        font-weight: 700;
        padding: 0.25rem 0.5rem 1.5rem 0.5rem;
        letter-spacing: -0.01em;
    }

    .nav-active {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4rem 0.6rem;
        margin: 0.1rem 0;
        border-radius: 6px;
        background: #eef2ff;
        color: #4f46e5 !important;
        font-size: 0.85rem;
        font-weight: 600;
        border-left: 2px solid #4f46e5;
    }

    [data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        color: #52525b !important;
        border: none;
        text-align: left;
        justify-content: flex-start;
        font-size: 0.85rem;
        font-weight: 500;
        padding: 0.4rem 0.6rem;
        border-radius: 6px;
        box-shadow: none;
        width: 100%;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #f0f0f1 !important;
        color: #18181b !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: #4f46e5 !important;
        color: #ffffff !important;
        font-weight: 600;
        margin-top: 0.75rem;
        padding: 0.45rem 0.6rem;
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background: #4338ca !important;
    }
    [data-testid="stSidebar"] hr { margin: 1rem 0; border-color: #e5e7eb; }

    .page-title { font-size: 1.4rem; font-weight: 700; letter-spacing: -0.01em; margin: 0; color: #18181b; }
    .page-subtitle { color: #71717a; font-size: 0.9rem; margin: 0.25rem 0 0 0; }

    .stats-row {
        display: flex;
        gap: 2.5rem;
        padding: 1.25rem 0;
        margin: 1.25rem 0 1.75rem 0;
        border-top: 1px solid #e5e7eb;
        border-bottom: 1px solid #e5e7eb;
    }
    .stat-block { display: flex; flex-direction: column; gap: 0.2rem; }
    .stat-label { font-size: 0.78rem; color: #71717a; font-weight: 500; }
    .stat-value { font-size: 1.6rem; font-weight: 700; color: #18181b; }

    .banner {
        display: flex;
        align-items: flex-start;
        gap: 0.6rem;
        padding: 0.65rem 0.9rem;
        border-radius: 8px;
        font-size: 0.85rem;
        margin-bottom: 1rem;
        border: 1px solid;
    }
    .banner-error { background: #fee2e2 !important; border-color: #fecaca; color: #b91c1c !important; }
    .banner-success { background: #d1fae5 !important; border-color: #a7f3d0; color: #047857 !important; }

    .ticket-title-lg { font-size: 1.3rem; font-weight: 700; margin: 0 0 0.35rem 0; letter-spacing: -0.01em; color: #18181b; }
    .ticket-meta-row { display: flex; gap: 0.5rem; font-size: 0.82rem; color: #71717a; margin-bottom: 1.25rem; }

    .msg-row { display: flex; gap: 0.75rem; padding: 0.9rem 0; border-bottom: 1px solid #f4f4f5; }
    .msg-avatar {
        width: 28px; height: 28px; border-radius: 50%;
        background: #eef2ff; color: #4f46e5;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.7rem; font-weight: 700; flex-shrink: 0;
    }
    .msg-author { font-weight: 600; font-size: 0.85rem; color: #18181b; }
    .msg-time { color: #71717a; font-size: 0.75rem; margin-left: 0.5rem; }
    .msg-text { font-size: 0.87rem; color: #18181b; margin-top: 0.2rem; line-height: 1.5; }

    .side-label { font-size: 0.72rem; font-weight: 600; color: #71717a; text-transform: uppercase; letter-spacing: 0.04em; margin: 0.9rem 0 0.25rem 0; }
    .side-value { font-size: 0.87rem; font-weight: 500; color: #18181b; }

    .stButton > button {
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 500;
        background-color: #ffffff !important;
        color: #18181b !important;
        border: 1px solid #d4d4d8 !important;
    }
    .stButton > button:hover {
        background-color: #f4f4f5 !important;
        border-color: #a1a1aa !important;
    }
    .stButton > button[kind="primary"] {
        background-color: #4f46e5 !important;
        color: #ffffff !important;
        border: none !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #4338ca !important;
    }
    /* Sidebar buttons stay flat/transparent — these rules are more specific
       than the ones above, so they win inside the sidebar. */
    [data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        border: none !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #f0f0f1 !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: #4f46e5 !important;
        border: none !important;
    }

    /* Text inputs, textareas, selectboxes — force light background + dark text */
    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input,
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] span {
        background-color: #ffffff !important;
        color: #18181b !important;
        border-color: #d4d4d8 !important;
    }
    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: #a1a1aa !important;
        opacity: 1 !important;
    }
    /* The selectbox dropdown menu is rendered in a portal outside the normal
       tree, so it needs its own (unscoped) rule. */
    div[data-baseweb="popover"] li,
    div[data-baseweb="menu"] li,
    ul[role="listbox"] li {
        background-color: #ffffff !important;
        color: #18181b !important;
    }
    div[data-baseweb="popover"] li:hover,
    div[data-baseweb="menu"] li:hover {
        background-color: #f4f4f5 !important;
    }

    /* Native table used for ticket lists — gives real resizable column
       borders (drag them) and automatic text truncation instead of
       hand-rolled HTML columns overflowing into each other. */
    [data-testid="stDataFrame"] { border: 1px solid #e5e7eb; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

STATUSES = ["open", "in_progress", "resolved"]
STATUS_LABELS = {"open": "Open", "in_progress": "In Progress", "resolved": "Resolved"}

# ---------------------------------------------------------------------------
# Database connection
#
# Credentials are read from environment variables — never hardcode them.
# In a Databricks App, set these as app resources/secrets (e.g. via
# app.yaml env vars or a secret scope), not literal strings in source.
# ---------------------------------------------------------------------------
def get_connection_url():
    url = os.environ.get("LAKEBASE_DATABASE_URL")
    if not url:
        try:
            url = st.secrets.get("LAKEBASE_DATABASE_URL", None)
        except Exception:
            pass
    if not url:
        raise RuntimeError(
            "LAKEBASE_DATABASE_URL is not set. Configure it as an environment "
            "variable in app.yaml — do not hardcode credentials in source."
        )
    return url


@contextmanager
def get_connection():
    """Yield a fresh connection per call. Never reused/cached across calls,
    so a failed query on one call can never poison a later call."""
    conn = None
    try:
        conn = psycopg2.connect(get_connection_url())
        yield conn
    except Exception as e:
        st.session_state["last_error"] = str(e)
        yield None
    finally:
        if conn:
            conn.close()


def check_database():
    """Verify the expected tables/columns are reachable.
    Does NOT run DDL against tables that already exist in the real schema."""
    with get_connection() as conn:
        if not conn:
            return False
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT ticket_id, title, status, created_by, created_at FROM tickets LIMIT 1")
                cur.execute("SELECT message_id, ticket_id, message_text, author, created_at FROM ticket_messages LIMIT 1")
            return True
        except Exception as e:
            conn.rollback()
            st.session_state["last_error"] = str(e)
            return False


# ---------------------------------------------------------------------------
# CRUD — matches the ACTUAL schema only:
#   tickets(ticket_id, title, status, created_by, created_at)
#   ticket_messages(message_id, ticket_id, message_text, author, created_at)
# ---------------------------------------------------------------------------
def get_all_tickets(status_filter=None):
    with get_connection() as conn:
        if not conn:
            return []
        try:
            with conn.cursor() as cur:
                if status_filter and status_filter != "All":
                    cur.execute("""
                        SELECT ticket_id, title, status, created_by, created_at
                        FROM tickets
                        WHERE status = %s
                        ORDER BY created_at DESC
                    """, (status_filter,))
                else:
                    cur.execute("""
                        SELECT ticket_id, title, status, created_by, created_at
                        FROM tickets
                        ORDER BY created_at DESC
                    """)
                rows = cur.fetchall()
            conn.commit()
            return rows
        except Exception as e:
            conn.rollback()
            st.session_state["last_error"] = f"Error fetching tickets: {e}"
            return []


def get_ticket(ticket_id):
    with get_connection() as conn:
        if not conn:
            return None
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT ticket_id, title, status, created_by, created_at
                    FROM tickets WHERE ticket_id = %s
                """, (ticket_id,))
                row = cur.fetchone()
            conn.commit()
            return row
        except Exception as e:
            conn.rollback()
            st.session_state["last_error"] = f"Error fetching ticket: {e}"
            return None


def get_ticket_messages(ticket_id):
    with get_connection() as conn:
        if not conn:
            return []
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT message_id, message_text, author, created_at
                    FROM ticket_messages
                    WHERE ticket_id = %s
                    ORDER BY created_at ASC
                """, (ticket_id,))
                rows = cur.fetchall()
            conn.commit()
            return rows
        except Exception as e:
            conn.rollback()
            st.session_state["last_error"] = f"Error fetching messages: {e}"
            return []


def create_ticket(title, created_by):
    with get_connection() as conn:
        if not conn:
            return None
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO tickets (title, status, created_by)
                    VALUES (%s, 'open', %s)
                    RETURNING ticket_id
                """, (title, created_by))
                new_id = cur.fetchone()[0]
            conn.commit()
            return new_id
        except Exception as e:
            conn.rollback()
            st.session_state["last_error"] = f"Error creating ticket: {e}"
            return None


def add_message(ticket_id, message_text, author):
    with get_connection() as conn:
        if not conn:
            return False
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO ticket_messages (ticket_id, message_text, author)
                    VALUES (%s, %s, %s)
                """, (ticket_id, message_text, author))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            st.session_state["last_error"] = f"Error adding message: {e}"
            return False


def update_ticket_status(ticket_id, new_status):
    with get_connection() as conn:
        if not conn:
            return False
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE tickets SET status = %s WHERE ticket_id = %s
                """, (new_status, ticket_id))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            st.session_state["last_error"] = f"Error updating status: {e}"
            return False


def get_ticket_stats():
    with get_connection() as conn:
        if not conn:
            return {}
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        COUNT(*),
                        COUNT(*) FILTER (WHERE status = 'open'),
                        COUNT(*) FILTER (WHERE status = 'in_progress'),
                        COUNT(*) FILTER (WHERE status = 'resolved')
                    FROM tickets
                """)
                total, open_c, prog_c, res_c = cur.fetchone()
            conn.commit()
            return {"total": total, "open": open_c, "in_progress": prog_c, "resolved": res_c}
        except Exception as e:
            conn.rollback()
            st.session_state["last_error"] = f"Error fetching stats: {e}"
            return {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def esc(val):
    return html_escape.escape(str(val)) if val is not None else ""


def fmt_date(value, fmt="%b %d"):
    try:
        if isinstance(value, str):
            value = datetime.strptime(value.split(".")[0], "%Y-%m-%d %H:%M:%S")
        return value.strftime(fmt)
    except Exception:
        return str(value)[:10]


def render_banner():
    err = st.session_state.pop("last_error", None)
    if err:
        st.markdown(f'<div class="banner banner-error">⚠️ {esc(err)}</div>', unsafe_allow_html=True)
    ok = st.session_state.pop("last_success", None)
    if ok:
        st.markdown(f'<div class="banner banner-success">✓ {esc(ok)}</div>', unsafe_allow_html=True)


def _status_style(val):
    styles = {
        "Open": "color: #b45309; font-weight: 600;",
        "In Progress": "color: #1d4ed8; font-weight: 600;",
        "Resolved": "color: #047857; font-weight: 600;",
    }
    return styles.get(val, "")


def render_ticket_list(tickets, key_prefix):
    """Native, resizable data grid — drag the column border in the header
    to resize, and long text truncates instead of overflowing into the
    next column."""
    if not tickets:
        st.markdown('<p style="color:#71717a;font-size:0.85rem;">No tickets found.</p>', unsafe_allow_html=True)
        return

    df = pd.DataFrame(tickets, columns=["ticket_id", "title", "status", "created_by", "created_at"])
    view = pd.DataFrame({
        "Ticket": df["ticket_id"].apply(lambda x: f"#{x}"),
        "Title": df["title"],
        "Status": df["status"].map(STATUS_LABELS),
        "Created by": df["created_by"],
        "Created": df["created_at"].apply(fmt_date),
    })

    styled = view.style.map(_status_style, subset=["Status"])

    st.dataframe(
        styled,
        use_container_width=True,
        hide_index=True,
        key=f"df_{key_prefix}",
        column_config={
            "Ticket": st.column_config.TextColumn(width="small"),
            "Title": st.column_config.TextColumn(width="large"),
            "Status": st.column_config.TextColumn(width="small"),
            "Created by": st.column_config.TextColumn(width="medium"),
            "Created": st.column_config.TextColumn(width="small"),
        },
    )

    # Row-click selection on st.dataframe needs a newer Streamlit release
    # than this app can rely on, so ticket opening uses a plain dropdown +
    # button instead — works on every Streamlit version.
    st.markdown('<div style="height:0.6rem;"></div>', unsafe_allow_html=True)
    options = {f"#{r.ticket_id} — {r.title}": int(r.ticket_id) for r in df.itertuples()}
    col_select, col_open = st.columns([4, 1])
    with col_select:
        choice = st.selectbox(
            "Open a ticket", list(options.keys()),
            key=f"pick_{key_prefix}", label_visibility="collapsed"
        )
    with col_open:
        if st.button("Open →", key=f"open_{key_prefix}", use_container_width=True):
            st.session_state.selected_ticket = options[choice]
            st.rerun()


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def page_overview():
    st.markdown('<div class="page-title">Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Monitor and manage your support requests.</div>', unsafe_allow_html=True)

    stats = get_ticket_stats()
    render_banner()
    if stats:
        st.markdown(f"""
        <div class="stats-row">
            <div class="stat-block"><div class="stat-label">Total tickets</div><div class="stat-value">{stats['total']}</div></div>
            <div class="stat-block"><div class="stat-label">Open</div><div class="stat-value">{stats['open']}</div></div>
            <div class="stat-block"><div class="stat-label">In progress</div><div class="stat-value">{stats['in_progress']}</div></div>
            <div class="stat-block"><div class="stat-label">Resolved</div><div class="stat-value">{stats['resolved']}</div></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="font-weight:600; font-size:0.95rem; margin-bottom:0.5rem; color:#18181b;">Recent Tickets</div>', unsafe_allow_html=True)
    tickets = get_all_tickets()
    render_ticket_list(tickets[:10], key_prefix="ov")


def page_ticket_list(status_filter, title):
    st.markdown(f'<div class="page-title">{esc(title)}</div>', unsafe_allow_html=True)
    st.markdown('<div style="height: 0.75rem;"></div>', unsafe_allow_html=True)
    render_banner()
    tickets = get_all_tickets(status_filter)
    render_ticket_list(tickets, key_prefix="list")


def page_ticket_detail(ticket_id):
    if st.button("← Back"):
        st.session_state.selected_ticket = None
        st.rerun()

    render_banner()
    ticket = get_ticket(ticket_id)
    if not ticket:
        st.markdown('<div class="banner banner-error">Ticket not found.</div>', unsafe_allow_html=True)
        return

    ticket_id, title, status, created_by, created_at = ticket
    messages = get_ticket_messages(ticket_id)

    col_main, col_side = st.columns([2.2, 1])

    with col_main:
        st.markdown(f'<div class="ticket-title-lg">{esc(title)}</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="ticket-meta-row"><span>#{ticket_id}</span><span>•</span>'
            f'<span>Created by {esc(created_by)}</span><span>•</span>'
            f'<span>{fmt_date(created_at, "%b %d, %Y at %I:%M %p")}</span></div>',
            unsafe_allow_html=True
        )

        st.markdown('<div style="font-weight:600; font-size:0.85rem; color:#71717a; margin-bottom:0.25rem;">Conversation</div>', unsafe_allow_html=True)

        if messages:
            for message_id, text, author, msg_created_at in messages:
                initials = "".join([w[0].upper() for w in author.split("@")[0].split(".")[:2]]) or "?"
                st.markdown(f"""
                    <div class="msg-row">
                        <div class="msg-avatar">{esc(initials)}</div>
                        <div style="flex:1;">
                            <span class="msg-author">{esc(author)}</span>
                            <span class="msg-time">{fmt_date(msg_created_at, "%I:%M %p")}</span>
                            <div class="msg-text">{esc(text)}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<p style="color:#71717a; font-size: 0.85rem;">No messages yet.</p>', unsafe_allow_html=True)

        st.markdown('<div style="height: 0.75rem;"></div>', unsafe_allow_html=True)
        with st.form(key=f"message_form_{ticket_id}", clear_on_submit=True):
            message_text = st.text_area("Message", label_visibility="collapsed", placeholder="Write a reply...")
            author = st.text_input("Your email", label_visibility="collapsed", placeholder="your.email@company.com")
            submit = st.form_submit_button("Send")
            if submit:
                if message_text and author:
                    if add_message(ticket_id, message_text, author):
                        st.session_state["last_success"] = "Message sent."
                        st.rerun()
                else:
                    st.session_state["last_error"] = "Please fill in both fields."
                    st.rerun()

    with col_side:
        st.markdown('<div class="side-label">Status</div>', unsafe_allow_html=True)
        new_status = st.selectbox(
            "Status", STATUSES, index=STATUSES.index(status),
            key=f"status_{ticket_id}", label_visibility="collapsed"
        )
        if new_status != status:
            if st.button("Update status", key=f"update_{ticket_id}"):
                if update_ticket_status(ticket_id, new_status):
                    st.session_state["last_success"] = "Status updated."
                    st.rerun()

        st.markdown('<div class="side-label">Created by</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="side-value">{esc(created_by)}</div>', unsafe_allow_html=True)

        st.markdown('<div class="side-label">Created</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="side-value">{fmt_date(created_at, "%b %d, %Y at %I:%M %p")}</div>', unsafe_allow_html=True)


def page_new_ticket():
    st.markdown('<div class="page-title">New support ticket</div>', unsafe_allow_html=True)
    st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)
    render_banner()

    with st.form(key="create_ticket_form", clear_on_submit=True):
        title = st.text_input("Title", placeholder="Brief description of the issue")
        message = st.text_area("Message", placeholder="Describe the issue in detail")
        created_by = st.text_input("Created by", placeholder="your.email@company.com")

        c1, c2 = st.columns([1, 1])
        with c1:
            cancel = st.form_submit_button("Cancel")
        with c2:
            submit = st.form_submit_button("Create ticket", type="primary")

        if cancel:
            st.session_state.current_page = "overview"
            st.rerun()

        if submit:
            if not title or not created_by:
                st.session_state["last_error"] = "Title and Created by are required."
                st.rerun()
            else:
                new_id = create_ticket(title, created_by)
                if new_id:
                    if message:
                        add_message(new_id, message, created_by)
                    st.session_state["last_success"] = f"Ticket #{new_id} created."
                    st.session_state.selected_ticket = new_id
                    st.rerun()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    if "current_page" not in st.session_state:
        st.session_state.current_page = "overview"
    if "selected_ticket" not in st.session_state:
        st.session_state.selected_ticket = None

    if not check_database():
        st.markdown(f'<div class="banner banner-error">⚠️ Database unavailable: {esc(st.session_state.get("last_error", ""))}</div>', unsafe_allow_html=True)

    nav_items = [
        ("overview", "🎯", "Overview"),
        ("all_tickets", "📋", "All Tickets"),
        ("open", "●", "Open"),
        ("in_progress", "●", "In Progress"),
        ("resolved", "●", "Resolved"),
    ]

    with st.sidebar:
        st.markdown('<div class="sidebar-brand">🎫 Support Hub</div>', unsafe_allow_html=True)
        for page_key, icon, label in nav_items:
            is_active = (st.session_state.current_page == page_key and not st.session_state.selected_ticket)
            if is_active:
                st.markdown(f'<div class="nav-active">{icon} {label}</div>', unsafe_allow_html=True)
            else:
                if st.button(f"{icon}  {label}", key=f"nav_{page_key}"):
                    st.session_state.current_page = page_key
                    st.session_state.selected_ticket = None
                    st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("＋  New Ticket", key="nav_new", type="primary"):
            st.session_state.current_page = "new_ticket"
            st.session_state.selected_ticket = None
            st.rerun()

    if st.session_state.selected_ticket:
        page_ticket_detail(st.session_state.selected_ticket)
    elif st.session_state.current_page == "overview":
        page_overview()
    elif st.session_state.current_page == "new_ticket":
        page_new_ticket()
    elif st.session_state.current_page == "all_tickets":
        page_ticket_list(None, "All Tickets")
    elif st.session_state.current_page == "open":
        page_ticket_list("open", "Open Tickets")
    elif st.session_state.current_page == "in_progress":
        page_ticket_list("in_progress", "In Progress")
    elif st.session_state.current_page == "resolved":
        page_ticket_list("resolved", "Resolved Tickets")


if __name__ == "__main__":
    main()