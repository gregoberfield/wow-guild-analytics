# Authentication System - Quick Start Guide

## What Changed

The WoW Guild Analytics application now requires **user authentication** for protected actions:

### Protected Actions (Login Required)
- ✅ Syncing guilds
- ✅ Syncing character details

### Public Actions (No Login Required)
- ✅ Viewing guild list
- ✅ Viewing guild analytics
- ✅ Viewing character rosters
- ✅ Accessing API endpoints

## Quick Setup

### 1. Install New Dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Migration
```bash
python migrate_add_users.py
```

### 3. Login with Default Admin
- **URL**: http://localhost:5000
- **Username**: `admin`
- **Password**: `admin123`

### 4. Change Admin Password (IMPORTANT!)
1. Login as admin
2. Click "Admin" in navigation
3. Click pencil icon next to admin user
4. Enter new password twice
5. Click "Save Changes"

## User Management (Admin Only)

### Create New User
1. Admin → Add User
2. Fill in username, email, password
3. Check "Administrator" if needed
4. Click "Create User"

### Edit User
1. Admin → Click pencil icon
2. Update fields (leave password blank to keep current)
3. Click "Save Changes"

### Deactivate User
1. Admin → Click pause icon
2. User cannot login (can be reactivated)

### Delete User
1. Admin → Click trash icon
2. Confirm deletion
3. User permanently removed

## User Roles

### Administrator
- Can sync guilds
- Can sync character details
- Can manage all users
- Can access admin panel

### Regular User
- Can sync guilds
- Can sync character details
- Cannot manage users
- Cannot access admin panel

## Navigation Changes

### When Logged Out
- Home
- Login

### When Logged In (Regular User)
- Home
- Sync Guild
- Logout (username)

### When Logged In (Admin)
- Home
- Sync Guild
- **Admin** (new!)
- Logout (username)

## Security Features

✅ Password hashing (Werkzeug)
✅ Session management (Flask-Login)
✅ Protected routes (@login_required)
✅ Admin-only routes (@admin_required)
✅ Remember me functionality
✅ Last login tracking
✅ Account activation/deactivation
✅ Self-protection (can't delete/deactivate yourself)

## Files Added

```
app/auth.py                          # Login/logout routes
app/admin.py                         # User management routes
app/templates/auth/login.html        # Login page
app/templates/admin/index.html       # Admin dashboard
app/templates/admin/add_user.html    # Add user form
app/templates/admin/edit_user.html   # Edit user form
migrate_add_users.py                 # Migration script
AUTHENTICATION.md                    # Full documentation
```

## Files Modified

```
requirements.txt          # Added Flask-Login, Werkzeug
app/__init__.py          # Added Flask-Login initialization
app/models.py            # Added User model
app/routes.py            # Added @login_required decorators
app/templates/base.html  # Updated navigation with login/admin links
app/templates/guild_detail.html  # Hide sync button when not logged in
```

## Troubleshooting

### Can't Login
- Verify username/password
- Check account is active
- Clear browser cache

### Can't Access Sync Guild
- Must be logged in
- Click "Login" in navigation

### Can't Access Admin Panel
- Must be logged in
- Must have admin privileges
- Contact admin to grant access

### Migration Failed
- Check database file permissions
- Ensure no Flask app is running
- Try deleting guild_data.db (⚠️ deletes all data)

## Important Notes

⚠️ **Change default password** - The default admin password is public knowledge!

⚠️ **Backup database** - Before making changes, backup `instance/guild_data.db`

⚠️ **Production SECRET_KEY** - Set a secure SECRET_KEY environment variable in production

✅ **API still public** - API endpoints don't require authentication (consider adding in future)

## Next Steps

1. ✅ Login with admin credentials
2. ✅ Change admin password
3. ✅ Create user accounts for your team
4. ✅ Test syncing guilds
5. ✅ Review admin panel features

## Full Documentation

For complete details, see [AUTHENTICATION.md](AUTHENTICATION.md)
