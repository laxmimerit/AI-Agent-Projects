# MCP Servers Setup Guide

Complete setup guide for integrating Airbnb, Google Calendar, Google Sheets, and Gmail MCP servers with AI applications using OAuth authentication.

---

## Prerequisites Installation

### 1. Install Node.js and npm

**Windows:**
1. Download Node.js LTS from [nodejs.org](https://nodejs.org/)
2. Run the installer (includes npm)
3. Verify installation:
   ```bash
   node --version
   npm --version
   ```

**macOS:**
```bash
# Using Homebrew
brew install node

# Verify
node --version
npm --version
```

**Linux:**
```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify
node --version
npm --version
```

### 2. Install uv (Python Package Manager)

`uvx` is part of `uv`, a fast Python package installer and resolver. Install it if you haven't already:

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Alternative (using pip):**
```bash
pip install uv
```

**Verify installation:**
```bash
uv --version
uvx --version
```

---

## Google Cloud Setup

This is a **one-time setup** for all Google services (Calendar, Sheets, Gmail).

### Step 1: Create Google Cloud Project (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown (top left)
3. Click **New Project**
4. Enter project name: "AI Agent MCP Integration"
5. Click **Create**
6. Wait for project creation and select it

### Step 2: Enable Required APIs

You need to enable APIs for each Google service:

1. In Google Cloud Console, go to **APIs & Services > Library**
2. Search and enable each of these APIs:
   - **Google Calendar API**
   - **Google Sheets API**
   - **Google Drive**
   - **Gmail API**

For each API:
- Click on the API name
- Click **Enable**
- Wait for confirmation

### Step 3: Create OAuth 2.0 Credentials

#### Configure OAuth Consent Screen (First Time Only)

1. Go to **APIs & Services > OAuth consent screen**
2. Select **External** user type
3. Click **Create**
4. Fill in required information:
   - **App name:** Claude MCP Integration
   - **User support email:** Your email address
   - **Developer contact email:** Your email address
5. Click **Save and Continue**

#### Add Test Users

1. In **Test users** section, click **Add Users**
2. Enter your Google email address (the one you'll use with Claude)
3. Click **Add**
4. Click **Save and Continue**

#### Create OAuth Client ID

1. Go to **APIs & Services > Credentials**
2. Click **Create Credentials > OAuth client ID**
3. Select **Application type:** Desktop app
4. **Name:** AI Agent App
5. Click **Create**
6. Click **Download JSON** (download icon) on the created credential
7. Click **OK** to close the dialog

### Step 4: Save Credentials File

**Windows:**
1. Create directory:
   ```powershell
   mkdir ~/.gmail-mcp
   ```
2. Rename downloaded JSON to `gcp-oauth.keys.json`
3. Move to: `~/.gmail-mcp/gcp-oauth.keys.json`

**macOS/Linux:**
1. Create directory:
   ```bash
   mkdir -p ~/.gmail-mcp
   ```
2. Rename downloaded JSON to `gcp-oauth.keys.json`
3. Move to: `~/.gmail-mcp/gcp-oauth.keys.json`

---

## First-Time Authentication

After configuring and restarting your AI application, you need to authenticate each Google service. The authentication process opens a browser window where you'll grant permissions.

### Google Calendar Authentication

**Windows:**
```powershell
# Set environment variable (use your actual file path)
#CMD
set GOOGLE_OAUTH_CREDENTIALS="C:\\Users\\laxmi\\.gmail-mcp\\gcp-oauth.keys.json"
#Powershell
$env:GOOGLE_OAUTH_CREDENTIALS="C:\\Users\\laxmi\\.gmail-mcp\\gcp-oauth.keys.json"


# Run authentication
npx @cocal/google-calendar-mcp auth
```

**macOS/Linux:**
```bash
# Set environment variable (use your actual file path)
export GOOGLE_OAUTH_CREDENTIALS="C:\\Users\\laxmi\\.gmail-mcp\\gcp-oauth.keys.json"

# Run authentication
npx @cocal/google-calendar-mcp auth
```

**What happens:**
1. Browser window opens automatically
2. Sign in with your Google account (the test user you added)
3. Review permissions and click **Allow**
4. You may see "Google hasn't verified this app" - click **Continue**
5. Browser shows "Authentication successful"
6. Close browser tab - you're done!

### Google Sheets Authentication

Google Sheets authentication happens automatically when you first use it in your AI application.

**First time usage:**
1. In your AI application, ask: **"List my spreadsheets"**
2. Browser opens for OAuth authentication
3. **Sign in** with your Google account
4. Click **Allow** to grant Sheets permissions
5. Token automatically saved
6. Close browser tab and return to your AI app

### Gmail Authentication

**Windows:**
```powershell
# Create directory if it doesn't exist
mkdir ~/.gmail-mcp

# Move your gcp-oauth.keys.json to this folder
# Then run authentication
npx @gongrzhe/server-gmail-autoauth-mcp auth
```

**macOS/Linux:**
```bash
# Create directory if it doesn't exist
mkdir -p ~/.gmail-mcp

# Move your gcp-oauth.keys.json to this folder
mv gcp-oauth.keys.json ~/.gmail-mcp/

# Run authentication
npx @gongrzhe/server-gmail-autoauth-mcp auth
```

**What happens:**
1. Opens browser for Gmail OAuth
2. **Sign in** with your Google account
3. Click **Allow** to grant Gmail permissions
4. Credentials saved to `~/.gmail-mcp/credentials.json`
5. Close browser tab - authentication complete!

### Airbnb (No Authentication Required)

Airbnb MCP works immediately without authentication for public listing searches.

---

### Token Refresh

- Tokens automatically refresh when expired
- If issues persist, delete token files and re-authenticate
- **Test mode tokens expire after 7 days** - you'll need to re-authenticate weekly unless you publish your app

---

## Resources

- [Google Cloud Console](https://console.cloud.google.com/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Node.js Downloads](https://nodejs.org/)
- [uv Documentation](https://github.com/astral-sh/uv)

### GitHub Repositories

- [Airbnb MCP Server](https://github.com/openbnb-org/mcp-server-airbnb)
- [Google Calendar MCP](https://github.com/nspady/google-calendar-mcp)
- [Google Sheets MCP](https://github.com/xing5/mcp-google-sheets)
- [Gmail MCP Server](https://github.com/GongRzhe/Gmail-MCP-Server)

---
