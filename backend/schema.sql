-- Gliders table
CREATE TABLE IF NOT EXISTS gliders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active'
);

-- Reservations table
CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    glider TEXT NOT NULL,
    time TEXT NOT NULL,
    name TEXT NOT NULL
);
