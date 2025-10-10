from __future__ import annotations
import os, csv, sys, math, zipfile, json, webbrowser
from datetime import datetime, date, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Matplotlib en Tk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import FuncFormatter, MaxNLocator

# Estilo global
PALETTE = {
    "inc": "#2E7D32",
    "exp": "#C62828",
    "net": "#1565C0",
    "grid": "#D0D7DE",
    "accent": "#6A5ACD",
}
plt.rcParams.update({
    "axes.edgecolor": "#E5E7EB",
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "axes.titleweight": "bold",
    "font.size": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.facecolor": "white",
})

# Constantes y archivos
CSV_HEADERS = ["fecha", "tipo", "categoria", "descripcion", "monto"]
DEFAULT_CSV = "finanzas.csv"
DEFAULT_CFG = "finanzas_config.json"   # guarda ajustes: saldo inicial, objetivos, topes
REPORTS_DIR = "reportes"

def ensure_dirs():
    os.makedirs(REPORTS_DIR, exist_ok=True)

def ensure_csv(path: str):
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f); writer.writerow(CSV_HEADERS)
        with open(path, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["2025-09-25","ingreso","ventas","Paquete básico","900"])
            w.writerow(["2025-09-26","gasto","alquiler","Renta local","600"])
            w.writerow(["2025-09-27","gasto","marketing","Anuncios","150"])
            w.writerow(["2025-09-28","ingreso","servicios","Servicio premium","1400"])
            w.writerow(["2025-09-29","gasto","salarios","Asistente","450"])
            w.writerow(["2025-09-30","gasto","insumos","Materiales","180"])
            w.writerow(["2025-10-01","ingreso","ventas","Producto A","1500"])
            w.writerow(["2025-10-02","gasto","alquiler","Renta local","600"])
            w.writerow(["2025-10-03","gasto","marketing","Redes","120"])
            w.writerow(["2025-10-04","ingreso","servicios","Consultoría","800"])
            w.writerow(["2025-10-05","gasto","salarios","Pago asistente","400"])
            w.writerow(["2025-10-06","gasto","insumos","Materiales","220"])
            w.writerow(["2025-10-07","ingreso","otros","Reembolso","150"])

def read_csv_file(path: str) -> List[dict]:
    ensure_csv(path)
    rows = []
    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if not set(CSV_HEADERS) <= set(r.keys()): continue
            try:
                r["monto"] = float(r["monto"])
            except Exception:
                continue
            rows.append(r)
    return rows

def append_row(path: str, row: dict):
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writerow(row)

