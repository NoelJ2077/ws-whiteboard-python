-- 1. Clients
CREATE TABLE IF NOT EXISTS Clients (
    client_id varchar(36) PRIMARY KEY,
    client_email VARCHAR(40),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    isAdmin BOOLEAN DEFAULT 0 -- // START & // END -> (Task 2)
);

-- 2. Whiteboards
CREATE TABLE IF NOT EXISTS Whiteboards (
    wb_id varchar(36) PRIMARY KEY,
    wb_name VARCHAR(100) NOT NULL,
    wb_snapshot JSON, -- aktueller Stand als JSON (Liste von Objekten)
    invite_key VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. M:N Mapping: welche Clients dürfen auf welches Whiteboard. beim erstellen eines boards wird dieses autom. dem Client hinzugefügt. über den key ? können andere clients hinzugefügt werden. 
CREATE TABLE IF NOT EXISTS Client_Whiteboards (
    client_id varchar(36) NOT NULL,
    wb_id varchar(36) NOT NULL,
    PRIMARY KEY (client_id, wb_id),
    FOREIGN KEY (client_id) REFERENCES Clients(client_id) ON DELETE CASCADE,
    FOREIGN KEY (wb_id) REFERENCES Whiteboards(wb_id) ON DELETE CASCADE
);

-- 4. Whiteboard-Aktionen (Log)
CREATE TABLE IF NOT EXISTS Actions_log (
    action_id INT AUTO_INCREMENT PRIMARY KEY,
    wb_id varchar(36) NULL,
    client_id varchar(36) NULL,
    action_type VARCHAR(20) NOT NULL,
    x1 FLOAT,
    y1 FLOAT,
    x2 FLOAT,
    y2 FLOAT,
    color VARCHAR(20),
    thickness INT DEFAULT 1,
    text_content TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (wb_id) REFERENCES Whiteboards(wb_id) ON DELETE SET NULL,
    FOREIGN KEY (client_id) REFERENCES Clients(client_id) ON DELETE SET NULL
);

-- 5. Client-Logging # inkl Chat-log, evtl. irgendwann den Chat-log auslagern. 
CREATE TABLE IF NOT EXISTS Client_log (
    client_id varchar(36) NULL,
    event_type VARCHAR(20) NOT NULL,
    event_data_intern TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES Clients(client_id) ON DELETE SET NULL
);
