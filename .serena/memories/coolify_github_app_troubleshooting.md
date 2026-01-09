# Coolify GitHub App Configuration & Troubleshooting

## Problem: "private_key" on null Error

When deployments fail with:
```
Deployment failed: Attempt to read property "private_key" on null
Location: /var/www/html/bootstrap/helpers/github.php:32
```

This means the GitHub App configuration in Coolify is missing or corrupted, specifically the private key.

## Root Cause

Coolify uses a GitHub App to authenticate and access repositories. The private key is required for this authentication. Common causes:
- GitHub App was deleted or revoked
- GitHub App lost permissions to repository
- Private key file corrupted in Coolify database
- GitHub App not properly configured during initial setup

## Solution: Reconfigure GitHub App

### Quick Navigation

1. **GitHub Side**: Create/configure GitHub App with proper permissions
2. **Coolify Side**: Add GitHub App source with all required credentials
3. **Application Side**: Update application to use new GitHub App source
4. **Test**: Redeploy and verify

### Critical Fields Required

| Field | Where to Find | Notes |
|-------|---------------|-------|
| App ID | GitHub App settings page | Shown at top |
| Client ID | GitHub App settings → About | Copy from form |
| Client Secret | GitHub App settings → Generate | Save immediately |
| Installation ID | URL after installing app | e.g., `/installations/12345678` |
| Private Key | Generate in GitHub App settings | Download .pem file |
| Webhook Secret | You create this | Use `openssl rand -hex 32` |

### GitHub App Permissions Needed

**Repository Permissions:**
- Contents: Read
- Metadata: Read
- Pull Requests: Read & Write (optional, for PR deployments)

**Account Permissions:**
- Email addresses: Read

**Subscribe to Events:**
- Push (required)
- Pull request (optional)

### Coolify Configuration URLs

Replace `your-coolify-url` with your actual Coolify URL (e.g., `http://localhost` or `https://coolify.yourdomain.com`):

- **Homepage URL**: `http://your-coolify-url`
- **Webhook URL**: `http://your-coolify-url/webhooks/source/github/events`
- **Setup URL**: `http://your-coolify-url/webhooks/source/github/install?source=<source_uuid>`

### Step-by-Step Process

#### 1. Create GitHub App

Go to: https://github.com/settings/apps (personal) or https://github.com/organizations/ORG/settings/apps

- Create new GitHub App
- Set permissions (see table above)
- Generate private key (download .pem)
- Generate client secret (save it)
- Install app to account/org
- Copy Installation ID from URL

#### 2. Add to Coolify

In Coolify:
- Sources → + Add → GitHub App → Manual Installation
- First, add private key in Keys & Tokens
- Then fill all GitHub App details
- Save and click "Sync Name" to verify

#### 3. Update Application

In your application:
- Go to Source/General tab
- Select new GitHub App from dropdown
- Verify repository path
- Save

#### 4. Test

- Click Deploy/Redeploy
- Watch logs for successful git clone
- No more private_key errors

## Local Coolify Webhook Issue

**Important**: If running Coolify locally (e.g., `http://localhost`), GitHub webhooks won't reach it. Solutions:
- Use ngrok to expose local Coolify
- Deploy Coolify to public server
- Use "Public Repository" method instead (for public repos only)

## Verification Commands

Check GitHub App installation access:
```
https://github.com/settings/installations
```

Check Coolify logs:
```bash
docker logs coolify
```

## Alternative: Public Repository Method

For public repos only, bypass GitHub App:
1. Application settings → Change to "Public Repository"
2. Enter: `https://github.com/username/repo`
3. Select branch
4. Save and redeploy

**Limitation**: No automatic deployments, no PR previews, no private repo access.

## Related Memories

- `coolify_deployment_architecture` - Container structure and file paths
- `website_upload_deployment` - Full deployment workflow
- `website_article_workflow` - Article deployment process

## References

- [Coolify GitHub App Manual Setup](https://coolify.io/docs/applications/ci-cd/github/manually-setup-github-app)
- [Move Between GitHub Apps](http://coolify.io/docs/applications/ci-cd/github/move-between-github-apps)
- [Coolify Troubleshooting](https://coolify.io/docs/troubleshoot/overview)
