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
- Connection stored securely in Databricks secrets
- Auto-creates database tables on first run

✅ **User-Friendly UI**
- Clean, responsive Streamlit interface
- Custom styling and visual indicators
- Real-time updates

## Architecture

```
Streamlit App (app.py)
    ↓
    ↓ Reads connection from Databricks secrets
    ↓ Auto-creates tables if not exists
    ↓
Lakebase Postgres
    │
    ├── tickets table
    └── ticket_messages table
```

## Setup Instructions

### 1. Configure Database Connection

Run the setup script to store your Lakebase connection URL in Databricks secrets:

```python
%run ./setup_secrets.py
```

This will:
- Create a secret scope called "ticketing"
- Prompt you to enter your Lakebase connection URL
- Store it securely in Databricks secrets
- Set permissions for all users to read the secret

**Connection URL format:**
```
postgresql://role:password@host:5432/databricks_postgres?sslmode=require
```

- **role**: Your Databricks email
- **password**: OAuth token or native Postgres password
- **host**: Your Lakebase endpoint (e.g., `ep-xxx.database.cloud.databricks.com`)
- **database**: `databricks_postgres`

### 2. Deploy the App

**Using Databricks Apps:**

```bash
# Initialize
databricks apps init ticketing-system --path ./databricks-lakebase-ticketing-system

# Deploy
databricks apps deploy ticketing-system

# Start
databricks apps start ticketing-system

# Get the app URL
databricks apps get ticketing-system
```

**That's it!** The app will:
- Read the connection URL from secrets
- Automatically create the database tables if they don't exist
- Start serving the ticketing system

### 3. (Optional) Manual Database Initialization

If you prefer to create tables manually before deploying:

```python
%run ./init_schema.py
```

This creates the `tickets` and `ticket_messages` tables if they don't exist.

## Database Schema

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

## Files

- **app.py** - Main Streamlit application with auto-table creation
- **setup_secrets.py** - One-time setup script to store connection URL
- **init_schema.py** - Optional script to manually initialize database
- **app.yaml** - Databricks Apps configuration
- **requirements.txt** - Python dependencies
- **README.md** - This file

## How It Works

1. **First Time Setup**: Run `setup_secrets.py` to store your Lakebase URL
2. **Deployment**: Deploy the app - it reads from secrets automatically
3. **Auto-Init**: On first run, app creates tables if they don't exist
4. **Ready to Use**: Start creating and managing tickets!

## Security

✅ **Secure by Design**
- Connection URL stored in Databricks secrets (encrypted)
- No credentials in code or config files
- No manual connection URL input in the app
- Automatic table creation (no manual SQL execution needed)

## Troubleshooting

**"Could not retrieve database connection from secrets"**
- Run `setup_secrets.py` to configure the connection
- Verify the secret scope "ticketing" exists
- Check that the secret key "lakebase-url" is set

**Connection Failed**
- Verify your connection URL format
- Check that the Lakebase endpoint is accessible
- Ensure your credentials are correct
- For OAuth tokens, regenerate if expired (1 hour)

**No Data Showing**
- Tables are created automatically on first run
- Check database permissions
- Verify you're connected to the correct database

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

MIT License

## Contact

Built as part of the Databricks Lakebase Boot Camp Day 1 Homework.