def import_csv(target_path: str, source_path: str) -> int:
    base = read_csv_file(target_path)
    existing = {(d["fecha"], d["tipo"], d["categoria"], d["descripcion"], float(d["monto"])) for d in base}
    new_count = 0
    with open(source_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if not set(CSV_HEADERS) <= set(r.keys()): continue
            try:
                tup = (r["fecha"], r["tipo"].lower(), r["categoria"], r["descripcion"], float(r["monto"]))
            except Exception:
                continue
            if tup not in existing:
                append_row(target_path, {
                    "fecha": r["fecha"], "tipo": r["tipo"].lower(), "categoria": r["categoria"],
                    "descripcion": r["descripcion"], "monto": tup[4],
                })
                new_count += 1
    return new_count

# Configuración (ajustes financieros)
DEFAULT_SETTINGS = {
    "saldo_inicial": 0.0,
    "objetivo_ahorro_pct": 10.0,   # % de ingresos
    "colchon_meses_objetivo": 3.0, # meses de gastos a cubrir
    "tope_categoria": {"marketing": 15.0}  # % del gasto total (por ejemplo)
}

def read_settings(path: str=DEFAULT_CFG) -> dict:
    if not os.path.exists(path):
        save_settings(DEFAULT_SETTINGS, path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_SETTINGS.copy()

def save_settings(cfg: dict, path: str=DEFAULT_CFG):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

# Dominio
@dataclass
class FinanceRecord:
    fecha: date
    tipo: str          # ingreso | gasto
    categoria: str
    descripcion: str
    monto: float

@dataclass
class FinanceData:
    records: List[FinanceRecord] = field(default_factory=list)

    @staticmethod
    def from_rows(rows: List[dict]) -> "FinanceData":
        out = []
        for r in rows:
            try:
                out.append(FinanceRecord(
                    fecha=datetime.strptime(r["fecha"], "%Y-%m-%d").date(),
                    tipo=r["tipo"].strip().lower(),
                    categoria=r["categoria"].strip(),
                    descripcion=r.get("descripcion","").strip(),
                    monto=float(r["monto"]),
                ))
            except Exception:
                continue
        return FinanceData(out)

    def filter_period(self, month: Optional[str]=None, start: Optional[str]=None, end: Optional[str]=None) -> "FinanceData":
        def in_range(d: date) -> bool:
            if month:
                try:
                    mstart = datetime.strptime(month+"-01", "%Y-%m-%d").date()
                    mend = (mstart.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                    return mstart <= d <= mend
                except Exception:
                    return True
            s = datetime.strptime(start, "%Y-%m-%d").date() if start else None
            e = datetime.strptime(end, "%Y-%m-%d").date() if end else None
            if s and d < s: return False
            if e and d > e: return False
            return True
        return FinanceData([r for r in self.records if in_range(r.fecha)])

    def totals(self) -> Tuple[float,float,float]:
        inc = sum(r.monto for r in self.records if r.tipo == "ingreso")
        exp = sum(r.monto for r in self.records if r.tipo == "gasto")
        net = inc - exp
        return inc, exp, net

    def by_category_expenses(self) -> Dict[str,float]:
        d = defaultdict(float)
        for r in self.records:
            if r.tipo == "gasto": d[r.categoria] += r.monto
        return dict(sorted(d.items(), key=lambda kv: -kv[1]))

    def daily_series(self) -> Dict[date,float]:
        d = defaultdict(float)
        for r in self.records:
            d[r.fecha] += r.monto if r.tipo == "ingreso" else -r.monto
        return dict(sorted(d.items(), key=lambda kv: kv[0]))

    def monthly_net_series(self) -> Dict[str,float]:
        d = defaultdict(float)
        for r in self.records:
            k = r.fecha.strftime("%Y-%m")
            d[k] += r.monto if r.tipo == "ingreso" else -r.monto
        return dict(sorted(d.items(), key=lambda kv: kv[0]))

    def monthly_inc_exp(self) -> Dict[str, Tuple[float,float,float]]:
        """Devuelve {YYYY-MM: (ingresos, gastos, neto)}"""
        inc = defaultdict(float); exp = defaultdict(float)
        for r in self.records:
            k = r.fecha.strftime("%Y-%m")
            if r.tipo == "ingreso": inc[k] += r.monto
            else: exp[k] += r.monto
        keys = sorted(set(inc.keys()) | set(exp.keys()))
        return {k: (inc.get(k,0.0), exp.get(k,0.0), inc.get(k,0.0)-exp.get(k,0.0)) for k in keys}

    def stats(self) -> Dict[str,float]:
        inc, exp, net = self.totals()
        gastos = self.by_category_expenses()
        top_cat = next(iter(gastos.keys())) if gastos else ""
        top_val = gastos[top_cat] if top_cat else 0.0
        ahorro_pct = (net/inc*100) if inc>0 else 0.0
        return {"ingresos":inc,"gastos":exp,"neto":net,"top":top_cat,"top_val":top_val,"ahorro_pct":ahorro_pct}

# Helpers formato y análisis
def usd_fmt(x, _pos=None):
    sign = "-" if x < 0 else ""
    v = abs(x)
    return f"{sign}${v:,.2f}"

def pct_fmt(x, _pos=None):
    return f"{x:.0f}%"

def group_top_n(d: Dict[str,float], n=6) -> Dict[str,float]:
    if len(d) <= n: return d
    items = list(d.items())
    top = items[:n]; rest = items[n:]
    out = dict(top); out["Otros"] = sum(v for _,v in rest); return out

def moving_average(seq: List[float], w: int) -> List[float]:
    w = max(1, int(w))
    out=[]; q=deque(maxlen=w); s=0.0
    for v in seq:
        q.append(v); s = sum(q); out.append(s/len(q))
    return out

def analyze_finances(fd: FinanceData, settings: dict) -> Dict[str, any]:
    """Cálculos adicionales para el reporte/alertas."""
    inc, exp, net = fd.totals()
    gastos_cat = fd.by_category_expenses()
    monthly = fd.monthly_inc_exp()
    months = list(monthly.keys())
    prom_neto = 0.0
    if months:
        prom_neto = sum(monthly[m][2] for m in months)/len(months)

    # runway con saldo inicial si el promedio es negativo
    saldo_inicial = float(settings.get("saldo_inicial", 0.0) or 0.0)
    runway_meses = None
    if prom_neto < 0 and saldo_inicial > 0:
        runway_meses = max(0.0, saldo_inicial/abs(prom_neto))

    # ahorro objetivo
    objetivo_pct = float(settings.get("objetivo_ahorro_pct", 10.0) or 0.0)
    ahorro_real_pct = (net/inc*100) if inc>0 else 0.0
    gap_ahorro_pct = objetivo_pct - ahorro_real_pct

    # break-even (ingreso mínimo para cubrir gastos)
    break_even = exp

    # tope por categoría (alertas si supera % del gasto)
    tope_map = settings.get("tope_categoria", {}) or {}
    alertas = []
    gasto_total = sum(gastos_cat.values()) or 1.0
    for cat, pct_tope in tope_map.items():
        uso = 100.0*(gastos_cat.get(cat,0.0)/gasto_total)
        if uso > pct_tope:
            alertas.append(f"⚠️ {cat}: {uso:.1f}% del gasto supera tope ({pct_tope:.1f}%). Considera recortar.")

    # crecimiento de gastos mes a mes
    growth_alert = None
    if len(months) >= 2:
        last = months[-1]; prev = months[-2]
        gasto_last = monthly[last][1]; gasto_prev = monthly[prev][1] or 1.0
        growth = 100.0*(gasto_last/gasto_prev - 1.0)
        if growth > 20:
            growth_alert = f"⚠️ Los gastos subieron {growth:.1f}% vs {prev}. Revisa incrementos puntuales."
        elif growth < -20:
            growth_alert = f"✅ Los gastos bajaron {abs(growth):.1f}% vs {prev}. Mantén el control."

    # recomendación de recorte para alcanzar objetivo de ahorro
    recomendaciones = []
    if inc > 0 and gap_ahorro_pct > 0:
        # monto adicional que necesitas ahorrar
        monto_extra_ahorro = inc*(gap_ahorro_pct/100.0)
        # sugerir recortar 1-2 categorías principales hasta cubrir ese gap
        cats_sorted = sorted(gastos_cat.items(), key=lambda kv: -kv[1])
        suger = []
        restante = monto_extra_ahorro
        for cat, val in cats_sorted[:3]:
            recorte = min(val*0.2, restante)  # propone recortar hasta 20% de cada top
            if recorte > 0:
                suger.append(f"- {cat}: recorta {usd_fmt(recorte)} (~{recorte/val*100:.0f}% del gasto de esa cat.)")
                restante -= recorte
            if restante <= 1: break
        if suger:
            recomendaciones.append("Para alcanzar tu objetivo de ahorro:")
            recomendaciones.extend(suger)

    if net < 0:
        recomendaciones.append(f"Estás en déficit de {usd_fmt(abs(net))}. Alcanza break-even con ingresos ≥ {usd_fmt(break_even)} o reduce gastos.")

    return {
        "prom_neto": prom_neto,
        "runway_meses": runway_meses,
        "ahorro_obj_pct": objetivo_pct,
        "ahorro_real_pct": ahorro_real_pct,
        "gap_ahorro_pct": gap_ahorro_pct,
        "break_even": break_even,
        "alertas": [a for a in [growth_alert] if a] + alertas,
        "recomendaciones": recomendaciones,
        "top3_gastos": list(fd.by_category_expenses().items())[:3],
    }

# App GUI
class FinanceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        ensure_dirs()
        self.title("Finanzas GUI PRO+MD")
        self.geometry("1320x870"); self.minsize(1160, 760)

        self.csv_path = DEFAULT_CSV
        ensure_csv(self.csv_path)
        self.fd_all = FinanceData.from_rows(read_csv_file(self.csv_path))
        self.filtered = self.fd_all

        self.settings = read_settings()

        # UI
        self._build_toolbar()
        self._build_filters()
        self._build_summary()
        self._build_notebook()
        self._build_status()

        self.render_all()

    # ToolBar
    def _build_toolbar(self):
        bar = ttk.Frame(self, padding=(10,8)); bar.pack(side=tk.TOP, fill=tk.X)
        self.csv_label = ttk.Label(bar, text=f"CSV: {os.path.abspath(self.csv_path)}")
        self.csv_label.pack(side=tk.LEFT)

        ttk.Separator(bar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        ttk.Button(bar, text="Abrir CSV…", command=self.on_open_csv).pack(side=tk.LEFT, padx=3)
        ttk.Button(bar, text="Importar CSV…", command=self.on_import_csv).pack(side=tk.LEFT, padx=3)
        ttk.Button(bar, text="Agregar Ingreso", command=lambda: self.on_add("ingreso")).pack(side=tk.LEFT, padx=3)
        ttk.Button(bar, text="Agregar Gasto", command=lambda: self.on_add("gasto")).pack(side=tk.LEFT, padx=3)

        ttk.Separator(bar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        ttk.Button(bar, text="Ajustes…", command=self.on_settings).pack(side=tk.LEFT, padx=3)
        ttk.Button(bar, text="Reporte Markdown", command=self.on_report_md).pack(side=tk.LEFT, padx=3)

        ttk.Separator(bar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        ttk.Button(bar, text="Exportar PNGs", command=self.export_all_png).pack(side=tk.LEFT, padx=3)
        ttk.Button(bar, text="Exportar ZIP", command=self.export_zip).pack(side=tk.LEFT, padx=3)
        ttk.Button(bar, text="Exportar PDF", command=self.export_pdf).pack(side=tk.LEFT, padx=3)

    # Filtros
    def _build_filters(self):
        box = ttk.Frame(self, padding=(12,4)); box.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(box, text="Período:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0,8))
        self.period_var = tk.StringVar(value="todo")
        ttk.Radiobutton(box, text="Todo", value="todo", variable=self.period_var, command=self._toggle_filters).pack(side=tk.LEFT)
        ttk.Radiobutton(box, text="Mes (YYYY-MM)", value="mes", variable=self.period_var, command=self._toggle_filters).pack(side=tk.LEFT)
        ttk.Radiobutton(box, text="Rango", value="rango", variable=self.period_var, command=self._toggle_filters).pack(side=tk.LEFT)

        self.ent_mes = ttk.Entry(box, width=10); self.ent_mes.insert(0, "2025-10"); self.ent_mes.pack(side=tk.LEFT, padx=6)
        self.ent_ini = ttk.Entry(box, width=12); self.ent_ini.insert(0, "2025-09-25")
        self.ent_fin = ttk.Entry(box, width=12); self.ent_fin.insert(0, "2025-10-07")

        ttk.Label(box, text=" | Media móvil:", padding=(10,0)).pack(side=tk.LEFT)
        self.mov_win = tk.IntVar(value=5)
        ttk.Spinbox(box, from_=2, to=60, width=5, textvariable=self.mov_win).pack(side=tk.LEFT)

        ttk.Button(box, text="Actualizar", command=self.apply_filters).pack(side=tk.LEFT, padx=10)
        self._toggle_filters()

    # Resumen
    def _build_summary(self):
        frame = ttk.LabelFrame(self, text="Resumen y consejos", padding=(10,8))
        frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(0,6))
        self.lbl_kpi = ttk.Label(frame, text="", font=("Segoe UI", 10), justify="left")
        self.lbl_kpi.pack(anchor="w")

    # Tabs
    def _build_notebook(self):
        self.nb = ttk.Notebook(self); self.nb.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
        self.tabs = {}
        for key, title in [
            ("barras", "Barras: Ingresos vs Gastos"),
            ("pie", "Pie: Gastos por Categoría (Top N)"),
            ("dona", "Dona: Gastos por Categoría (Top N)"),
            ("flujo", "Líneas: Flujo Diario + Media Móvil + Acumulado"),
            ("waterfall", "Waterfall: Neto Mensual"),
            ("box", "Boxplot: Gastos por Categoría"),
            ("pareto", "Pareto: Gastos por Categoría"),
        ]:
            frame = ttk.Frame(self.nb); self.nb.add(frame, text=title)
            self.tabs[key] = {"frame": frame, "figure": None, "canvas": None}

    # Status
    def _build_status(self):
        status = ttk.Frame(self, padding=(10,6)); status.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var = tk.StringVar(value="Listo.")
        ttk.Label(status, textvariable=self.status_var).pack(side=tk.LEFT)

    # Eventos
    def _toggle_filters(self):
        mode = self.period_var.get()
        if mode == "todo":
            self.ent_mes.pack_forget(); self.ent_ini.pack_forget(); self.ent_fin.pack_forget()
        elif mode == "mes":
            self.ent_ini.pack_forget(); self.ent_fin.pack_forget()
            self.ent_mes.pack(side=tk.LEFT, padx=6)
        else:
            self.ent_mes.pack_forget()
            self.ent_ini.pack(side=tk.LEFT, padx=6); self.ent_fin.pack(side=tk.LEFT)

    def on_open_csv(self):
        p = filedialog.askopenfilename(title="Abrir CSV", filetypes=[("CSV", "*.csv"), ("Todos", "*.*")])
        if not p: return
        self.csv_path = p; self.csv_label.config(text=f"CSV: {os.path.abspath(self.csv_path)}")
        self._reload()

    def on_import_csv(self):
        p = filedialog.askopenfilename(title="Importar CSV", filetypes=[("CSV", "*.csv"), ("Todos", "*.*")])
        if not p: return
        n = import_csv(self.csv_path, p)
        messagebox.showinfo("Importación", f"Importados {n} registros.")
        self._reload()

    def on_add(self, tipo: str):
        try:
            top = tk.Toplevel(self); top.title(f"Agregar {tipo.capitalize()}"); top.grab_set()
            frm = ttk.Frame(top, padding=10); frm.pack(fill=tk.BOTH, expand=True)
            ttk.Label(frm, text="Fecha (YYYY-MM-DD):").grid(row=0, column=0, sticky="w"); e_fecha = ttk.Entry(frm); e_fecha.grid(row=0, column=1, sticky="ew"); e_fecha.insert(0, datetime.today().strftime("%Y-%m-%d"))
            ttk.Label(frm, text="Categoría:").grid(row=1, column=0, sticky="w"); e_cat = ttk.Entry(frm); e_cat.grid(row=1, column=1, sticky="ew")
            ttk.Label(frm, text="Descripción:").grid(row=2, column=0, sticky="w"); e_desc = ttk.Entry(frm); e_desc.grid(row=2, column=1, sticky="ew")
            ttk.Label(frm, text="Monto:").grid(row=3, column=0, sticky="w"); e_monto = ttk.Entry(frm); e_monto.grid(row=3, column=1, sticky="ew")
            frm.columnconfigure(1, weight=1)
            def ok():
                try:
                    fecha = datetime.strptime(e_fecha.get().strip(), "%Y-%m-%d").date()
                    categoria = e_cat.get().strip() or ("ventas" if tipo=="ingreso" else "varios")
                    descripcion = e_desc.get().strip()
                    monto = float(e_monto.get().strip())
                    if monto <= 0: raise ValueError("Monto debe ser > 0")
                    append_row(self.csv_path, {"fecha":str(fecha),"tipo":tipo,"categoria":categoria,"descripcion":descripcion,"monto":monto})
                    top.destroy(); self._reload()
                except Exception as ex:
                    messagebox.showerror("Dato inválido", f"Revisa los campos.\n\n{ex}")
            ttk.Button(frm, text="Guardar", command=ok).grid(row=4, column=0, pady=(10,0))
            ttk.Button(frm, text="Cancelar", command=top.destroy).grid(row=4, column=1, pady=(10,0), sticky="e")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_settings(self):
        cfg = read_settings()
        top = tk.Toplevel(self); top.title("Ajustes financieros"); top.grab_set()
        frm = ttk.Frame(top, padding=10); frm.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frm, text="Saldo inicial (para runway):").grid(row=0, column=0, sticky="w"); e_saldo = ttk.Entry(frm); e_saldo.grid(row=0, column=1, sticky="ew"); e_saldo.insert(0, str(cfg.get("saldo_inicial",0.0)))
        ttk.Label(frm, text="Objetivo de ahorro (%) de ingresos:").grid(row=1, column=0, sticky="w"); e_obj = ttk.Entry(frm); e_obj.grid(row=1, column=1, sticky="ew"); e_obj.insert(0, str(cfg.get("objetivo_ahorro_pct",10.0)))
        ttk.Label(frm, text="Colchón objetivo (meses de gasto):").grid(row=2, column=0, sticky="w"); e_col = ttk.Entry(frm); e_col.grid(row=2, column=1, sticky="ew"); e_col.insert(0, str(cfg.get("colchon_meses_objetivo",3.0)))
        ttk.Label(frm, text="Tope categoría (JSON {'cat': %,...}):").grid(row=3, column=0, sticky="w"); e_tope = ttk.Entry(frm); e_tope.grid(row=3, column=1, sticky="ew"); e_tope.insert(0, json.dumps(cfg.get("tope_categoria",{}), ensure_ascii=False))
        frm.columnconfigure(1, weight=1)
        def guardar():
            try:
                cfg["saldo_inicial"] = float(e_saldo.get().strip() or 0)
                cfg["objetivo_ahorro_pct"] = float(e_obj.get().strip() or 0)
                cfg["colchon_meses_objetivo"] = float(e_col.get().strip() or 0)
                cfg["tope_categoria"] = json.loads(e_tope.get().strip() or "{}")
                save_settings(cfg); self.settings = cfg
                top.destroy(); self.render_all()
            except Exception as ex:
                messagebox.showerror("Error", f"No se pudieron guardar ajustes:\n{ex}")
        ttk.Button(frm, text="Guardar ajustes", command=guardar).grid(row=4, column=0, pady=(10,0))
        ttk.Button(frm, text="Cerrar", command=top.destroy).grid(row=4, column=1, pady=(10,0), sticky="e")

    def _reload(self):
        rows = read_csv_file(self.csv_path)
        self.fd_all = FinanceData.from_rows(rows)
        self.apply_filters()

    def apply_filters(self):
        mode = self.period_var.get()
        month = start = end = None
        if mode == "mes": month = self.ent_mes.get().strip()
        elif mode == "rango":
            start = self.ent_ini.get().strip(); end = self.ent_fin.get().strip()
        self.filtered = self.fd_all.filter_period(month, start, end)
        self.render_all()

    # Render
    def render_all(self):
        try:
            inc, exp, net = self.filtered.totals()
            gastos_cat = self.filtered.by_category_expenses()
            daily = self.filtered.daily_series()
            monthly = self.filtered.monthly_net_series()
            suf = self._suffix()

            # análisis
            st = self.filtered.stats()
            deep = analyze_finances(self.filtered, self.settings)
            consejo = "✅ Positivo, separa 10–20% a emergencia." if st["neto"]>=0 else "⚠️ Déficit, ajusta categoría principal."
            extra = []
            if deep["runway_meses"] is not None:
                extra.append(f"Runway: {deep['runway_meses']:.1f} meses con saldo inicial.")
            extra.append(f"Objetivo ahorro: {deep['ahorro_obj_pct']:.1f}% | Real: {deep['ahorro_real_pct']:.1f}%")
            if deep["gap_ahorro_pct"]>0:
                extra.append(f"Te falta {deep['gap_ahorro_pct']:.1f} pts para el objetivo.")
            self.lbl_kpi.config(text=(
                f"Ingresos: {usd_fmt(inc)}   |   Gastos: {usd_fmt(exp)}   |   Neto: {usd_fmt(net)}   |   Ahorro: {st['ahorro_pct']:.1f}%\n"
                f"Mayor gasto: {st['top'] or '—'} ({usd_fmt(st['top_val'])})   ·   {consejo}\n"
                + (" · ".join(extra))
            ))

            # Gráficas
            self._render_barras(inc, exp, net, suf)
            self._render_pie(group_top_n(gastos_cat), suf)
            self._render_dona(group_top_n(gastos_cat), suf)
            self._render_flujo(daily, suf, window=self.mov_win.get())
            self._render_waterfall(monthly, suf)
            self._render_boxplot(self.filtered, suf)
            self._render_pareto(gastos_cat, suf)

            # alertas en status
            alerts = deep["alertas"]
            if alerts:
                self.status(" | ".join(alerts))
            else:
                self.status("Gráficas y análisis actualizados.")
        except Exception as e:
            messagebox.showerror("Error al graficar", str(e))

    def _prepare_tab(self, key: str):
        tab = self.tabs[key]
        for child in tab["frame"].winfo_children(): child.destroy()
        fig = plt.Figure(figsize=(9.6,5.4), dpi=100)
        canvas = FigureCanvasTkAgg(fig, master=tab["frame"])
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        tab["figure"] = fig; tab["canvas"] = canvas
        return fig, canvas

    def _suffix(self):
        m = self.period_var.get()
        if m=="mes": return f" ({self.ent_mes.get().strip()})"
        if m=="rango": return f" ({self.ent_ini.get().strip()}..{self.ent_fin.get().strip()})"
        return " (Todo)"

    # Gráficas
    def _render_barras(self, inc: float, exp: float, net: float, suf: str):
        fig, canvas = self._prepare_tab("barras")
        ax = fig.add_subplot(111)
        ax.set_title(f"Ingresos vs Gastos{suf}")
        rects = ax.bar(["Ingresos", "Gastos"], [inc, exp], color=[PALETTE["inc"], PALETTE["exp"]], alpha=0.9)
        ax.axhline(0, color="#888888", linewidth=0.8)
        ax.plot([-0.3, 1.3], [net, net], color=PALETTE["net"], linewidth=2, linestyle="--", label=f"Neto: {usd_fmt(net)}")
        ax.yaxis.set_major_formatter(FuncFormatter(usd_fmt))
        ax.yaxis.set_major_locator(MaxNLocator(nbins=6, prune="lower"))
        ax.grid(axis="y", linestyle="--", color=PALETTE["grid"], alpha=0.7)
        for r, val in zip(rects, [inc, exp]):
            ax.annotate(usd_fmt(val), (r.get_x()+r.get_width()/2, r.get_height()),
                        xytext=(0, 6), textcoords="offset points", ha="center", va="bottom", fontsize=11, weight="bold")
        ax.legend(loc="upper right")
        fig.tight_layout(); canvas.draw()

    def _render_pie(self, gastos_cat: Dict[str,float], suf: str):
        fig, canvas = self._prepare_tab("pie"); ax = fig.add_subplot(111)
        ax.set_title(f"Gastos por categoría (Top N){suf}")
        if not gastos_cat:
            ax.text(0.5, 0.5, "No hay datos de gastos", ha="center", va="center", fontsize=12)
        else:
            labels = list(gastos_cat.keys()); sizes = list(gastos_cat.values())
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct=lambda p: f"{p:.1f}%",
                                              startangle=90, pctdistance=0.75)
            for at in autotexts: at.set_fontweight("bold")
            ax.axis("equal")
        fig.tight_layout(); canvas.draw()

    def _render_dona(self, gastos_cat: Dict[str,float], suf: str):
        fig, canvas = self._prepare_tab("dona"); ax = fig.add_subplot(111)
        ax.set_title(f"Dona — Gastos por categoría (Top N){suf}")
        if not gastos_cat:
            ax.text(0.5, 0.5, "No hay datos de gastos", ha="center", va="center", fontsize=12)
        else:
            labels = list(gastos_cat.keys()); sizes = list(gastos_cat.values())
            ax.pie(sizes, labels=labels, autopct=lambda p: f"{p:.1f}%", startangle=90, pctdistance=0.78)
            centre = plt.Circle((0,0), 0.55, fc="white")
            ax.add_artist(centre); ax.axis("equal")
        fig.tight_layout(); canvas.draw()

    def _render_flujo(self, daily: Dict[date,float], suf: str, window: int=5):
        fig, canvas = self._prepare_tab("flujo"); ax = fig.add_subplot(111)
        ax.set_title(f"Flujo diario + Media móvil ({window}) + Acumulado{suf}")
        if not daily:
            ax.text(0.5, 0.5, "No hay serie diaria", ha="center", va="center", fontsize=12)
        else:
            days = list(daily.keys()); vals = [daily[d] for d in days]
            acc, s = [], 0.0
            for v in vals: s += v; acc.append(s)
            mv = moving_average(vals, window)
            ax.plot(days, vals, label="Flujo diario", color=PALETTE["accent"], linewidth=1.8)
            ax.plot(days, mv, label="Media móvil", color=PALETTE["inc"], linestyle="--", linewidth=2.2)
            ax.plot(days, acc, label="Acumulado", color=PALETTE["net"], linestyle=":", linewidth=2.2)
            ax.yaxis.set_major_formatter(FuncFormatter(usd_fmt))
            ax.grid(True, linestyle="--", color=PALETTE["grid"], alpha=0.7)
            ax.legend(loc="best"); fig.autofmt_xdate()
        fig.tight_layout(); canvas.draw()

    def _render_waterfall(self, monthly_net: Dict[str,float], suf: str):
        fig, canvas = self._prepare_tab("waterfall"); ax = fig.add_subplot(111)
        ax.set_title(f"Waterfall del neto mensual{suf}")
        if not monthly_net:
            ax.text(0.5, 0.5, "No hay datos mensuales", ha="center", va="center", fontsize=12)
        else:
            keys = list(monthly_net.keys()); vals = [monthly_net[k] for k in keys]
            running = 0.0; bottoms = []; heights = []; colors = []; ymax = 0.0
            for v in vals:
                if v >= 0: bottoms.append(running); heights.append(v); running += v; colors.append(PALETTE["inc"])
                else:      bottoms.append(running+v); heights.append(-v); running += v; colors.append(PALETTE["exp"])
                ymax = max(ymax, abs(v))
            bars = ax.bar(keys, heights, bottom=bottoms, color=colors, alpha=0.9)
            for i, (k, v) in enumerate(zip(keys, vals)):
                y = bottoms[i] + (heights[i] if v >= 0 else 0)
                ax.text(i, y + max(1.0, ymax)*0.02, f"{v:+,.2f}", ha="center", va="bottom", fontsize=10, weight="bold")
            ax.yaxis.set_major_formatter(FuncFormatter(usd_fmt))
            ax.grid(axis="y", linestyle="--", color=PALETTE["grid"], alpha=0.7)
        fig.tight_layout(); canvas.draw()

    def _render_boxplot(self, data: FinanceData, suf: str):
        fig, canvas = self._prepare_tab("box"); ax = fig.add_subplot(111)
        ax.set_title(f"Distribución de gastos por categoría (boxplot){suf}")
        cat_map = defaultdict(list)
        for r in data.records:
            if r.tipo=="gasto": cat_map[r.categoria].append(r.monto)
        if not cat_map:
            ax.text(0.5, 0.5, "No hay gastos", ha="center", va="center", fontsize=12)
        else:
            labels = list(cat_map.keys()); values = [cat_map[k] for k in labels]
            bp = ax.boxplot(values, labels=labels, showmeans=True, meanline=True)
            # resaltar media (verde) y mediana (azul)
            for med in bp["medians"]:
                med.set_color(PALETTE["net"]); med.set_linewidth(2.2)
            for mean in bp["means"]:
                mean.set_color(PALETTE["inc"]); mean.set_linewidth(2.0)
            ax.yaxis.set_major_formatter(FuncFormatter(usd_fmt))
            ax.grid(True, axis="y", linestyle="--", color=PALETTE["grid"], alpha=0.7)
        fig.tight_layout(); canvas.draw()

    def _render_pareto(self, gastos_cat: Dict[str,float], suf: str):
        fig, canvas = self._prepare_tab("pareto"); ax = fig.add_subplot(111)
        ax.set_title(f"Pareto de gastos por categoría{suf}")
        if not gastos_cat:
            ax.text(0.5, 0.5, "No hay datos de gastos", ha="center", va="center", fontsize=12)
        else:
            items = list(gastos_cat.items()); cats = [k for k,_ in items]; vals = [v for _,v in items]
            total = sum(vals) or 1.0
            cum, s = [], 0.0
            for v in vals: s += v; cum.append(100.0*s/total)
            ax.bar(cats, vals, color=PALETTE["exp"], alpha=0.9)
            ax2 = ax.twinx(); ax2.plot(cats, cum, marker="o", color=PALETTE["net"], linewidth=2.0)
            ax.set_ylabel("USD"); ax2.set_ylabel("Acumulado (%)")
            ax.yaxis.set_major_formatter(FuncFormatter(usd_fmt))
            ax2.yaxis.set_major_formatter(FuncFormatter(pct_fmt)); ax2.set_ylim(0, 110)
            ax.grid(axis="y", linestyle="--", color=PALETTE["grid"], alpha=0.7)
            for i, v in enumerate(vals):
                ax.text(i, v + max(1.0, max(vals))*0.02, f"{usd_fmt(v)}", ha="center", va="bottom", fontsize=10, weight="bold")
        fig.tight_layout(); canvas.draw()

    # Reporte Markdown
    def on_report_md(self):
        path = filedialog.asksaveasfilename(title="Guardar Reporte Markdown",
                                            defaultextension=".md",
                                            filetypes=[("Markdown","*.md")],
                                            initialdir=os.path.abspath(REPORTS_DIR),
                                            initialfile=f"reporte_finanzas{self._suffix().replace(' ','_')}.md")
        if not path: return
        try:
            content = self._build_markdown_report()
            with open(path, "w", encoding="utf-8") as f: f.write(content)
            self.status(f"Reporte MD guardado: {path}")
            if messagebox.askyesno("Reporte guardado", "¿Abrir el archivo?"):
                webbrowser.open(f"file://{os.path.abspath(path)}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el reporte:\n{e}")

    def _build_markdown_report(self) -> str:
        fd = self.filtered
        inc, exp, net = fd.totals()
        gastos_cat = fd.by_category_expenses()
        daily = fd.daily_series()
        monthly = fd.monthly_net_series()
        stats = fd.stats()
        deep = analyze_finances(fd, self.settings)

        period = self._suffix().strip()
        lines = []
        lines.append(f"# Reporte Finanzas {period}")
        lines.append("")
        lines.append("## KPIs")
        lines.append(f"- **Ingresos:** {usd_fmt(inc)}")
        lines.append(f"- **Gastos:** {usd_fmt(exp)}")
        lines.append(f"- **Neto:** {usd_fmt(net)}")
        lines.append(f"- **Ahorro (sobre ingresos):** {stats['ahorro_pct']:.2f}%")
        if deep["runway_meses"] is not None:
            lines.append(f"- **Runway estimado:** {deep['runway_meses']:.1f} meses (con saldo inicial {usd_fmt(self.settings.get('saldo_inicial',0.0))})")
        lines.append("")
        lines.append("## Análisis")
        top3 = deep["top3_gastos"]
        if top3:
            lines.append("- **Top 3 gastos por categoría:**")
            for c,v in top3:
                lines.append(f"  - {c}: {usd_fmt(v)}")
        lines.append(f"- **Objetivo de ahorro:** {deep['ahorro_obj_pct']:.1f}% | **Real:** {deep['ahorro_real_pct']:.1f}% | **Brecha:** {max(0.0, deep['gap_ahorro_pct']):.1f} pts")
        lines.append(f"- **Break-even aproximado:** ingresos ≥ {usd_fmt(deep['break_even'])}")
        if deep["alertas"]:
            lines.append("")
            lines.append("### Alertas")
            for a in deep["alertas"]:
                lines.append(f"- {a}")
        if deep["recomendaciones"]:
            lines.append("")
            lines.append("### Recomendaciones")
            for r in deep["recomendaciones"]:
                lines.append(f"{r}")
        lines.append("")
        lines.append("## Gráficas recomendadas (si exportaste)")
        lines.append("- 01_barras_ingresos_gastos*.png")
        lines.append("- 02_pie_gastos*.png")
        lines.append("- 03_dona_gastos*.png")
        lines.append("- 04_linea_flujo*.png")
        lines.append("- 05_waterfall_mensual*.png")
        lines.append("- 06_boxplot_gastos*.png")
        lines.append("- 07_pareto_gastos*.png")
        lines.append("")
        lines.append("> Generado por Finanzas GUI PRO+MD")
        return "\n".join(lines)

    # Export
    def _collect_figures(self) -> List[Tuple[str, plt.Figure]]:
        mapping = [
            ("01_barras_ingresos_gastos","barras"),
            ("02_pie_gastos","pie"),
            ("03_dona_gastos","dona"),
            ("04_linea_flujo","flujo"),
            ("05_waterfall_mensual","waterfall"),
            ("06_boxplot_gastos","box"),
            ("07_pareto_gastos","pareto"),
        ]
        out=[]
        for base,key in mapping:
            fig = self.tabs[key]["figure"]
            if fig: out.append((base, fig))
        return out

    def export_all_png(self):
        folder = filedialog.askdirectory(title="Carpeta destino para PNGs")
        if not folder: return
        suf = self._suffix().replace(" ","_").replace("..","_")
        cnt = 0
        for base,fig in self._collect_figures():
            p = os.path.join(folder, f"{base}{suf}.png")
            fig.savefig(p, dpi=150, bbox_inches="tight"); cnt+=1
        self.status(f"Exportadas {cnt} PNG a {folder}")
        messagebox.showinfo("Exportación", f"Exportadas {cnt} imágenes en:\n{folder}")

    def export_zip(self):
        folder = filedialog.askdirectory(title="Carpeta para ZIP")
        if not folder: return
        suf = self._suffix().replace(" ","_").replace("..","_")
        zip_path = os.path.join(folder, f"graficas{suf}.zip")
        tmp=[]
        for base,fig in self._collect_figures():
            p = os.path.join(folder, f"{base}{suf}.png")
            fig.savefig(p, dpi=150, bbox_inches="tight"); tmp.append(p)
        with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as zf:
            for p in tmp: zf.write(p, arcname=os.path.basename(p))
        self.status(f"ZIP: {zip_path}")
        messagebox.showinfo("ZIP creado", f"Guardado en:\n{zip_path}")

    def export_pdf(self):
        path = filedialog.asksaveasfilename(title="Guardar PDF", defaultextension=".pdf",
                                            filetypes=[("PDF","*.pdf")])
        if not path: return
        with PdfPages(path) as pdf:
            for base, fig in self._collect_figures():
                pdf.savefig(fig, bbox_inches="tight")
        self.status(f"PDF: {path}")
        messagebox.showinfo("PDF exportado", f"Se guardó en:\n{path}")

    def status(self, txt:str): self.status_var.set(txt)

# main
def main():
    app = FinanceApp()
    app.mainloop()

if __name__ == "__main__":
    main()