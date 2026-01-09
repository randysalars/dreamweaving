# Coolify GitHub App Setup and Troubleshooting Guide

## Overview

This guide covers how to set up or reconfigure a GitHub App integration in Coolify, specifically for fixing the `private_key null` error that prevents deployments.

## Common Error

```
Deployment failed: Attempt to read property "private_key" on null
Location: /var/www/html/bootstrap/helpers/github.php:32
```

This error means the GitHub App configuration in Coolify is missing or corrupted, specifically the private key.

---

## Step-by-Step Setup Guide

### Phase 1: Check Current GitHub App Status

1. **Open your Coolify dashboard** (e.g., `http://localhost` or your Coolify server URL)

2. **Go to Sources** (find it in the left sidebar)

3. **Check your existing GitHub App**:
   - Look for your GitHub source/app in the list
   - Click on it to see its details
   - Note if the private key is missing or shows an error

### Phase 2: Set Up New GitHub App on GitHub

1. **Go to GitHub** and navigate to:
   - **Personal account**: https://github.com/settings/apps
   - **Organization**: https://github.com/organizations/YOUR_ORG/settings/apps

2. **Click "New GitHub App"** (or you can try to fix the existing one)

3. **Configure the GitHub App**:
   - **GitHub App name**: Choose something like "Coolify-Salars" or "Coolify-Local"
   - **Homepage URL**: `http://your-coolify-url` (e.g., `http://localhost`)
   - **Callback URL**: `http://your-coolify-url`
   - **Setup URL**: We'll add this after creating the Coolify source (see Phase 3)

4. **Enable Webhook**:
   - ✅ Check "Active"
   - **Webhook URL**: `http://your-coolify-url/webhooks/source/github/events`
   - **Webhook secret**: Generate a random string (save this for later)
     ```bash
     # Generate a secure webhook secret:
     openssl rand -hex 32
     ```

5. **Set Repository Permissions**:
   - **Contents**: Read access
   - **Metadata**: Read access
   - **Pull requests**: Read & write (optional, for PR deployments)

6. **Set Account Permissions**:
   - **Email addresses**: Read access

7. **Subscribe to Events**:
   - ✅ Push
   - ✅ Pull request (optional)

8. **Click "Create GitHub App"**

9. **Generate Private Key**:
   - After creation, scroll down to "Private keys"
   - Click "Generate a private key"
   - **Save the downloaded `.pem` file** - you'll need this content

