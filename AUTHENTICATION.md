### Authentication System Implementation

## Overview
The WoW Guild Analytics application now includes a comprehensive authentication system with user management. This ensures that only authorized users can sync guilds and manage character data.

## Features

### User Authentication
- **Login/Logout**: Secure session-based authentication
- **Password Hashing**: Passwords are hashed using Werkzeug's secure methods
- **Remember Me**: Option to stay logged in across sessions
- **Session Management**: Automatic session handling via Flask-Login

### Authorization
- **Protected Routes**: Guild sync and character sync require login
- **Admin-Only Access**: User management restricted to administrators
- **Role-Based Access**: Two roles - User and Administrator

### User Management (Admin Only)
- **Create Users**: Add new users with username, email, and password
- **Edit Users**: Update user details, change passwords, toggle admin status
- **Delete Users**: Remove users from the system
- **Activate/Deactivate**: Disable user accounts without deletion
- **Self-Protection**: Admins cannot delete or deactivate themselves

## Installation

### 1. Install Dependencies

```bash
pip install Flask-Login==0.6.3 Werkzeug==3.0.1
```

Or install from requirements.txt:

```bash
pip install -r requirements.txt
```

### 2. Run Migration

Create the User table and default admin account:

```bash
python migrate_add_users.py
```

This will create a default admin user:
- **Username**: `admin`
- **Password**: `admin123`

⚠️ **IMPORTANT**: Change this password immediately after first login!

## Usage

### For End Users

#### Logging In
1. Navigate to the application homepage
2. Click "Login" in the navigation bar
3. Enter your username and password
4. Optionally check "Remember me" to stay logged in
5. Click "Login"

#### Syncing Guilds (Requires Login)
1. Log in to your account
2. Click "Sync Guild" in the navigation
3. Enter realm and guild name
4. Click "Sync Guild"

#### Syncing Character Details (Requires Login)
1. Log in to your account
2. Navigate to a guild detail page
3. Click "Sync Character Details" button
4. Confirm the action

#### Logging Out
- Click "Logout" in the navigation bar

### For Administrators

#### Accessing Admin Panel
1. Log in with an admin account
2. Click "Admin" in the navigation bar
3. View the User Management dashboard

#### Creating a New User
1. Go to Admin Dashboard
2. Click "Add User" button
3. Fill in the form:
   - Username (required, unique)
   - Email (required, unique)
   - Password (required, min 6 characters)
   - Confirm Password (must match)
   - Check "Administrator" if user should be admin
4. Click "Create User"

#### Editing a User
1. Go to Admin Dashboard
2. Click the pencil icon next to a user
3. Update fields as needed:
   - Username
   - Email
   - Password (leave blank to keep current)
   - Admin status
   - Active status
4. Click "Save Changes"

**Note**: You cannot remove your own admin privileges or deactivate your own account.

#### Deactivating a User
1. Go to Admin Dashboard
2. Click the pause icon next to a user
3. User account will be deactivated (can be reactivated later)

#### Deleting a User
1. Go to Admin Dashboard
2. Click the trash icon next to a user
3. Confirm deletion
4. User will be permanently removed

**Note**: You cannot delete your own account.

## Security Features

### Password Security
- Passwords are hashed using `werkzeug.security.generate_password_hash`
- Minimum password length: 6 characters
- Passwords never stored in plain text

### Session Security
- Flask-Login manages secure sessions
- Session cookies are HTTP-only
- Optional "remember me" functionality
- Automatic logout on session expiry

### Authorization Checks
- `@login_required`: Decorator for protected routes
- `@admin_required`: Custom decorator for admin-only routes
- Role checks in templates to hide unauthorized actions

### Protection Against Common Attacks
- CSRF protection via Flask's built-in security
- SQL injection protection via SQLAlchemy ORM
- Password hashing prevents rainbow table attacks
- No password length shown in UI

## Database Schema

### User Model
```python
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
```

### Fields
- **id**: Primary key
- **username**: Unique login name (indexed)
- **email**: Unique email address (indexed)
- **password_hash**: Hashed password (never store plain text)
- **is_admin**: Admin privileges flag
- **is_active**: Account activation status
- **created_at**: Account creation timestamp
- **last_login**: Last successful login timestamp

