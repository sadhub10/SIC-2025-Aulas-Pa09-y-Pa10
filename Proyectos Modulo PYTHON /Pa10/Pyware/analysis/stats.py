
import pandas as pd
from scipy.stats import ttest_ind

def procesar_dataframe(df):
    """
    Limpia y calcula:
    - Variables numéricas
    - Marcador de clima adverso
    - Puntajes de sueño, dieta, estado de ánimo
    - ISA (promedio de síntomas)
    - Matriz de correlación
    - Correlación Sueño(T-1) vs Fatiga(T)
    - t-test: dolor en clima adverso vs normal
    """
    try:
        columnas_num = [
            'rigidez_score', 'dolor_score', 'inflamacion_score',
            'fatiga_score', 'actividad_fisica', 'temperatura_C'
        ]
        for c in columnas_num:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce')

        df.dropna(subset=[c for c in columnas_num if c in df.columns], inplace=True)
        if df.empty:
            return None

        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')

        # Clima adverso
        if 'clima' in df.columns:
            df['clima_adverso'] = ((df['clima'] == 'Lluvioso') | (df['clima'] == 'Húmedo')).astype(int)
        else:
            df['clima_adverso'] = 0

        # Sueño a número
        mapa_sueno = {'Horrible': 1, 'Malo': 2, 'Ok': 3, 'Bueno': 4, 'Excelente': 5}
        if 'sueño' in df.columns:
            df['sueno_score'] = df['sueño'].map(mapa_sueno)

        # Dieta a número
        mapa_dieta = {'Inflamatoria': 0, 'Balanceada': 1, 'Antiinflamatoria': 2}
        if 'dieta_tipo' in df.columns:
            df['dieta_score'] = df['dieta_tipo'].map(mapa_dieta)

        # Estado de ánimo a número 
        if 'estado_animo_score' not in df.columns:
            mapa_animo = {
                'Triste': 1, 'Frustrado': 1, 'Irritable': 2, 'Ansioso': 2,
                'Estresado': 3, 'Neutral': 3, 'Tranquilo': 4, 'Optimista': 5, 'Feliz': 5
            }
            if 'estado_animo' in df.columns:
                df['estado_animo_score'] = df['estado_animo'].map(mapa_animo).fillna(3)
            else:
                df['estado_animo_score'] = 3

        #promedio de síntomas
        sintomas = ['dolor_score', 'inflamacion_score', 'fatiga_score', 'rigidez_score']
        df['ISA'] = df[sintomas].mean(axis=1)

        columnas_para_corr = [
            'temperatura_C', 'actividad_fisica', 'sueno_score', 'dieta_score',
            'clima_adverso', 'rigidez_score', 'dolor_score',
            'inflamacion_score', 'fatiga_score', 'estado_animo_score', 'ISA'
        ]
        columnas_existentes = [c for c in columnas_para_corr if c in df.columns]
        df_num = df[columnas_existentes]
        matriz = df_num.corr(numeric_only=True)

        # Sueño vs Fatiga
        if 'sueno_score' in df.columns and 'fatiga_score' in df.columns and len(df) > 1:
            sueno_t1 = df['sueno_score'].shift(1).dropna()
            fatiga_t = df['fatiga_score'].iloc[1:]
            corr_sueno_fatiga = sueno_t1.corr(fatiga_t) if not sueno_t1.empty else 0.0
        else:
            corr_sueno_fatiga = 0.0

        # test dolor clima
        if 'dolor_score' in df.columns:
            a = df[df['clima_adverso'] == 1]['dolor_score']
            b = df[df['clima_adverso'] == 0]['dolor_score']
            if len(a) > 1 and len(b) > 1:
                t_stat, p_valor = ttest_ind(a, b, equal_var=False)
            else:
                t_stat, p_valor = 0.0, 1.0
        else:
            t_stat, p_valor = 0.0, 1.0

        info_t = {'t_stat': float(t_stat), 'p_val': float(p_valor)}
        return (df, df_num, matriz, info_t, float(corr_sueno_fatiga))
    except Exception:
        return None

def cargar_y_procesar_csv(ruta_csv):
    try:
        df = pd.read_csv(ruta_csv)
        return procesar_dataframe(df)
    except Exception:
        return None
