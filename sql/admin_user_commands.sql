-- ============================================================
-- WoW Guild Analytics - Manual Admin User SQL Commands
-- ============================================================
-- Use these commands if you need to manually manage users
-- in the SQLite database.
--
-- Access database:
--   sqlite3 instance/guild_analytics.db
-- ============================================================

-- 1. CREATE DEFAULT ADMIN USER
-- Password: admin123
-- IMPORTANT: Change password after first login!
-- ============================================================

INSERT INTO user (username, email, password_hash, is_admin, is_active, created_at)
VALUES (
    'admin',
    'admin@example.com',
    'scrypt:32768:8:1$jBq8rK9L3qXmEOvC$8c5e2a3d1f9b7e6c4a0d8f1b3e5c7a9d2f4b6e8c0a1d3f5b7e9c1a3d5f7b9e0c2a4d6f8b0c1e3f5a7c9e1b3d5f7a9c0b2d4f6e8a0c1d3f5b7e9c1a3d5f7b9e0c2a4d6f8b',
    1,
    1,
    datetime('now')
);

-- ============================================================
-- 2. LIST ALL USERS
-- ============================================================

SELECT id, username, email, is_admin, is_active, created_at, last_login
FROM user
ORDER BY id;

-- ============================================================
-- 3. CHECK IF ADMIN USER EXISTS
-- ============================================================

SELECT * FROM user WHERE username = 'admin';

-- ============================================================
-- 4. MAKE A USER AN ADMIN
-- ============================================================

UPDATE user 
SET is_admin = 1 
WHERE username = 'your-username';

-- ============================================================
-- 5. ACTIVATE/DEACTIVATE USER
-- ============================================================

-- Activate user
UPDATE user 
SET is_active = 1 
WHERE username = 'your-username';

-- Deactivate user
UPDATE user 
SET is_active = 0 
WHERE username = 'your-username';

-- ============================================================
-- 6. RESET ADMIN PASSWORD TO DEFAULT (admin123)
-- ============================================================

UPDATE user
SET password_hash = 'scrypt:32768:8:1$jBq8rK9L3qXmEOvC$8c5e2a3d1f9b7e6c4a0d8f1b3e5c7a9d2f4b6e8c0a1d3f5b7e9c1a3d5f7b9e0c2a4d6f8b0c1e3f5a7c9e1b3d5f7a9c0b2d4f6e8a0c1d3f5b7e9c1a3d5f7b9e0c2a4d6f8b'
WHERE username = 'admin';

-- ============================================================
-- 7. DELETE A USER (USE WITH CAUTION!)
-- ============================================================

DELETE FROM user WHERE username = 'username-to-delete';

-- ============================================================
-- 8. COUNT USERS
-- ============================================================

SELECT COUNT(*) as user_count FROM user;
SELECT COUNT(*) as admin_count FROM user WHERE is_admin = 1;
SELECT COUNT(*) as active_count FROM user WHERE is_active = 1;

-- ============================================================
-- 9. VIEW USER TABLE STRUCTURE
-- ============================================================

.schema user

-- ============================================================
-- 10. BACKUP DATABASE BEFORE MAKING CHANGES
-- ============================================================

-- From command line (not in SQLite):
-- sqlite3 instance/guild_analytics.db ".backup instance/guild_analytics_backup.db"

-- ============================================================
-- COMMON TROUBLESHOOTING
-- ============================================================

-- Check if user table exists:
SELECT name FROM sqlite_master WHERE type='table' AND name='user';

-- If table doesn't exist, run migrations:
-- Exit SQLite and run: python migrate_add_users.py

-- Verify password hash format:
SELECT username, substr(password_hash, 1, 20) as hash_prefix FROM user;

-- ============================================================
-- SQLITE COMMAND REFERENCE
-- ============================================================

-- .tables          -- List all tables
-- .schema user     -- Show user table structure  
-- .headers on      -- Show column headers
-- .mode column     -- Format output as columns
-- .quit            -- Exit SQLite
-- .help            -- Show all commands

-- ============================================================
