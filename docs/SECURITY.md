# Security & Deployment Guide

This document covers security best practices and deployment configuration for the WoW Guild Analytics application.

## Table of Contents
- [Environment Variables](#environment-variables)
- [Credential Management](#credential-management)
- [Git Security](#git-security)
- [Production Deployment](#production-deployment)
- [Security Checklist](#security-checklist)

---

## Environment Variables

### Configuration File Strategy

The application uses **environment variables** for all sensitive configuration:

- **`config.py`** - Contains NO secrets, only `os.environ.get()` calls
- **`.env`** - Contains actual secrets (NEVER commit this)
- **`.env.example`** - Template without real values (safe to commit)

### Setting Up Environment Variables

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your actual credentials:**
   ```bash
   nano .env  # or use your preferred editor
   ```

3. **Verify `.env` is in `.gitignore`:**
   ```bash
   cat .gitignore | grep "^.env$"
   ```

### Required Environment Variables

**Battle.net API (Required):**
- `BNET_CLIENT_ID` - Your Battle.net OAuth Client ID
- `BNET_CLIENT_SECRET` - Your Battle.net OAuth Client Secret
- `BNET_REGION` - Region code (us, eu, kr, tw, cn)

**Flask (Required):**
- `SECRET_KEY` - Flask secret key for session management
  - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`

**Azure OpenAI (Optional):**
- `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI resource endpoint
- `AZURE_OPENAI_API_KEY` - Your Azure OpenAI API key
- `AZURE_OPENAI_DEPLOYMENT` - Deployment name (default: gpt-4o)
- `AZURE_OPENAI_API_VERSION` - API version (default: 2024-08-01-preview)

### Loading Environment Variables

The application automatically loads environment variables using `python-dotenv`:

```python
from dotenv import load_dotenv
load_dotenv()  # Loads from .env file
```

This happens in `config.py` before the `Config` class is defined.

---

## Credential Management

### DO NOT Commit Secrets

**NEVER commit these to your repository:**
- `.env` file (actual credentials)
- `config.py` with hardcoded values
- Any file containing API keys or passwords
- Database files with user data (`instance/`)
- Log files that might contain sensitive data

### Safe to Commit

**These files are safe to commit:**
- `.env.example` (template with placeholder values)
- `config.py` (uses only `os.environ.get()`)
- `.gitignore` (ensures sensitive files are excluded)
- Documentation files

### Credential Rotation

If credentials are compromised:

1. **Immediately revoke** the compromised credentials at the source:
   - Battle.net: https://develop.battle.net/access/clients
   - Azure: https://portal.azure.com/

2. **Generate new credentials** from the respective platforms

3. **Update your `.env` file** with new values

4. **Restart the application** to load new credentials

5. **If committed to git:**
   ```bash
   # Remove from git history (dangerous - consider repo as compromised)
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch .env' \
     --prune-empty --tag-name-filter cat -- --all
   ```

---

## Git Security

### Verify .gitignore Protection

Before committing, always verify sensitive files are ignored:

```bash
# Check if .env would be committed (should show nothing)
git status --ignored | grep .env

# Check what would be committed
git status

# View what's actually ignored
git check-ignore -v .env
```

### Pre-Commit Checklist

Before every `git commit`:

1. ✅ No hardcoded credentials in code files
2. ✅ `.env` file is NOT staged
3. ✅ `instance/` directory is NOT staged
4. ✅ No `.db` files are staged
5. ✅ No log files are staged
6. ✅ `config.py` only uses `os.environ.get()`

### Emergency: Accidentally Committed Secrets

If you accidentally commit secrets:

1. **DO NOT push to remote** if possible
2. **Rotate credentials immediately** at the source
3. **Remove from git history:**
   ```bash
   git reset HEAD~1  # Undo last commit (if not pushed)
   # OR
   git rebase -i HEAD~3  # Edit last 3 commits
   ```

4. **If already pushed to remote:**
   - Consider the repository **compromised**
   - Rotate ALL credentials immediately
   - Contact repository administrator if needed
   - Consider creating a new repository

---

## Production Deployment

### Environment Configuration

**Development (.env file):**
```bash
FLASK_ENV=development
SECRET_KEY=dev-key-change-in-production
```

**Production (system environment):**
```bash
export FLASK_ENV=production
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
export BNET_CLIENT_ID="your-actual-client-id"
export BNET_CLIENT_SECRET="your-actual-client-secret"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your-actual-api-key"
```

### Production Best Practices

1. **Use strong SECRET_KEY:**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Set environment variables at system level:**
   - Use systemd service files
   - Or cloud provider environment variable settings
   - Do NOT use `.env` files in production

3. **Secure file permissions:**
   ```bash
   chmod 600 .env  # Only owner can read/write
   ```

4. **Use HTTPS in production:**
   - Configure reverse proxy (nginx, Apache)
   - Obtain SSL/TLS certificates (Let's Encrypt)

5. **Change default admin password:**
   - Default: `admin` / `admin123`
   - Change immediately after first login

6. **Enable proper logging:**
   - Configure log rotation
   - Monitor for suspicious activity
   - Don't log sensitive data

### Cloud Deployment Examples

**Azure App Service:**
```bash
az webapp config appsettings set --resource-group myResourceGroup \
  --name myWebApp --settings \
  BNET_CLIENT_ID="xxx" \
  BNET_CLIENT_SECRET="xxx" \
  AZURE_OPENAI_ENDPOINT="xxx" \
  AZURE_OPENAI_API_KEY="xxx"
```

**Heroku:**
```bash
heroku config:set BNET_CLIENT_ID="xxx"
heroku config:set BNET_CLIENT_SECRET="xxx"
heroku config:set AZURE_OPENAI_ENDPOINT="xxx"
heroku config:set AZURE_OPENAI_API_KEY="xxx"
```

**Docker:**
```bash
docker run -e BNET_CLIENT_ID="xxx" \
  -e BNET_CLIENT_SECRET="xxx" \
  -e AZURE_OPENAI_ENDPOINT="xxx" \
  -e AZURE_OPENAI_API_KEY="xxx" \
  your-image
```

---

## Security Checklist

### Before Committing to Git

- [ ] No hardcoded credentials in any files
- [ ] `.env` is in `.gitignore`
- [ ] `instance/` directory is in `.gitignore`
- [ ] `config.py` only uses environment variables
- [ ] `.env.example` has placeholder values only
- [ ] Run `git status` to verify no sensitive files staged

### Before Deploying

- [ ] Generate strong SECRET_KEY for production
- [ ] Configure environment variables at system level
- [ ] Remove or secure `.env` file
- [ ] Change default admin password
- [ ] Enable HTTPS/SSL
- [ ] Configure proper logging
- [ ] Set up database backups
- [ ] Test with Azure OpenAI credentials (if using AI features)

### Regular Maintenance

- [ ] Rotate credentials periodically
- [ ] Review user accounts and permissions
- [ ] Monitor logs for suspicious activity
- [ ] Keep dependencies updated (`pip list --outdated`)
- [ ] Review and update `.gitignore` as needed
- [ ] Audit admin user access

### Incident Response

If credentials are compromised:

1. [ ] Revoke compromised credentials immediately
2. [ ] Generate new credentials
3. [ ] Update configuration
4. [ ] Restart application
5. [ ] Review access logs
6. [ ] Notify affected parties if needed
7. [ ] Document incident

---

## Additional Resources

- [Battle.net API Documentation](https://develop.battle.net/)
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Flask Security](https://flask.palletsprojects.com/en/2.3.x/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)

---

## Questions or Issues?

If you discover a security vulnerability, please:
- Do NOT open a public issue
- Contact the repository maintainer privately
- Allow time for a fix before public disclosure
