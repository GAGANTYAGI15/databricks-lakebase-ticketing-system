# Databricks Lakebase Ticketing System

A full-featured support ticket management system built with Streamlit and powered by Databricks Lakebase (Postgres).

## Features

✅ **Complete Ticket Management**
- View all tickets with status filtering
- Create new tickets with title and initial message
- Add messages/comments to tickets
- Update ticket status (open, in_progress, resolved)
- Dashboard with ticket statistics

✅ **Lakebase Integration**
- Uses Lakebase Postgres for data storage
- Connection configured via app.yaml environment variables
- Persistent database with existing schema

✅ **User-Friendly UI**
- Clean, responsive Streamlit interface
- Custom styling and visual indicators
- Real-time updates

## Architecture

```
Streamlit App (app.py)
    ↓
    ↓ Reads connection from app.yaml env vars
    ↓
Lakebase Postgres
    │
    ├── tickets table
    └── ticket_messages table
```

## Setup Instructions

### 1. Configure Database Connection

Edit `app.yaml` and set your Lakebase connection URL as an environment variable:

```yaml
env:
  - name: LAKEBASE_DATABASE_URL
    value: postgresql://app_user:password@host/databricks_postgres?sslmode=require
```

**Connection URL format:**
```
postgresql://role:password@host/databricks_postgres?sslmode=require
```

- **role**: Your database username (e.g., `app_user`)
- **password**: Your Lakebase password  
- **host**: Your Lakebase endpoint (e.g., `ep-xxx.database.us-east-2.cloud.databricks.com`)
- **database**: `databricks_postgres`

### 2. Deploy the App

**Using Databricks Apps:**

```bash
# Navigate to project directory
cd databricks-lakebase-ticketing-system

# Deploy
databricks apps deploy ticketing-system

# Check status and get URL
databricks apps get ticketing-system
```

**That's it!** The app will:
- Read the connection URL from app.yaml environment variables
- Connect to your existing Lakebase database
- Start serving the ticketing system

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
- Select and open a ticket to see messages and update status

### Create Ticket
- Fill in ticket title and optional initial message
- Submit to create a new ticket (automatically opens with status)

### Ticket Details
- View all messages for a ticket
- Add new messages
- Update ticket status

## Files

- **app.py** - Main Streamlit application
- **app.yaml** - Databricks Apps configuration with database connection
- **requirements.txt** - Python dependencies
- **README.md** - This file

## How It Works

1. **Configuration**: Edit `app.yaml` with your Lakebase connection URL
2. **Deployment**: Deploy the app using `databricks apps deploy`
3. **Connection**: App reads the database URL from environment variables
4. **Ready to Use**: Start creating and managing tickets!

## Security

✅ **Secure by Design**
- Connection URL configured via app.yaml environment variables
- No credentials hardcoded in source code
- Credentials managed through Databricks Apps deployment
- Environment variables isolated per app deployment

## Troubleshooting

**"LAKEBASE_DATABASE_URL is not set"**
- Edit `app.yaml` and configure the database URL in the `env` section
- Ensure the URL format is correct: `postgresql://user:password@host/database?sslmode=require`
- Redeploy the app after updating app.yaml

**Connection Failed**
- Verify your connection URL format in app.yaml
- Check that the Lakebase endpoint is accessible
- Ensure your database credentials are correct
- Verify the database name is `databricks_postgres`

**No Data Showing**
- Check database permissions for your user
- Verify you're connected to the correct database
- Ensure the tables `tickets` and `ticket_messages` exist

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
