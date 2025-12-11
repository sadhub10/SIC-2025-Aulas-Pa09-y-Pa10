# 🔐 SecureCard IA  
### Sistema Inteligente de Detección de Fraude en Transacciones con Tarjeta  
**Equipo:** CodeScore – Samsung Innovation Campus 2025  

---

## 📌 Descripción General  
SecureCard IA es un sistema inteligente diseñado para **detectar transacciones fraudulentas en tiempo real** utilizando modelos combinados de **IA supervisada, no supervisada y reglas de negocio**.  

Este proyecto nace para atender un problema real:  
> En Panamá, más del 50% de los compradores abandona una compra en línea por sospechas de fraude, y 1 de cada 5 ha sido víctima de estafa.

---

## 🧠 Tecnologías y Modelos Utilizados

### **Modelos de Inteligencia Artificial**
- **XGBoost (supervisado):** Predicción de probabilidad de fraude.  
- **Isolation Forest (no supervisado):** Detección de anomalías atípicas.  
- **Reglas de negocio:** Ajuste del nivel de riesgo según comportamiento, frecuencia, montos y saldos.

### **Backend – Python**
- Pandas, NumPy, Joblib  
- Manejo de CSV como base de datos  
- Procesamiento de fechas y operaciones matemáticas  

### **Frontend – Flet**
- Interfaz intuitiva con pestañas  
- Formularios, vistas de usuario y administrador  
- Análisis detallado de cada transacción  

---

## 🚀 Funcionalidades Principales

### 👤 **Modo Usuario**
- Registrar nuevas transacciones  
- Visualizar saldos e historial  
- Ver el análisis de riesgo y recomendación del sistema  

### 🛡️ **Modo Administrador**
- Acceso protegido  
- Gestión de usuarios y transacciones  
- Visualización detallada de cada evaluación  
- Retroalimentación manual sobre transacciones  

---

## 🌎 Impacto Social y Beneficios
- Incrementa la seguridad y confianza en compras digitales  
- Reduce pérdidas económicas por fraude  
- Ofrece explicaciones claras y transparentes  
- Mejora la experiencia del usuario frente a transacciones sospechosas  

---

## 📁 Estructura del Proyecto

```
CodeScore/
├── SecuredCard_IA.py
├── backend_fraude.py
├──README.md
└── Data/
    ├── modelo_xgb_fraude.pkl
    ├── modelo_isoforest_paysim_optimo.pkl
    ├── logo1.png
    ├── usuarios.csv
    └── transacciones.csv
```

---

## 🛠️ Instalación y Ejecución

### 1. Clonar el repositorio
git clone https://github.com/sadhub10/SIC-2025-Aulas-Pa09-y-Pa10.git

### 2. Instalar dependencias
pip install -r requirements.txt

### 3. Ejecutar
python SecuredCard_IA.py

---

## 👥 Equipo de Desarrollo – CodeScore
```
| Nombre          | Rol                                    |
| --------------- | -------------------------------------- |
| Adriel Pérez    | Coordinador + Entrenamiento de Modelos |
| Ernesto Yee     | Backend + Documentación                |
| Sharon Correa   | Frontend Flet                          |
| Edgard González | Documentación + QA                     |
---
