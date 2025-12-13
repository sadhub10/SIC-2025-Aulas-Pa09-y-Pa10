import json
from pipelines.imhpa.models import EstacionesModel


WIND_PAYLOAD = r'''
{"estaciones":{"93002":{"latitud":"9.34030","longitud":"-82.24500","nombre":"AEROPUERTO DE BOCAS (93-002)","sensor_valor":"1 m/s","sensor_fecha":"26\/11\/2025 02:00 PM","numero_estacion":"93002","sensor_valor_sin_format":1,"adicionales":[]},"106014":{"latitud":"8.35060","longitud":"-82.51250","nombre":"QUEREVALO 2 (106-014)","sensor_valor":"2.4 m/s","sensor_fecha":"30\/11\/2025 06:00 PM","numero_estacion":"106014","sensor_valor_sin_format":2.4,"adicionales":[]},"108023":{"latitud":"8.39670","longitud":"-82.42830","nombre":"DAVID (108-023)","sensor_valor":"2.9 m/s","sensor_fecha":"30\/11\/2025 07:05 PM","numero_estacion":"108023","sensor_valor_sin_format":2.9,"adicionales":[]}}}
'''

HUM_PAYLOAD = r'''
{"estaciones":{"93002":{"latitud":"9.34030","longitud":"-82.24500","nombre":"AEROPUERTO DE BOCAS (93-002)","sensor_valor":"93.1 %","sensor_fecha":"26\/11\/2025 02:00 PM","numero_estacion":"93002","sensor_valor_sin_format":93.1,"adicionales":[]},"102023":{"latitud":"8.83808","longitud":"-82.75814","nombre":"SANTA CLARA (102-023)","sensor_valor":"100 %","sensor_fecha":"30\/11\/2025 06:00 PM","numero_estacion":"102023","sensor_valor_sin_format":100,"adicionales":[]},"106014":{"latitud":"8.35060","longitud":"-82.51250","nombre":"QUEREVALO 2 (106-014)","sensor_valor":"97.8 %","sensor_fecha":"30\/11\/2025 06:00 PM","numero_estacion":"106014","sensor_valor_sin_format":97.8,"adicionales":[]}}}
'''


def test_wind_value_extraction():
    payload = json.loads(WIND_PAYLOAD)
    m = EstacionesModel.model_validate(payload)

    st = m.estaciones.get("108023")
    assert st is not None
    assert abs(st.sensor_valor_sin_format - 2.9) < 1e-6
    assert isinstance(st.latitud, float)
    assert isinstance(st.longitud, float)


def test_humidity_value_extraction():
    payload = json.loads(HUM_PAYLOAD)
    m = EstacionesModel.model_validate(payload)

    s1 = m.estaciones.get("93002")
    s2 = m.estaciones.get("102023")
    assert s1 is not None and s2 is not None
    assert abs(s1.sensor_valor_sin_format - 93.1) < 1e-6
    assert s2.sensor_valor_sin_format == 100


def test_rain_value_extraction_and_temp():
    # small rainfall payload sample and temperature-like value
    rain_payload = {
        "estaciones": {
            "91029": {"latitud": "8.93030", "longitud": "-82.69000", "nombre": "CHANGUINOLA 2 (91-029)", "sensor_valor": "1 mm", "sensor_fecha": "30/11/2025 18:15", "numero_estacion": "91029", "sensor_valor_sin_format": 1, "adicionales": []},
            "93002": {"latitud": "9.34030", "longitud": "-82.24500", "nombre": "AEROPUERTO DE BOCAS (93-002)", "sensor_valor": "32.5 mm", "sensor_fecha": "26/11/2025 14:30", "numero_estacion": "93002", "sensor_valor_sin_format": 32.5, "adicionales": []}
        }
    }

    m = EstacionesModel.model_validate(rain_payload)
    r1 = m.estaciones.get("91029")
    r2 = m.estaciones.get("93002")
    assert r1 is not None and r2 is not None
    assert abs(r1.sensor_valor_sin_format - 1.0) < 1e-6
    assert abs(r2.sensor_valor_sin_format - 32.5) < 1e-6


def test_invalid_payload_raises():
    # missing keys in one station
    bad = [{"estacion": "x", "valor": 1}]  # missing 'fecha'
    from pipelines.imhpa.parse_imhpa import validate_json

    try:
        validate_json(bad)
    except ValueError as e:
        assert "no contiene" in str(e).lower() or "requeridas" in str(e).lower()
    else:
        raise AssertionError("validate_json should have raised for bad payload")