10. **Note down these values** (you'll need them for Coolify):
    - **App ID** (shown at the top)
    - **Client ID** (in the "About" section)
    - Click "Generate a new client secret" and save the **Client Secret**

11. **Install the GitHub App**:
    - Click "Install App" in the left sidebar
    - Choose your account/organization
    - Select "All repositories" or "Only select repositories" (include your repos)
    - Click "Install"
    - **Copy the Installation ID from the URL** (it's the number after `/settings/installations/`)
      - Example: `https://github.com/settings/installations/12345678` → Installation ID is `12345678`

### Phase 3: Add GitHub App to Coolify

1. **In Coolify, go to Sources** (left sidebar)

2. **Click the "+ Add" button**

3. **Click "GitHub App"**

4. **Choose "Manual Installation"**

5. **First, add the Private Key**:
   - Before filling the form, go to **Keys & Tokens** (in Coolify sidebar)
   - Click "+ Add"
   - Give it a name like "GitHub App Private Key"
   - Open the `.pem` file you downloaded and **paste the entire contents** (including `-----BEGIN RSA PRIVATE KEY-----` and `-----END RSA PRIVATE KEY-----`)
   - Save

6. **Go back to Sources → Add GitHub App → Manual Installation**

7. **Fill in all the fields**:
   - **Name**: Something like "GitHub - Personal" or "GitHub - MyOrg"
   - **Organization** (optional): Leave blank for personal account
   - **GitHub App Name**: The name you chose on GitHub
   - **App ID**: From GitHub
   - **Installation ID**: From the URL after installing
   - **Client ID**: From GitHub
   - **Client Secret**: From GitHub (the one you generated)
   - **Webhook Secret**: The secret you created earlier
   - **Private Key**: Select the key you just added

8. **Save**

9. **Copy the Source UUID** (you'll see it in the URL or the source details)
   - Example: `yc80os80o0wkog4kcw8ww0ow`

10. **Go back to GitHub** → Your App → General settings:
    - Update **Setup URL** to: `http://your-coolify-url/webhooks/source/github/install?source=YOUR_SOURCE_UUID`
    - Save changes

11. **Back in Coolify**, click **"Sync Name"** button on your source to verify it's working
    - If successful, you'll see a confirmation message

### Phase 4: Update Your Application

1. **Go to your application** (e.g., `randysalars/salars:main`)

2. **Click the "General" or "Source" tab** (look for Git/GitHub settings)

3. **Find "Git Source" section**

4. **Select your new GitHub App** from the dropdown

5. **Verify the repository path** is correct (e.g., `yourusername/salarsu`)

6. **Save changes**

### Phase 5: Test Deployment

1. **Click "Deploy" or "Redeploy"**

2. **Watch the logs** - you should now see:
   - Git clone starting successfully
   - Build process beginning
   - No more `private_key null` errors

---

## Quick Troubleshooting

### Deployment Still Failing?

| Issue | Solution |
|-------|----------|
| **Webhook errors** | If running Coolify locally, GitHub can't reach it. Consider using ngrok or make sure Coolify is publicly accessible |
| **Private key invalid** | Ensure the entire PEM file content was copied including `-----BEGIN RSA PRIVATE KEY-----` and `-----END RSA PRIVATE KEY-----` headers |
| **Installation ID wrong** | Double-check you copied the Installation ID from the URL after installing the GitHub App |
| **"Sync Name" fails** | Verify all fields (App ID, Client ID, Client Secret, Installation ID) are correct |
| **Permission denied** | Check that the GitHub App has access to your repository in GitHub's installation settings |

### Verify GitHub App Access

Go to: `https://github.com/organizations/<organization>/settings/installations`
(or `https://github.com/settings/installations` for personal account)

- Check that your Coolify GitHub App is installed
- Verify it has access to the repositories you're trying to deploy

### Check Coolify Logs

If deployment fails, check the Coolify application logs for more details:

```bash
# If running Coolify in Docker:
docker logs coolify

# Or check specific container logs
docker ps | grep coolify
docker logs <container-id>
```

---

## Alternative: Use Public Repository (Quick Workaround)

If your repository is public and you want to bypass GitHub App authentication temporarily:

1. **Go to your application settings in Coolify**
2. **Change Git Source Type** from "GitHub App" to "Public Repository"
3. **Enter the repository URL directly**: `https://github.com/yourusername/repo`
4. **Select the branch**: `main`
5. **Save and Redeploy**

**Note:** This won't work for private repositories and you'll lose features like automatic commit deployments and PR previews.

---

## Requirements

- **Coolify version**: v4.0.0-beta.408 or higher (for switching between GitHub Apps)
- **GitHub permissions**: Ability to create GitHub Apps in your account/organization
- **Network access**: Coolify must be accessible to receive webhooks from GitHub (for local setups, consider ngrok)

---

## References

- [Manually Setup GitHub App | Coolify Docs](https://coolify.io/docs/applications/ci-cd/github/manually-setup-github-app)
- [Move Between GitHub Apps | Coolify Docs](http://coolify.io/docs/applications/ci-cd/github/move-between-github-apps)
- [GitHub Integration - Coolify Docs](https://coolify.io/docs/applications/ci-cd/github/integration)
- [Setup GitHub App | Coolify Docs](https://next.coolify.io/docs/applications/ci-cd/github/setup-app)
- [CI/CD with Git Providers | Coolify Docs](https://coolify.io/docs/applications/ci-cd/introduction)

---

## Related Documentation

See also:
- `coolify_deployment_architecture` (Serena memory) - Deployment structure and container paths
- `website_upload_deployment` (Serena memory) - Full website deployment workflow
