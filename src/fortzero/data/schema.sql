PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS profiles (
    alias TEXT PRIMARY KEY,
    preferred_mode TEXT NOT NULL,
    created_at TEXT NOT NULL,
    last_opened_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_alias TEXT NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    active INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (profile_alias) REFERENCES profiles(alias) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS campaign_state (
    profile_alias TEXT NOT NULL,
    campaign_id TEXT NOT NULL,
    state_json TEXT NOT NULL DEFAULT '{}',
    updated_at TEXT NOT NULL,
    PRIMARY KEY (profile_alias, campaign_id),
    FOREIGN KEY (profile_alias) REFERENCES profiles(alias) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS world_state (
    profile_alias TEXT PRIMARY KEY,
    state_json TEXT NOT NULL DEFAULT '{}',
    updated_at TEXT NOT NULL,
    FOREIGN KEY (profile_alias) REFERENCES profiles(alias) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_alias TEXT NOT NULL,
    mission_id TEXT NOT NULL,
    report_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (profile_alias) REFERENCES profiles(alias) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS event_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    source TEXT NOT NULL,
    mission_id TEXT,
    profile_alias TEXT,
    session_id INTEGER,
    payload_json TEXT NOT NULL
);
