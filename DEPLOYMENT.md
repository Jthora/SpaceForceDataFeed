# Deployment Guide

This guide provides step-by-step instructions for deploying the Space Force Events Dashboard on Replit.

## Prerequisites

Before deploying, ensure you have:
- A Replit account
- Access to the required API keys and database credentials

## Step 1: Fork the Project

1. Visit the project repository on Replit
2. Click "Fork" to create your copy of the project
3. Wait for Replit to set up the development environment

## Step 2: Configure Environment Variables

The following environment variables are required and should be set in Replit's Secrets tab:

```
DATABASE_URL=postgresql://[username]:[password]@[host]:[port]/[database]
PGUSER=[database username]
PGPASSWORD=[database password]
PGHOST=[database host]
PGPORT=[database port]
PGDATABASE=[database name]
```

To set up the environment variables:
1. Click on "Tools" in the left sidebar
2. Select "Secrets"
3. Add each required variable

## Step 3: Database Setup

The database will be automatically created and configured when you run the project for the first time. The necessary tables will be created automatically.

## Step 4: Running the Application

1. Click the "Run" button in Replit
2. Wait for the application to start (this may take a few moments)
3. The application will be available at the URL provided by Replit

## Step 5: Verify Installation

1. Check the application logs for any errors
2. Verify that the dashboard loads correctly
3. Test the news feed and event tracking functionality
4. Confirm that notifications are working

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify database credentials in Secrets
   - Check if the database is accessible from Replit

2. **Missing Dependencies**
   - The project will automatically install required dependencies
   - If needed, manually trigger a reinstall using the Package Manager

3. **Port Conflicts**
   - The application runs on port 5000 by default
   - Port can be modified in `.streamlit/config.toml`

### Logs and Monitoring

- Access logs through Replit's console
- Monitor application performance in the Replit dashboard
- Check database connectivity using the provided tools

## Maintenance

### Updates and Upgrades

1. Pull latest changes from the repository
2. Replit will automatically update dependencies
3. Restart the application using the "Run" button

### Backup and Recovery

1. Database backups are handled by Replit
2. Code changes are version controlled through Replit
3. Environment variables should be backed up separately

## Security Considerations

1. Keep all API keys and credentials secure in Replit Secrets
2. Regularly update dependencies for security patches
3. Monitor application logs for suspicious activity

## Support

For additional support:
1. Check the project documentation
2. Review the troubleshooting guide
3. Submit issues through Replit's interface
