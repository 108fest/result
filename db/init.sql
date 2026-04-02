CREATE TABLE users (
    id INT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password TEXT NOT NULL,
    level INT NOT NULL DEFAULT 0,
    kpi INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    token TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE chats (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    user1_id INT,
    user2_id INT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    chat_id INT NOT NULL,
    sender_id INT NOT NULL,
    message_text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE
);




INSERT INTO users (id, username, password, level, kpi)
VALUES (4542, 'gosha.cringer', 'hard_AF_password234123@Fw34$%^&', 0, 10);


INSERT INTO sessions (user_id, token)
VALUES (4542, 'eyJzdWIiOiI0NTQyIiwidXNlcm_BEZUMCI_SASAT_OiJnb3NoYS5jcml');


ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR(255) NOT NULL DEFAULT 'Unknown';
ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(255) NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255) NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS photo_url VARCHAR(500) NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(32) NOT NULL DEFAULT 'junior_dev';
ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_source VARCHAR(32) NOT NULL DEFAULT 'portal';
ALTER TABLE users ADD COLUMN IF NOT EXISTS promotion_requested BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS promotion_requested_at TIMESTAMP NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS break_until TIMESTAMP NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP NOT NULL DEFAULT NOW();

ALTER TABLE sessions ADD COLUMN IF NOT EXISTS session_token VARCHAR(128) NULL;
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP NULL;

CREATE TABLE IF NOT EXISTS admin_settings (
    id INT PRIMARY KEY,
    auto_approve_promotions BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    started_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS news (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    summary TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE sessions ALTER COLUMN token DROP NOT NULL;

-- Create admin user
INSERT INTO users (id, username, password, level, kpi, full_name, role)
VALUES (1, 'admin', 'super_secret_admin_pass', 2, 9999, 'System Admin', 'admin') ON CONFLICT DO NOTHING;

-- Create dummy chats (IDs 1 to 10)
INSERT INTO chats (id, title, user1_id, user2_id) VALUES (1, 'Admin Secret Chat', 1, 1);
INSERT INTO chats (id, title, user1_id, user2_id) VALUES (2, 'Dummy Chat 2', 1, 1);
INSERT INTO chats (id, title, user1_id, user2_id) VALUES (3, 'Dummy Chat 3', 1, 1);
INSERT INTO chats (id, title, user1_id, user2_id) VALUES (4, 'Dummy Chat 4', 1, 1);
INSERT INTO chats (id, title, user1_id, user2_id) VALUES (5, 'Dummy Chat 5', 1, 1);
INSERT INTO chats (id, title, user1_id, user2_id) VALUES (6, 'Dummy Chat 6', 1, 1);
INSERT INTO chats (id, title, user1_id, user2_id) VALUES (7, 'Dummy Chat 7', 1, 1);
INSERT INTO chats (id, title, user1_id, user2_id) VALUES (8, 'Dummy Chat 8', 1, 1);
INSERT INTO chats (id, title, user1_id, user2_id) VALUES (9, 'Dummy Chat 9', 1, 1);
INSERT INTO chats (id, title, user1_id, user2_id) VALUES (10, 'Dummy Chat 10', 1, 1);

-- Reset sequence to start from 11
SELECT setval('chats_id_seq', 10, true);

-- Add secret message
INSERT INTO chat_messages (chat_id, sender_id, message_text) VALUES (1, 1, 'Guys, we are testing new email templates at /api/email_templates/preview. For now, access is restricted via header -> X-Astra-Test-Key: Em41l_s3cr4t_t3mpl4t3s_b3_c4r3f4l. Do not leak this.');
