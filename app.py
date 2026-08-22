import streamlit as st
import psycopg
import os
from datetime import datetime
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config

# Page configuration
st.set_page_config(
    page_title="Support Ticket System",
    page_icon="🎫",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .ticket-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ddd;
        margin: 0.5rem 0;
    }
    .status-open { background-color: #fff3cd; border-color: #ffc107; }
    .status-in_progress { background-color: #cfe2ff; border-color: #0d6efd; }
    .status-resolved { background-color: #d1e7dd; border-color: #198754; }
    .priority-high { color: #dc3545; font-weight: bold; }
    .priority-medium { color: #fd7e14; }
    .priority-low { color: #6c757d; }
    .message-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 0.5rem;
        color: white;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_connection():
    """Get database connection with OAuth token"""
    try:
        # Get Lakebase connection details from environment
        host = os.environ.get("LAKEBASE_HOST")
        database = os.environ.get("LAKEBASE_DATABASE", "databricks_postgres")
        
        if not host:
            st.error("❌ LAKEBASE_HOST environment variable not set")
            return None
        
        # Generate OAuth token using Databricks SDK
        config = Config(
            host=os.environ.get("DATABRICKS_HOST"),
            token=os.environ.get("DATABRICKS_TOKEN")
        )
        w = WorkspaceClient(config=config)
        
        # Get current user for connection
        user = w.current_user.me()
        username = user.user_name
        
        # Generate database credential
        endpoint_name = os.environ.get("LAKEBASE_ENDPOINT")
        if not endpoint_name:
            st.error("❌ LAKEBASE_ENDPOINT environment variable not set")
            return None
            
        token = w.postgres.generate_database_credential(endpoint=endpoint_name).token
        
        # Create connection
        conn = psycopg.connect(
            host=host,
            dbname=database,
            user=username,
            password=token,
            sslmode="require"
        )
        return conn
    except Exception as e:
        st.error(f"❌ Database connection failed: {str(e)}")
        return None

def get_all_tickets(status_filter=None):
    """Fetch all tickets with optional status filter"""
    conn = get_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor() as cur:
            if status_filter and status_filter != "All":
                cur.execute("""
                    SELECT ticket_id, title, status, priority, category, created_by, created_at
                    FROM tickets
                    WHERE status = %s
                    ORDER BY created_at DESC
                """, (status_filter.lower(),))
            else:
                cur.execute("""
                    SELECT ticket_id, title, status, priority, category, created_by, created_at
                    FROM tickets
                    ORDER BY created_at DESC
                """)
            return cur.fetchall()
    except Exception as e:
        st.error(f"Error fetching tickets: {str(e)}")
        return []

def get_ticket_messages(ticket_id):
    """Fetch messages for a specific ticket"""
    conn = get_connection()
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
            return cur.fetchall()
    except Exception as e:
        st.error(f"Error fetching messages: {str(e)}")
        return []

def create_ticket(title, priority, category, created_by):
    """Create a new ticket"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tickets (title, status, priority, category, created_by)
                VALUES (%s, 'open', %s, %s, %s)
                RETURNING ticket_id
            """, (title, priority, category, created_by))
            conn.commit()
            return cur.fetchone()[0]
    except Exception as e:
        st.error(f"Error creating ticket: {str(e)}")
        conn.rollback()
        return False

def add_message(ticket_id, message_text, author):
    """Add a message to a ticket"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO ticket_messages (ticket_id, message_text, author)
                VALUES (%s, %s, %s)
            """, (ticket_id, message_text, author))
            
            # Update ticket's updated_at timestamp
            cur.execute("""
                UPDATE tickets
                SET updated_at = CURRENT_TIMESTAMP
                WHERE ticket_id = %s
            """, (ticket_id,))
            conn.commit()
            return True
    except Exception as e:
        st.error(f"Error adding message: {str(e)}")
        conn.rollback()
        return False

def update_ticket_status(ticket_id, new_status):
    """Update ticket status"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE tickets
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE ticket_id = %s
            """, (new_status, ticket_id))
            conn.commit()
            return True
    except Exception as e:
        st.error(f"Error updating status: {str(e)}")
        conn.rollback()
        return False

def get_ticket_stats():
    """Get ticket statistics"""
    conn = get_connection()
    if not conn:
        return {}
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN status = 'open' THEN 1 END) as open,
                    COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress,
                    COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved
                FROM tickets
            """)
            result = cur.fetchone()
            return {
                'total': result[0],
                'open': result[1],
                'in_progress': result[2],
                'resolved': result[3]
            }
    except Exception as e:
        st.error(f"Error fetching stats: {str(e)}")
        return {}

# Main App
def main():
    st.title("🎫 Support Ticket System")
    st.markdown("*Powered by Lakebase*")
    
    # Sidebar for navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["📊 Dashboard", "📋 View Tickets", "➕ Create Ticket"]
    )
    
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "📋 View Tickets":
        show_tickets()
    elif page == "➕ Create Ticket":
        show_create_ticket()

def show_dashboard():
    """Show dashboard with statistics"""
    st.header("Dashboard")
    
    stats = get_ticket_stats()
    
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(
                f'<div class="stat-card"><h2>{stats["total"]}</h2><p>Total Tickets</p></div>',
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                f'<div class="stat-card"><h2>{stats["open"]}</h2><p>Open</p></div>',
                unsafe_allow_html=True
            )
        
        with col3:
            st.markdown(
                f'<div class="stat-card"><h2>{stats["in_progress"]}</h2><p>In Progress</p></div>',
                unsafe_allow_html=True
            )
        
        with col4:
            st.markdown(
                f'<div class="stat-card"><h2>{stats["resolved"]}</h2><p>Resolved</p></div>',
                unsafe_allow_html=True
            )
    
    st.markdown("---")
    st.subheader("Recent Tickets")
    tickets = get_all_tickets()
    
    if tickets:
        for ticket in tickets[:5]:
            display_ticket_card(ticket, compact=True)
    else:
        st.info("No tickets found")

def show_tickets():
    """Show all tickets with filtering"""
    st.header("All Tickets")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        status_filter = st.selectbox(
            "Filter by status",
            ["All", "Open", "In_progress", "Resolved"]
        )
    
    tickets = get_all_tickets(status_filter if status_filter != "All" else None)
    
    if tickets:
        for ticket in tickets:
            display_ticket_card(ticket)
    else:
        st.info("No tickets found")

def display_ticket_card(ticket, compact=False):
    """Display a ticket card"""
    ticket_id, title, status, priority, category, created_by, created_at = ticket
    
    status_class = f"status-{status}"
    priority_class = f"priority-{priority}"
    
    with st.container():
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(
                f'<div class="ticket-card {status_class}">'
                f'<h4>#{ticket_id}: {title}</h4>'
                f'<p><span class="{priority_class}">Priority: {priority.upper()}</span> | '
                f'Status: {status.replace("_", " ").title()} | '
                f'Category: {category or "N/A"}</p>'
                f'<p><small>Created by: {created_by} | {created_at}</small></p>'
                f'</div>',
                unsafe_allow_html=True
            )
        
        with col2:
            if not compact:
                if st.button("View Details", key=f"view_{ticket_id}"):
                    st.session_state.selected_ticket = ticket_id
    
    if not compact and hasattr(st.session_state, 'selected_ticket') and st.session_state.selected_ticket == ticket_id:
        show_ticket_details(ticket_id)

def show_ticket_details(ticket_id):
    """Show detailed ticket view with messages"""
    st.markdown("---")
    st.subheader(f"Ticket #{ticket_id} Details")
    
    # Status update
    col1, col2 = st.columns([2, 1])
    with col1:
        new_status = st.selectbox(
            "Update Status",
            ["open", "in_progress", "resolved"],
            key=f"status_{ticket_id}"
        )
    with col2:
        if st.button("Update Status", key=f"update_{ticket_id}"):
            if update_ticket_status(ticket_id, new_status):
                st.success("✅ Status updated!")
                st.rerun()
    
    # Messages
    st.markdown("### Messages")
    messages = get_ticket_messages(ticket_id)
    
    if messages:
        for message in messages:
            message_id, text, author, created_at = message
            st.markdown(
                f'<div class="message-box">'
                f'<strong>{author}</strong> <small>({created_at})</small><br>'
                f'{text}'
                f'</div>',
                unsafe_allow_html=True
            )
    
    # Add new message
    st.markdown("### Add Message")
    with st.form(key=f"message_form_{ticket_id}"):
        message_text = st.text_area("Message", key=f"msg_{ticket_id}")
        author = st.text_input("Your Email", key=f"author_{ticket_id}")
        submit = st.form_submit_button("Send Message")
        
        if submit:
            if message_text and author:
                if add_message(ticket_id, message_text, author):
                    st.success("✅ Message added!")
                    st.rerun()
            else:
                st.error("Please fill in all fields")

def show_create_ticket():
    """Show create ticket form"""
    st.header("Create New Ticket")
    
    with st.form(key="create_ticket_form"):
        title = st.text_input("Title *", placeholder="Brief description of the issue")
        priority = st.selectbox("Priority *", ["low", "medium", "high"])
        category = st.selectbox(
            "Category",
            ["", "Access Issue", "Performance", "Feature Request", "Bug Report", "Other"]
        )
        created_by = st.text_input("Your Email *", placeholder="your.email@company.com")
        
        submit = st.form_submit_button("Create Ticket")
        
        if submit:
            if not title or not created_by:
                st.error("❌ Please fill in all required fields (marked with *)")
            else:
                ticket_id = create_ticket(title, priority, category or None, created_by)
                if ticket_id:
                    st.success(f"✅ Ticket #{ticket_id} created successfully!")
                    st.balloons()
                    # Clear form by rerunning
                    st.rerun()

if __name__ == "__main__":
    main()
