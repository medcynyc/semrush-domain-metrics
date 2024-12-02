# Heroku Configuration

# Additional API Configuration
- `SEMRUSH_API_DATABASE`: SEMrush database code (default: "us")
- `SEMRUSH_REQUEST_TIMEOUT`: API request timeout in seconds (default: 30)
  
## Required Config Vars

The following configuration variables need to be set in your Heroku application settings:

### Required
- `SEMRUSH_API_KEY`: Your SEMrush API key
- `SEMRUSH_DOMAIN`: Target domain to analyze (e.g., "christinamagdolna.com")
- `DATABASE_URL`: Automatically set by Heroku Postgres addon

### Optional
- `LOG_LEVEL`: Logging level (default: "INFO")
- `BATCH_SIZE`: Number of items to process in batch (default: 1000)
- `MAX_RETRIES`: Maximum retry attempts for failed operations (default: 3)
- `RETRY_DELAY`: Delay between retries in seconds (default: 5)

## Setting Up Config Vars

1. In the Heroku Dashboard:
   - Go to Settings → Config Vars → Reveal Config Vars
   - Add each required variable

2. Via Heroku CLI:
```bash
heroku config:set SEMRUSH_API_KEY=your_api_key
heroku config:set SEMRUSH_DOMAIN=your_domain

