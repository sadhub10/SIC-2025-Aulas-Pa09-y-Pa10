CREATE DATABASE IF NOT EXISTS novamind
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE novamind;

CREATE TABLE IF NOT EXISTS analisis_comentarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    comentario TEXT NOT NULL,

    emotion_label VARCHAR(64),
    emotion_score FLOAT,

    stress_level VARCHAR(32),
    sent_pos FLOAT DEFAULT 0.0,
    sent_neu FLOAT DEFAULT 0.0,
    sent_neg FLOAT DEFAULT 0.0,

    categories JSON,
    summary TEXT,
    suggestion TEXT,

    departamento VARCHAR(80) DEFAULT '',
    equipo VARCHAR(80) DEFAULT '',
    fecha VARCHAR(20) DEFAULT '',

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_departamento (departamento),
    INDEX idx_equipo (equipo),
    INDEX idx_stress_level (stress_level),
    INDEX idx_fecha (fecha)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
