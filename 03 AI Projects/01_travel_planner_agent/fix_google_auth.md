# Fix Google Calendar Authentication

## Problem
The Google Calendar MCP authentication tokens have expired.

Error: `Authentication tokens are no longer valid. Please restart the server to re-authenticate.`

## Solution

### Option 1: Delete and Re-authenticate (Recommended)

1. **Delete the existing token file:**
   ```bash
   del "C:\Users\laxmi\.gmail-mcp\token.json"
   ```

2. **Run the script again** - it will trigger OAuth re-authentication:
   ```bash
   python "D:\Courses\Udemy\AI Agent Projects\03 AI Projects\01_travel_planner_agent\travel_planner_agent.py"
   ```

3. A browser window should open asking you to authenticate with Google
4. Grant the necessary permissions
5. The new token will be saved automatically

### Option 2: Use Claude Desktop MCP (If you have it set up)

If you have Google Calendar MCP working in Claude Desktop:
1. Copy the token.json from Claude Desktop's location
2. Replace it in `C:\Users\laxmi\.gmail-mcp\token.json`

### Option 3: Re-run Google OAuth Setup

If deletion doesn't trigger re-auth, you may need to:
1. Check your `gcp-oauth.keys.json` file exists and is valid
2. Make sure the OAuth credentials include the Calendar API scope
3. Run a standalone Google Calendar authentication script first

## After Authentication Works

Once authentication is successful, you should see the event being added to Google Calendar without errors.