## File Structure

```
app/
├── __init__.py          # Flask-Login initialization
├── models.py            # User model
├── auth.py              # Authentication routes (login, logout)
├── admin.py             # Admin routes (user management)
├── routes.py            # Main routes (with @login_required decorators)
├── templates/
│   ├── auth/
│   │   └── login.html   # Login page
│   └── admin/
│       ├── index.html   # Admin dashboard
│       ├── add_user.html   # Add user form
│       └── edit_user.html  # Edit user form
└── static/
    └── css/
        └── style.css    # Dark theme styles
```

## Protected Routes

### Requires Login
- `/sync` (GET, POST) - Sync guild roster
- `/guild/<id>/sync-characters` (POST) - Sync character details

### Requires Admin
- `/admin` - Admin dashboard
- `/admin/users/add` - Add user
- `/admin/users/<id>/edit` - Edit user
- `/admin/users/<id>/delete` - Delete user
- `/admin/users/<id>/toggle-status` - Toggle user status

### Public Routes
- `/` - Home page (view guilds)
- `/guild/<id>` - Guild detail page (view analytics)
- `/auth/login` - Login page
- `/auth/logout` - Logout action
- `/api/*` - API endpoints (currently public)

## Configuration

### Environment Variables

No additional environment variables needed. The existing `SECRET_KEY` in `config.py` is used for session management.

### Default Values
- SECRET_KEY: 'dev-secret-key-change-in-production'

⚠️ **Production**: Set a secure `SECRET_KEY` environment variable in production!

## Best Practices

### For Administrators

1. **Change Default Password**: Immediately change the default admin password
2. **Create Individual Accounts**: Don't share the admin account
3. **Use Strong Passwords**: Enforce minimum 8+ character passwords
4. **Regular Audits**: Review user list regularly
5. **Deactivate, Don't Delete**: Deactivate users instead of deleting when possible
6. **Principle of Least Privilege**: Only make users admins when necessary

### For Users

1. **Secure Passwords**: Use unique, strong passwords
2. **Log Out**: Always log out on shared computers
3. **Report Issues**: Notify admins of any suspicious activity

## Troubleshooting

### Cannot Log In
- **Check Credentials**: Verify username and password are correct
- **Account Status**: Ensure account is active (contact admin)
- **Clear Cache**: Try clearing browser cache/cookies

### "User not found" Error
- Account may not exist - contact administrator
- Username is case-sensitive

### "Account deactivated" Message
- Account has been disabled - contact administrator

### Cannot Access Admin Panel
- Only administrators can access admin features
- Verify your account has admin privileges

### Migration Fails
- Ensure database is accessible
- Check for any existing schema conflicts
- Delete `guild_data.db` and run migration again (WARNING: deletes all data)

## Future Enhancements

Potential improvements:
- Password reset functionality
- Email verification
- Two-factor authentication (2FA)
- User activity logging
- Password expiration policies
- Role-based permissions (beyond admin/user)
- API key authentication for API endpoints
- OAuth2 integration (Google, Microsoft, etc.)
- User profile pages
- Password strength indicator
- Account lockout after failed attempts
- Session timeout configuration

## API Considerations

Currently, API endpoints (`/api/*`) are public. Consider:
- Adding API key authentication
- Rate limiting
- Token-based authentication (JWT)
- Separate API user management

## Security Checklist

- [x] Passwords are hashed
- [x] Protected routes use @login_required
- [x] Admin routes use @admin_required
- [x] Users cannot delete themselves
- [x] Users cannot remove their own admin status
- [x] Inactive users cannot log in
- [x] Last login timestamp tracked
- [x] Session management via Flask-Login
- [x] CSRF protection enabled
- [ ] Rate limiting (future)
- [ ] API authentication (future)
- [ ] Password reset (future)
- [ ] 2FA (future)

## Support

For questions or issues:
1. Check this documentation
2. Review error messages in logs
3. Contact system administrator
4. Check application logs in `logs/app.log`
