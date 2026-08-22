#!/usr/bin/env python3
"""
One-time setup script: stores the Lakebase connection URL in Databricks secrets.
Run this once to configure the app's database connection.

Usage:
    python setup_secrets.py
    
Or from a notebook:
    %run ./setup_secrets.py
"""

from databricks.sdk import WorkspaceClient
from databricks.sdk.service import workspace
import getpass

w = WorkspaceClient()

def setup_secrets():
    """Setup Databricks secrets for Lakebase connection."""
    
    print("\n" + "="*80)
    print("LAKEBASE TICKETING SYSTEM - SECRET SETUP")
    print("="*80 + "\n")
    
    # Create scope if it doesn't exist (will fail silently if exists)
    try:
        w.secrets.create_scope(scope="ticketing")
        print("✅ Created secret scope 'ticketing'")
    except Exception:
        print("ℹ️ Secret scope 'ticketing' already exists")
    
    # Get the Lakebase URL from user
    print("\n📝 Please provide your Lakebase connection URL")
    print("Format: postgresql://role:password@host:5432/databricks_postgres?sslmode=require\n")
    
    lakebase_url = getpass.getpass("Paste your Lakebase URL: ")
    
    # Store the secret
    w.secrets.put_secret(
        scope="ticketing",
        key="lakebase-url",
        string_value=lakebase_url
    )
    print("✅ Stored Lakebase URL in secrets")
    
    # Set permissions so all users can read
    try:
        w.secrets.put_acl(
            scope="ticketing",
            principal="users",
            permission=workspace.AclPermission.READ,
        )
        print("✅ Set read permissions for all users")
    except Exception as e:
        print(f"⚠️ Could not set permissions: {e}")
    
    print("\n" + "="*80)
    print("✅ SETUP COMPLETE!")
    print("="*80)
    print("\nThe app will now use this connection automatically.")
    print("To update the URL later, run this script again.\n")

if __name__ == "__main__":
    setup_secrets()
