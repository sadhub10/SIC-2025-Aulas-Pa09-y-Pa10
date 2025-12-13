USE novamind;

CREATE TABLE IF NOT EXISTS usuarios_rrhh (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(100),
    email VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,

    INDEX idx_usuario (usuario)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO usuarios_rrhh (usuario, password_hash, nombre_completo, email)
VALUES
('admin', '$2b$12$VjjApnsYS2jlSwbkH.kGCeSKettEiKf1MXiGIdoBwtXPO9y.yWNau', 'Administrador RRHH', 'admin@empresa.com'),
('rrhh', '$2b$12$VjjApnsYS2jlSwbkH.kGCeSKettEiKf1MXiGIdoBwtXPO9y.yWNau', 'Recursos Humanos', 'rrhh@empresa.com');

