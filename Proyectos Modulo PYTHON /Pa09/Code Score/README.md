# Análisis de Riesgo Financiero — Microempresas

Pequeña aplicación de escritorio/web local para capturar datos financieros diarios/mensuales, visualizar gráficos y analizar niveles de riesgo por mes.

## Requisitos
- Python 3.10+ (probado en 3.11.3 en la venv del proyecto)
- Windows, Linux o macOS

## Dependencias
Ver `requirements.txt` para la lista exacta. Instala con:

```powershell
# activar venv o usar el Python del sistema
python -m venv .venv; . .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

## Archivos importantes
- `app.py` — código principal de la aplicación (Flet + Matplotlib + pandas)
- `finanzas_empresaxyz.csv` — archivo de datos principal (se crea si no existe)
- `finanzas_empresaxyz_expandido.csv` — ejemplo/import posible
- `*.bak` / `*.bak_normalize` — backups creados automáticamente en operaciones destructivas

## Cómo ejecutar
1. Crear y activar un entorno virtual (opcional pero recomendado):

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Ejecuta la aplicación:

```powershell
python .\app.py
```

La interfaz se abrirá (modo web/desktop según tu instalación de Flet). Navega a la pestaña "Captura de datos" para añadir registros o importa un CSV.

## Notas importantes
- La aplicación intenta detectar formatos de fecha con heurística (día/mes o mes/día). Si importas CSV con fechas en formato `dd/mm/YYYY`, usa el botón "Normalizar CSV" después de importar para convertir fechas a ISO (`YYYY-MM-DD`).
- Antes de sobrescribir el CSV original la app crea una copia de seguridad `*.bak`.
- Si deseas compartir el proyecto, incluye la carpeta `.venv` opcionalmente o explícales que creen un venv y usen `pip install -r requirements.txt`.

## Personalización
- Puedes cambiar la constante `CSV_PATH` en `app.py` para apuntar a otro archivo por defecto.
- Para mostrar el nivel `MEDIO` en la gráfica de distribución de riesgo, busca la función `fig_distribucion_riesgo` en `app.py`.

## Licencia
Código entregado para uso educativo/prototipo.
