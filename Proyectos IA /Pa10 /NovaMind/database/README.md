# Scripts de Base de Datos

Esta carpeta contiene los scripts SQL y datos de prueba para NovaMind.

## Archivos

### schema.sql
Script para crear la base de datos y la tabla `analisis_comentarios`.

### usuarios.sql
Script para crear la tabla `usuarios_rrhh` y usuarios por defecto.

**Uso:**
```bash
mysql -u root -p < schema.sql
```

O desde MySQL:
```sql
SOURCE schema.sql;
```

**Nota:** El backend crea las tablas automáticamente con SQLAlchemy cuando se ejecuta por primera vez, pero este script está disponible si prefieres crear la estructura manualmente.

### datos_prueba.sql
Script con 20 comentarios pre-analizados para poblar el dashboard inmediatamente.

**Uso:**
```bash
mysql -u root -p novamind < datos_prueba.sql
```

O desde MySQL:
```sql
USE novamind;
SOURCE datos_prueba.sql;
```

Estos datos incluyen:
- Comentarios de diferentes departamentos (Operaciones, Ventas, IT)
- Diferentes niveles de estrés (alto, medio, bajo)
- Variedad de emociones (joy, sadness, anger, fear, neutral)
- Múltiples categorías detectadas
- Fechas en rango de Enero-Febrero 2025

### comentarios_ejemplo.csv
Archivo CSV con 10 comentarios sin analizar para probar la carga masiva.

**Uso:**
1. Desde el frontend: Sección "Análisis CSV" → Subir este archivo
2. Desde el backend API: POST a `/analizar-lote/` con la ruta del archivo

## Inicio Rápido

### Opción 1: Con datos de prueba (recomendado para testing)

```bash
mysql -u root -p < schema.sql
mysql -u root -p novamind < datos_prueba.sql
```

Esto te dará 20 comentarios pre-analizados para ver el dashboard funcionando inmediatamente.

### Opción 2: Base de datos vacía (producción)

```bash
mysql -u root -p < schema.sql
```

Luego usa el frontend o la API para ingresar comentarios que serán analizados por la IA.

### Opción 3: Automático (SQLAlchemy)

Simplemente ejecuta el backend - las tablas se crearán automáticamente:

```bash
uvicorn backend.main:app --reload --port 8000
```

## Verificar Instalación

Desde MySQL:
```sql
USE novamind;
SHOW TABLES;
SELECT COUNT(*) FROM analisis_comentarios;
```

## Limpiar Datos

Para eliminar todos los registros pero mantener la estructura:
```sql
USE novamind;
TRUNCATE TABLE analisis_comentarios;
```

Para eliminar todo:
```sql
DROP DATABASE novamind;
```
