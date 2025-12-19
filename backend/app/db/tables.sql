-- 1. Clients
CREATE TABLE IF NOT EXISTS Clients (
    client_id varchar(36) PRIMARY KEY,
    client_email VARCHAR(40),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    isAdmin BOOLEAN DEFAULT 0 -- // START (Task 2) & // END (Task 2)
);

-- 5. Client-Logging # inkl Chat-log, evtl. irgendwann den Chat-log auslagern. 
CREATE TABLE IF NOT EXISTS Client_log (
    client_id varchar(36) NULL,
    event_type VARCHAR(20) NOT NULL,
    event_data_intern TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES Clients(client_id) ON DELETE SET NULL
);
