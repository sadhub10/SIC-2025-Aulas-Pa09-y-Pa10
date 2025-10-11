# data/simulate.py


import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generar_dataset_simulado(dias=180, semilla=42, guardar_csv=False, ruta_csv=None):
    """
    Genera un dataset clínico realista:
    - Clima de Panamá (estacional)
    - Sueño con memoria (hoy se parece a ayer)
    - Dieta (Inflamatoria, Balanceada, Antiinflamatoria)
    - Actividad física (más probabilidad entre semana)
    - Brotes (sube, se mantiene, baja)
    - Síntomas dependientes y con memoria de un día a otro
    - Estado de ánimo derivado de síntomas y hábitos
    """
    np.random.seed(semilla)

    # Fechas
    fecha_inicio = datetime(2025, 1, 1)
    fechas = [fecha_inicio + timedelta(days=i) for i in range(dias)]

    # Clima de Panamá
    def clima_panama(fecha):
        mes = fecha.month
        if mes in [12, 1, 2, 3]:
            return np.random.choice(['Soleado', 'Seco', 'Ventoso'], p=[0.6, 0.3, 0.1])
        elif mes == 4:
            return np.random.choice(['Soleado', 'Seco', 'Ventoso'], p=[0.5, 0.3, 0.2])
        elif mes in [5, 11]:
            return np.random.choice(['Soleado', 'Nublado', 'Lluvioso', 'Húmedo'], p=[0.3, 0.3, 0.2, 0.2])
        else:
            return np.random.choice(['Lluvioso', 'Nublado', 'Húmedo'], p=[0.5, 0.3, 0.2])

    clima = [clima_panama(f) for f in fechas]
    temperatura = [np.random.uniform(26, 32) for _ in range(dias)]
    clima_adverso = [1 if c in ['Lluvioso', 'Húmedo'] else 0 for c in clima]

    # Actividad física 
    actividad_fisica = []
    for f in fechas:
        if f.weekday() < 5:
            actividad_fisica.append(np.random.choice([0, 1], p=[0.3, 0.7]))
        else:
            actividad_fisica.append(np.random.choice([0, 1], p=[0.6, 0.4]))

    # Sueño con memoria
    opciones_sueno = ['Horrible', 'Malo', 'Ok', 'Bueno', 'Excelente']
    sueno_num = [np.random.choice([2, 3, 4])]
    for _ in range(1, dias):
        ayer = sueno_num[-1]
        hoy = int(np.clip(ayer + np.random.choice([-1, 0, 1], p=[0.2, 0.6, 0.2]), 1, 5))
        sueno_num.append(hoy)
    sueno = [opciones_sueno[s - 1] for s in sueno_num]

    # Dieta
    opciones_dieta = ['Inflamatoria', 'Balanceada', 'Antiinflamatoria']
    dieta_tipo = [np.random.choice(opciones_dieta) for _ in range(dias)]
    dieta_num = [opciones_dieta.index(d) for d in dieta_tipo]  # 0,1,2

    # Brotes (3 a 5 episodios)
    numero_brotes = np.random.randint(3, 6)
    brotes = np.zeros(dias)
    for _ in range(numero_brotes):
        inicio = np.random.randint(0, dias - 14)
        duracion = np.random.randint(3, 15)
        fin = min(inicio + duracion, dias)
        for i in range(inicio, fin):
            pos = (i - inicio) / float(duracion)
            if pos < 0.3:
                brotes[i] = (pos / 0.3) * 2
            elif pos < 0.7:
                brotes[i] = 2 + np.random.uniform(-0.3, 0.3)
            else:
                brotes[i] = 2 * (1 - (pos - 0.7) / 0.3)

    # Síntomas 
    dolor_score, rigidez_score, inflamacion_score, fatiga_score = [], [], [], []
    for i in range(dias):
        # Dolor base
        dolor = 0.5 + brotes[i]
        dolor += clima_adverso[i] * np.random.uniform(0.3, 0.8)

        dolor += (1 - dieta_num[i]) * 0.3

        if actividad_fisica[i] == 1:
            dolor -= np.random.uniform(0, 0.3)
        dolor += (6 - sueno_num[i]) * 0.25
        if i > 0:
            dolor += dolor_score[-1] * 0.3
        dolor += np.random.normal(0, 0.2)
        dolor = int(np.clip(round(dolor), 0, 5))
        dolor_score.append(dolor)

        rigidez = int(np.clip(round(dolor * np.random.uniform(0.7, 1.0) +
                                   brotes[i] * 0.4 +
                                   clima_adverso[i] * np.random.uniform(0.5, 1.0)), 0, 5))
        rigidez_score.append(rigidez)

        inflamacion = int(np.clip(round(
            dolor * 0.6 + (1 - dieta_num[i]) * 0.4 + brotes[i] * 0.5 + np.random.normal(0, 0.3)
        ), 0, 5))
        inflamacion_score.append(inflamacion)

        fatiga = round(dolor * 0.4 + (5 - sueno_num[i]) * 0.7 + brotes[i] * 0.3 + clima_adverso[i] * 0.3)
        if actividad_fisica[i] == 1:
            fatiga -= 0.2
        fatiga = int(np.clip(round(fatiga + np.random.normal(0, 0.2)), 0, 5))
        fatiga_score.append(fatiga)

    # Estado de ánimo
    estado_animo_score, estado_animo = [], []
    for i in range(dias):
        puntaje = 5 - dolor_score[i] * 0.5 - fatiga_score[i] * 0.3
        puntaje += actividad_fisica[i] * 0.4 + (sueno_num[i] - 3) * 0.2
        puntaje += np.random.normal(0, 0.4)
        puntaje = int(np.clip(round(puntaje), 1, 5))
        estado_animo_score.append(puntaje)

        if puntaje <= 2:
            estado_animo.append(np.random.choice(['Triste', 'Frustrado', 'Irritable']))
        elif puntaje == 3:
            estado_animo.append(np.random.choice(['Estresado', 'Ansioso', 'Irritable']))
        else:
            estado_animo.append(np.random.choice(['Tranquilo', 'Optimista', 'Feliz']))

    df = pd.DataFrame({
        'fecha': fechas,
        'clima': clima,
        'temperatura_C': np.round(temperatura, 1),
        'actividad_fisica': actividad_fisica,
        'sueño': sueno,
        'dieta_tipo': dieta_tipo,
        'rigidez_score': rigidez_score,
        'dolor_score': dolor_score,
        'inflamacion_score': inflamacion_score,
        'fatiga_score': fatiga_score,
        'estado_animo': estado_animo,
        'estado_animo_score': estado_animo_score
    })

    if guardar_csv:
        if ruta_csv is None:
            ruta_csv = "dataset_clinico_simulado.csv"
        df.to_csv(ruta_csv, index=False)

    return df
