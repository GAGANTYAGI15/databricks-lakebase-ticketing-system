# Databricks Lakebase Ticketing System

A full-featured support ticket management system built with Streamlit and powered by Databricks Lakebase (Postgres).

## Features

✅ **Complete Ticket Management**
- View all tickets with status filtering
- Create new tickets with priority and category
- Add messages/comments to tickets
- Update ticket status (open, in_progress, resolved)
- Dashboard with ticket statistics

✅ **Lakebase Integration**
- Uses Lakebase Postgres for data storage
- Connection URL-based authentication
- Supports both OAuth tokens and native Postgres passwords

✅ **User-Friendly UI**
- Clean, responsive Streamlit interface
- Custom styling and visual indicators
- Real-time updates

## Database Schema

The app uses two related tables:

### `tickets` table
```sql
ticket_id SERIAL PRIMARY KEY
title VARCHAR(255) NOT NULL
status VARCHAR(50) NOT NULL
priority VARCHAR(20) DEFAULT 'medium'
category VARCHAR(100)
created_by VARCHAR(255) NOT NULL
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

### `ticket_messages` table
```sql
message_id SERIAL PRIMARY KEY
ticket_id INTEGER NOT NULL (FOREIGN KEY -> tickets.ticket_id)
message_text TEXT NOT NULL
author VARCHAR(255) NOT NULL
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

## Setup Instructions

### 1. Database Setup

The database schema and sample data have already been created in your Lakebase project `my-lakebase`.

### 2. Get Your Connection URL

**Option A: Run the helper script**

Open a Databricks notebook and run:
```python
%run ./connection_helper.py
```

This will generate your connection URL with an OAuth token (valid for 1 hour).

**Option B: Manual construction**

Format: `postgresql://role:password@host:5432/databricks_postgres?sslmode=require`

- **role**: Your Databricks email (e.g., `gagantyagi2000@gmail.com`)
- **password**: OAuth token or native Postgres password
- **host**: Your Lakebase endpoint (e.g., `ep-muddy-shape-d8ufskmd.database.us-east-2.cloud.databricks.com`)
- **database**: `databricks_postgres`

### 3. Deploy the App

**Using Databricks Apps:**

```bash
# Initialize (if not already done)
apps init ticketing-system --path ./databricks-lakebase-ticketing-system

# Deploy
apps deploy ticketing-system

# Start
apps start ticketing-system

# Get the app URL
apps get ticketing-system
```

**Local Development:**

```bash
cd databricks-lakebase-ticketing-system
pip install -r requirements.txt
streamlit run app.py
```

### 4. Use the App

1. Open the app URL
2. Enter your Lakebase connection URL when prompted
3. Click "Connect"
4. Start managing tickets!

## Usage

### Dashboard
- View ticket statistics (total, open, in progress, resolved)
- See recent tickets at a glance

### View Tickets
- Browse all tickets
- Filter by status (All, Open, In Progress, Resolved)
- Click "View Details" to see messages and update status

### Create Ticket
- Fill in ticket details (title, priority, category)
- Submit to create a new ticket

### Ticket Details
- View all messages for a ticket
- Add new messages
- Update ticket status

## Architecture

```
Streamlit App (app.py)
    ↓
    ↓ psycopg2 connection
    ↓
Lakebase Postgres
    │
    ├── tickets table
    └── ticket_messages table
```

## Sample Data

The database includes:
- 3 sample tickets with different statuses
- 9 messages across the tickets (3 per ticket)
- Multiple priorities (high, medium, low)
- Different categories (Access Issue, Performance, Feature Request)

## Files

- `app.py` - Main Streamlit application
- `app.yaml` - Databricks Apps configuration
- `requirements.txt` - Python dependencies
- `connection_helper.py` - Helper script to generate connection URLs
- `README.md` - This file

## Security Notes

⚠️ **Important:**
- Never commit connection URLs with credentials to git
- OAuth tokens expire after 1 hour
- For production, use native Postgres passwords (non-expiring)
- Keep connection URLs secure

## Troubleshooting

**Connection Failed**
- Verify your connection URL format
- Check that the Lakebase endpoint is accessible
- Ensure your credentials are correct
- For OAuth tokens, regenerate if expired (1 hour)

**No Data Showing**
- Verify the database schema exists
- Check that sample data was inserted
- Confirm you're connected to the correct database

**Permission Errors**
- Ensure your Postgres role has proper permissions
- Check that you can connect with the same credentials via psql

## Future Enhancements

- ☐ Ticket assignment to users
- ☐ Email notifications
- ☐ File attachments
- ☐ Ticket search functionality
- ☐ Advanced filtering (by date, priority, category)
- ☐ User authentication
- ☐ Export tickets to CSV
- ☐ Ticket history/audit log

## License

MIT License - feel free to use and modify!

## Contact

Built as part of the Databricks Lakebase Boot Camp Day 1 Homework.