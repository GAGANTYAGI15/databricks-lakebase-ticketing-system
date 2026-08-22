#!/usr/bin/env python3
"""
Lakebase Connection URL Helper

This script helps you generate the connection URL for the ticketing system app.
Run this from a Databricks notebook to get your connection URL.
"""

from databricks.sdk import WorkspaceClient

def get_lakebase_connection_url(
    project_id="my-lakebase",
    branch_id="production",
    endpoint_id="primary",
    database="databricks_postgres"
):
    """
    Generate a Lakebase connection URL with OAuth token.
    
    Args:
        project_id: Your Lakebase project ID
        branch_id: Branch name (default: production)
        endpoint_id: Endpoint name (default: primary)
        database: Database name (default: databricks_postgres)
    
    Returns:
        Connection URL string
    """
    w = WorkspaceClient()
    
    # Get endpoint details
    endpoint_name = f"projects/{project_id}/branches/{branch_id}/endpoints/{endpoint_id}"
    endpoint = w.postgres.get_endpoint(name=endpoint_name)
    host = endpoint.status.hosts.host
    
    # Get current user
    user = w.current_user.me()
    username = user.user_name
    
    # Generate OAuth token (valid for 1 hour)
    token = w.postgres.generate_database_credential(endpoint=endpoint_name).token
    
    # Build connection URL
    connection_url = f"postgresql://{username}:{token}@{host}:5432/{database}?sslmode=require"
    
    return connection_url, host

if __name__ == "__main__":
    print("\n" + "="*80)
    print("LAKEBASE CONNECTION URL GENERATOR")
    print("="*80 + "\n")
    
    try:
        url, host = get_lakebase_connection_url()
        
        print("✅ Connection URL generated successfully!\n")
        print("📋 Copy this URL and paste it into the ticketing app:")
        print("-" * 80)
        print(url)
        print("-" * 80)
        
        print("\n📌 Important Notes:")
        print("  • This token expires in 1 hour")
        print("  • For production, use a native Postgres password (non-expiring)")
        print("  • Keep this URL secure - it contains credentials!\n")
        
        print("🔧 Connection Details:")
        print(f"  Host: {host}")
        print(f"  Database: databricks_postgres")
        print(f"  SSL Mode: require\n")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("  1. Make sure you're running this from a Databricks notebook")
        print("  2. Verify your Lakebase project exists: 'my-lakebase'")
        print("  3. Check that you have access to the project\n")
