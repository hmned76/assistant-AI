-- Migration initiale : tables users, contacts, events (rendez‑vous)

-- Création de la table users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    language_preference VARCHAR(50) DEFAULT 'fr',   -- 'fr' ou 'tn'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Création de la table contacts
CREATE TABLE contacts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),               -- format international, nullable
    relation VARCHAR(50),            -- frère, sœur, médecin, etc.
    is_private BOOLEAN DEFAULT FALSE -- vrai si l'utilisateur veut garder secrètes ces infos
);

-- Création de la table events (rendez‑vous)
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    is_private BOOLEAN DEFAULT FALSE,
    contact_id INTEGER REFERENCES contacts(id) ON DELETE SET NULL,
    notes TEXT
);

-- Index utiles
CREATE INDEX idx_events_user_id ON events(user_id);
CREATE INDEX idx_events_start ON events(start_time);
CREATE INDEX idx_contacts_user_id ON contacts(user_id);