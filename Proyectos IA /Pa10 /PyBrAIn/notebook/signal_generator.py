import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
import csv
import random

# ======================================================================
# CONFIG GLOBAL PARA DATASET
# ======================================================================

# Símbolos que se usarán para cada imagen del dataset (para que se vea bien la onda)
VIS_SYMBOLS_DATASET = 16

# ======================================================================
# 1. CLASE GENERADORA (CANAL DISPERSIVO ALEATORIO + AWGN)
# ======================================================================

class SignalGenerator:
    def __init__(self,
                 samples_per_symbol: int = 16,
                 num_symbols: int = 100,
                 symbol_rate: float = 1000.0,
                 seed: int | None = None):
        self.samples_per_symbol = int(samples_per_symbol)
        self.num_symbols = int(num_symbols)
        self.symbol_rate = float(symbol_rate)
        self.fs = self.symbol_rate * self.samples_per_symbol
        # RNG común para bits, canal e ISI
        self.rng = np.random.default_rng(seed)

    # --------------------------------------------------
    # Bits → símbolos (decimal)
    # --------------------------------------------------
    def _get_bits(self, M):
        bps = int(np.log2(M))
        bits = self.rng.integers(0, 2, self.num_symbols * bps)
        bits_reshaped = bits.reshape(-1, bps)
        powers = 1 << np.arange(bps)[::-1]
        symbols = bits_reshaped @ powers   # 0..M-1
        return bits, symbols, bps

    # --------------------------------------------------
    # Baseband/analítico → pasabanda real
    # --------------------------------------------------
    def _to_passband(self, x_bb: np.ndarray, modulation_name: str, Nc: int = 2):
        """
        Convierte una señal compleja de banda base (analítica) a pasabanda real.
        Para ASK se usa un seno puro; para PSK/QAM/FSK se usa mezcla I/Q con cos/sin.
        """
        mod = modulation_name.upper()
        num_samples = len(x_bb)
        t = np.arange(num_samples) / self.fs

        # Frecuencia de la portadora: Nc ciclos por símbolo
        cycles_per_symbol = Nc
        fc = cycles_per_symbol * self.fs / self.samples_per_symbol  # = Nc * Rs

        # Caso especial ASK: amplitud real * seno
        if "ASK" in mod:
            amp = x_bb.real.astype(np.float64)  # niveles 0..M-1
            s_pass = amp * np.sin(2 * np.pi * fc * t)
            return s_pass.astype(np.float64)

        # Resto (PSK/QAM/FSK): representación I/Q estándar
        carrier_cos = np.cos(2 * np.pi * fc * t)
        carrier_sin = np.sin(2 * np.pi * fc * t)

        I = x_bb.real
        Q = x_bb.imag
        s_pass = I * carrier_cos - Q * carrier_sin
        return s_pass.astype(np.float64)

    # --------------------------------------------------
    # Canal: ISI "borroso" ALEATORIO + AWGN
    # --------------------------------------------------
    def _apply_channel(self, tx_signal, snr_db, isi_severity):
        rx = tx_signal.astype(np.complex128)

        # 1) ISI (blur temporal aleatorio)
        if isi_severity is not None and isi_severity > 0:
            s = float(np.clip(isi_severity, 0.0, 1.0))

            VIS_ISI_FACTOR = 1.5
            alpha = 1.0 - (1.0 - s) ** VIS_ISI_FACTOR  # 0..1

            L_min, L_max = 5, 61
            L = int(L_min + alpha * (L_max - L_min))
            if L % 2 == 0:
                L += 1

            n = np.arange(L)
            center = (L - 1) / 2
            sigma = L / 5.0

            gauss = np.exp(-0.5 * ((n - center) / sigma) ** 2)
            gauss = gauss / np.sum(gauss)

            phase = np.exp(1j * 2 * np.pi * self.rng.random(L))

            h_base = gauss * phase
            h_base = h_base / np.sqrt(np.sum(np.abs(h_base) ** 2))

            delta = np.zeros(L, dtype=np.complex128)
            delta[int(center)] = 1.0 + 0j

            h = (1.0 - alpha) * delta + alpha * h_base
            h = h / np.sqrt(np.sum(np.abs(h) ** 2))

            rx = np.convolve(rx, h, mode="same")

        # 2) Ruido AWGN complejo
        if snr_db is not None:
            # Ahora usamos el SNR "real" que le pasas (sin escalar)
            eff_snr = max(float(snr_db), 0.0)
            sig_pwr = np.mean(np.abs(rx) ** 2)

            if eff_snr == 0:
                noise_pwr = sig_pwr
            else:
                noise_pwr = sig_pwr / (10 ** (eff_snr / 10.0))

            noise = np.sqrt(noise_pwr / 2) * (
                self.rng.standard_normal(len(rx))
                + 1j * self.rng.standard_normal(len(rx))
            )
            rx = rx + noise

        return rx

    # --------------------------------------------------
    # MODULACIONES
    # --------------------------------------------------

    def generate_ask(self, M, snr_db, isi):
        """
        ASK (incluye OOK):
        - Niveles de amplitud: 0, 1, 2, ..., M-1  (sin normalizar).
        - La portadora TX tendrá amplitud pico = M-1.
        """
        bits, symbols, bps = self._get_bits(M)

        # Niveles 0..M-1 directamente (voltajes)
        levels = np.arange(M, dtype=float)  # 0,1,...,M-1

        amp_syms = levels[symbols]               # amplitud por símbolo
        iq_syms = amp_syms.astype(np.complex128) # constelación 1D en el eje real

        # Oversampling (pulso rectangular por símbolo)
        tx_bb = np.repeat(iq_syms, self.samples_per_symbol)

        # Canal complejo (ISI + AWGN)
        rx_bb = self._apply_channel(tx_bb, snr_db, isi)

        # Pasar a pasabanda real (senoidal)
        tx_pb = self._to_passband(tx_bb, "ASK")
        rx_pb = self._to_passband(rx_bb, "ASK")

        return tx_pb, rx_pb, bits, symbols, iq_syms, tx_bb, rx_bb

    def generate_psk(self, M, snr_db, isi):
        bits, symbols, bps = self._get_bits(M)

        if M == 2:
            # BPSK en eje imaginario (±j)
            bpsk_q = np.where(symbols == 0, 1.0, -1.0)
            iq_syms = 1j * bpsk_q.astype(np.complex128)
        else:
            if M == 4:
                # Tabla QPSK
                phase_deg_lut = np.array([-135.0, -45.0, 135.0, 45.0])
                phases = np.deg2rad(phase_deg_lut)
            elif M == 8:
                # Tabla 8-PSK
                phase_deg_lut = np.array([
                    -112.5, -157.5, -67.5, -22.5,
                    112.5,  157.5,  67.5,  22.5
                ])
                phases = np.deg2rad(phase_deg_lut)
            else:
                phases = 2 * np.pi * np.arange(M) / M

            iq_syms = np.exp(1j * phases[symbols])

        tx_bb = np.repeat(iq_syms, self.samples_per_symbol)
        rx_bb = self._apply_channel(tx_bb, snr_db, isi)

        tx_pb = self._to_passband(tx_bb, "PSK")
        rx_pb = self._to_passband(rx_bb, "PSK")

        return tx_pb, rx_pb, bits, symbols, iq_syms, tx_bb, rx_bb

    def generate_qam(self, M, snr_db, isi):
        """
        QAM:
        - Para M=8: LUT 8-QAM (2 amplitudes, 4 fases) tipo la figura.
        - Para M=16,64,256,...: QAM cuadrada estándar normalizada.
        """
        bits, symbols, bps = self._get_bits(M)

        if M == 8:
            # 8-QAM: 2 radios, 4 fases (puntos sobre ejes)
            r_inner = 1.0
            r_outer = 2.0

            const = np.array([
                r_inner + 0j,          # 0 -> 000
                r_outer + 0j,          # 1 -> 001
                0.0 + 1j * r_inner,    # 2 -> 010
                0.0 + 1j * r_outer,    # 3 -> 011
                -r_inner + 0j,         # 4 -> 100
                -r_outer + 0j,         # 5 -> 101
                0.0 - 1j * r_inner,    # 6 -> 110
                0.0 - 1j * r_outer     # 7 -> 111
            ], dtype=np.complex128)
        else:
            # QAM cuadrada (M = 4, 16, 64, 256, ...)
            sqrt_M = int(np.sqrt(M))
            if sqrt_M * sqrt_M != M:
                raise ValueError(f"M={M} no es cuadrado perfecto para QAM cuadrada")
            r = 2 * np.arange(sqrt_M) - (sqrt_M - 1)   # -3,-1,1,3,...
            I, Q = np.meshgrid(r, r)
            const = (I + 1j * Q).flatten().astype(np.complex128)

        # Normalización de energía promedio a 1
        const /= np.sqrt(np.mean(np.abs(const) ** 2))

        iq_syms = const[symbols]
        tx_bb = np.repeat(iq_syms, self.samples_per_symbol)
        rx_bb = self._apply_channel(tx_bb, snr_db, isi)

        tx_pb = self._to_passband(tx_bb, "QAM")
        rx_pb = self._to_passband(rx_bb, "QAM")

        return tx_pb, rx_pb, bits, symbols, iq_syms, tx_bb, rx_bb

    def generate_fsk(self, M, snr_db, isi):
        """
        M-FSK “clásico” multinivel con FASE CONTINUA (CPFSK).

        - M frecuencias equiespaciadas alrededor de una portadora fc.
        - El diseño del span alrededor de fc es el MISMO que ya tenías
          (por eso el espectro se mantiene donde estaba).
        - FSK de amplitud constante: |tx_bb[n]| = 1 para todo n.
        """
        # 1) Bits → símbolos 0..M-1
        bits, symbols, bps = self._get_bits(M)

        Rs  = self.symbol_rate
        sps = self.samples_per_symbol
        fs  = self.fs          # = Rs * sps
        dt  = 1.0 / fs

        # 2) Portadora central FSK (misma que usa _to_passband)
        Nc_fsk = 8             # ciclos de portadora por símbolo
        fc = Nc_fsk * Rs       # fc = Nc * Rs

        nyq = fs / 2.0         # frecuencia de Nyquist

        # 3) Rango "seguro" alrededor de fc donde meter TODAS las M frecuencias
        margin   = 0.05 * nyq
        span_max = min(fc - margin,        # no bajar demasiado hacia 0 Hz
                       nyq - fc - margin)  # no subir demasiado hacia Nyquist
        if span_max <= 0:
            # Por si algún día cambias Rs/sps a algo muy raro
            span_max = 0.4 * nyq

        # Usamos el 80 % de ese rango para dejar margen en los bordes
        span = 0.8 * span_max

        # 4) M offsets de frecuencia equiespaciados entre -span y +span
        #    → M tonos distintos alrededor de fc.
        if M == 1:
            offsets = np.array([0.0], dtype=float)
        else:
            offsets = np.linspace(-span, span, M, dtype=float)

        # Frecuencia (offset respecto a fc) asociada a cada símbolo
        freq_offset_syms = offsets[symbols]          # shape: (num_symbols,)
        freq_offset_up   = np.repeat(freq_offset_syms, sps)

        # 5) CPFSK: fase continua = integral discreta de la frecuencia
        #    φ[n] = φ[n-1] + 2π Δf[n]·dt
        phi0 = 2.0 * np.pi * self.rng.random()
        phase_bb = phi0 + 2.0 * np.pi * np.cumsum(freq_offset_up) * dt
        tx_bb = np.exp(1j * phase_bb)   # |tx_bb| = 1 → amplitud constante

        # 6) Canal complejo (ISI + AWGN)
        rx_bb = self._apply_channel(tx_bb, snr_db, isi)

        # 7) Conversión a pasabanda real usando la misma fc (Nc_fsk)
        tx_pb = self._to_passband(tx_bb, "FSK", Nc=Nc_fsk)
        rx_pb = self._to_passband(rx_bb, "FSK", Nc=Nc_fsk)

        # Para FSK no usamos constelación I/Q
        iq_syms = None

        return tx_pb, rx_pb, bits, symbols, iq_syms, tx_bb, rx_bb

# ======================================================================
# 2. FUNCIÓN DE VISUALIZACIÓN (para debug/clase, NO para dataset)
# ======================================================================

def plot_modulation_analysis(name, tx_pb, rx_pb,
                             bits, symbols, M, fs, sps,
                             rx_complex=None, tx_complex=None,
                             ideal_syms=None):
    # Aquí va tu función completa original si la usas.
    # No la repito para no hacer esto kilométrico.
    pass

# ======================================================================
# 3. CONFIGURACIÓN DE SÍMBOLOS (utility)
# ======================================================================

def symbols_for_M(M, base_factor=20, min_syms=40):
    """
    El número de símbolos se ajusta automáticamente según M:
    num_symbols = max(min_syms, base_factor * M)
    """
    return max(min_syms, base_factor * M)

# ======================================================================
# 4. HELPERS PARA GENERACIÓN DE DATASET (CNN)
# ======================================================================

def _snr_range_for_M(M: int):
    """Rangos base de SNR según M (compartidos por sampler y categorizador)."""
    if M <= 8:
        snr_min, snr_max = 0.0, 30.0
    elif M == 16:
        snr_min, snr_max = 5.0, 30.0
    elif M == 32:
        snr_min, snr_max = 10.0, 30.0
    else:  # M >= 64
        snr_min, snr_max = 15.0, 30.0
    span = snr_max - snr_min
    easy_min = snr_min + 0.6 * span
    mid_min  = snr_min + 0.3 * span
    return snr_min, snr_max, mid_min, easy_min


def snr_band_for_M(M: int, snr_db: float) -> str:
    """
    Clasifica un valor de SNR en BAJO / MEDIO / ALTO
    usando los mismos cortes que el sampler.
    """
    snr_min, snr_max, mid_min, easy_min = _snr_range_for_M(M)
    if snr_db < mid_min:
        return "BAJO"
    elif snr_db < easy_min:
        return "MEDIO"
    else:
        return "ALTO"


def snr_interval_for_band(M: int, band: str):
    """
    Devuelve (snr_low, snr_high) para una banda dada: BAJO / MEDIO / ALTO,
    garantizando que snr_band_for_M(M, snr_db) dé exactamente esa banda.
    """
    band = band.upper()
    snr_min, snr_max, mid_min, easy_min = _snr_range_for_M(M)
    eps = 1e-6

    if band == "BAJO":
        low = snr_min
        high = mid_min - eps       # para que nunca salte a MEDIO
    elif band == "MEDIO":
        low = mid_min
        high = easy_min - eps      # para que nunca salte a ALTO
    elif band == "ALTO":
        low = easy_min
        high = snr_max
    else:
        raise ValueError(f"Banda SNR desconocida: {band}")

    return low, high


def isi_limits_for_M(M: int):
    """
    Devuelve (isi_min, isi_max) usando la misma lógica de antes.
    """
    if M <= 8:
        isi_min, isi_max = 0.0, 1.0
    elif M == 16:
        isi_min, isi_max = 0.0, 0.8
    elif M == 32:
        isi_min, isi_max = 0.0, 0.6
    else:  # M >= 64
        isi_min, isi_max = 0.0, 0.5
    return isi_min, isi_max


def isi_levels_for_M(M: int, n_levels: int = 5):
    """
    Genera una lista de niveles de ISI *deterministas* entre el mínimo y máximo
    permitido para ese M. Se cuantifican a 2 decimales para que coincidan con
    los nombres de carpeta (ISI 0.00, ISI 0.25, etc.).
    """
    isi_min, isi_max = isi_limits_for_M(M)
    if n_levels <= 1:
        return [float(f"{isi_min:.2f}")]
    levels = [
        isi_min + (isi_max - isi_min) * k / (n_levels - 1)
        for k in range(n_levels)
    ]
    levels = [float(f"{x:.2f}") for x in levels]
    return levels


def generate_signal_once(modulation: str,
                         M: int,
                         snr_db: float,
                         isi: float,
                         num_symbols: int,
                         samples_per_symbol: int,
                         symbol_rate: float,
                         seed: int):
    """
    Genera UNA realización de señal pasabanda TX/RX para la modulación indicada.
    Devuelve:
      tx_pb, rx_pb, fs, sps, bits, symbols, iq_syms, tx_bb, rx_bb
    """
    modulation = modulation.upper()
    gen = SignalGenerator(samples_per_symbol=samples_per_symbol,
                          num_symbols=num_symbols,
                          symbol_rate=symbol_rate,
                          seed=seed)

    if modulation == "ASK":
        tx_pb, rx_pb, bits, symbols, iq_syms, tx_bb, rx_bb = gen.generate_ask(M, snr_db, isi)
    elif modulation == "PSK":
        tx_pb, rx_pb, bits, symbols, iq_syms, tx_bb, rx_bb = gen.generate_psk(M, snr_db, isi)
    elif modulation == "QAM":
        tx_pb, rx_pb, bits, symbols, iq_syms, tx_bb, rx_bb = gen.generate_qam(M, snr_db, isi)
    elif modulation == "FSK":
        tx_pb, rx_pb, bits, symbols, iq_syms, tx_bb, rx_bb = gen.generate_fsk(M, snr_db, isi)
    else:
        raise ValueError(f"Modulación desconocida: {modulation}")

    return tx_pb, rx_pb, gen.fs, gen.samples_per_symbol, bits, symbols, iq_syms, tx_bb, rx_bb


def save_cnn_image(modulation: str,
                   M: int,
                   tx_pb: np.ndarray,
                   rx_pb: np.ndarray,
                   fs: float,
                   sps: int,
                   bits,
                   symbols,
                   iq_syms,
                   tx_bb,
                   rx_bb,
                   out_path: str,
                   vis_symbols: int | None = None):
    """
    Genera la imagen que verá la CNN.

    - Para ASK / PSK / QAM:
        * Subplot 1: waveform RX en el tiempo (segmento, normalizada).
        * Subplot 2: diagrama de constelación RX:
              - puntos recibidos
              - puntos ideales (+) alineados
              - ejes cruzados en (0,0) como referencia
        * Subplot 3: espectro de potencia (|FFT| normalizado) de RX pasabanda.

    - Para FSK:
        * Subplot 1: waveform RX en el tiempo (segmento, normalizada).
        * Subplot 2: espectro de potencia de RX pasabanda.

    Todas las imágenes se generan con la misma resolución (figsize, dpi).
    """
    if vis_symbols is None:
        vis_symbols = VIS_SYMBOLS_DATASET

    mod = modulation.upper()

    # ---------- Helper interno para PSD ----------
    def _prepare_psd(sig, fs, NFFT: int = 2048):
        sig = np.asarray(sig, dtype=float)
        if len(sig) < NFFT:
            x = np.pad(sig, (0, NFFT - len(sig)))
        else:
            x = sig[:NFFT]
        window = np.hanning(len(x))
        xw = x * window
        F = np.fft.rfft(xw, NFFT)
        mag = np.abs(F)
        mag /= (np.max(mag) + 1e-12)  # normalizar 0..1
        return mag

    # =========================================================
    # ASK / PSK / QAM → waveform + constelación + PSD
    # =========================================================
    if mod in ("ASK", "PSK", "QAM"):
        # 1) Waveform RX (segmento)
        total_samples = min(len(rx_pb), vis_symbols * sps)
        rx_seg = rx_pb[:total_samples]
        max_abs_w = np.max(np.abs(rx_seg)) + 1e-12
        rx_seg = rx_seg / max_abs_w
        n = np.arange(total_samples)

        # 2) Constelación a partir de RX_BB
        offset = sps // 2
        sampled_rx = np.array(rx_bb[offset::sps], dtype=np.complex128)
        if sampled_rx.size == 0:
            sampled_rx = rx_bb.astype(np.complex128)

        # Rotar BPSK para dejarla horizontal
        if mod == "PSK" and M == 2:
            sampled_rx = sampled_rx * (-1j)
            iq_syms_plot = iq_syms * (-1j) if iq_syms is not None else None
        else:
            iq_syms_plot = iq_syms

        x = sampled_rx.real
        y = sampled_rx.imag

        # puntos ideales alineados
        if iq_syms_plot is not None:
            ideal = np.array(iq_syms_plot[:len(sampled_rx)], dtype=np.complex128)
            x_ideal = ideal.real
            y_ideal = ideal.imag
            all_vals = np.concatenate([x, y, x_ideal, y_ideal])
        else:
            x_ideal = None
            y_ideal = None
            all_vals = np.concatenate([x, y])

        max_abs_c = np.max(np.abs(all_vals)) + 1e-12
        x /= max_abs_c
        y /= max_abs_c
        if x_ideal is not None:
            x_ideal /= max_abs_c
            y_ideal /= max_abs_c

        # 3) PSD de RX pasabanda (usamos el mismo segmento)
        psd = _prepare_psd(rx_seg, fs)
        k_psd = np.arange(len(psd))

        # 4) Figura: 3 subplots
        fig, (ax1, ax2, ax3) = plt.subplots(
            3, 1, figsize=(12, 12), dpi=100,
            gridspec_kw={"height_ratios": [1, 1, 1]}
        )

        # --- Subplot 1: waveform ---
        ax1.plot(n, rx_seg, linewidth=1.0)
        ax1.axis("off")
        ax1.margins(x=0)

        # --- Subplot 2: constelación ---
        ax2.scatter(x, y, s=8, alpha=0.8)          # recibidos
        if x_ideal is not None:
            ax2.scatter(x_ideal, y_ideal, s=40, marker="+", linewidths=1.5)
        ax2.axhline(0.0, color="0.6", linewidth=0.8)
        ax2.axvline(0.0, color="0.6", linewidth=0.8)
        ax2.set_xlim(-1.1, 1.1)
        ax2.set_ylim(-1.1, 1.1)
        ax2.axis("off")
        ax2.margins(x=0, y=0)

        # --- Subplot 3: PSD ---
        ax3.plot(k_psd, psd, linewidth=1.0)
        ax3.axis("off")
        ax3.margins(x=0)

        plt.tight_layout(pad=0.0)
        fig.savefig(out_path, bbox_inches="tight", pad_inches=0.0)
        plt.close(fig)

    # =========================================================
    # FSK → waveform + PSD
    # =========================================================
    else:
        total_samples = min(len(rx_pb), vis_symbols * sps)
        rx_seg = rx_pb[:total_samples]

        max_abs = np.max(np.abs(rx_seg)) + 1e-12
        rx_seg = rx_seg / max_abs
        n = np.arange(total_samples)

        psd = _prepare_psd(rx_seg, fs)
        k_psd = np.arange(len(psd))

        fig, (ax1, ax2) = plt.subplots(
            2, 1, figsize=(12, 12), dpi=100,
            gridspec_kw={"height_ratios": [1, 1]}
        )

        # --- Subplot 1: waveform ---
        ax1.plot(n, rx_seg, linewidth=1.0)
        ax1.axis("off")
        ax1.margins(x=0)

        # --- Subplot 2: PSD ---
        ax2.plot(k_psd, psd, linewidth=1.0)
        ax2.axis("off")
        ax2.margins(x=0)

        plt.tight_layout(pad=0.0)
        fig.savefig(out_path, bbox_inches="tight", pad_inches=0.0)
        plt.close(fig)


def sample_snr_for_M(M: int) -> float:
    """
    Versión aleatoria clásica (ya no se usa en el main, pero la dejo
    por si quieres hacer pruebas fuera del barrido determinista).
    """
    snr_min, snr_max, mid_min, easy_min = _snr_range_for_M(M)

    u = random.random()
    if u < 0.6:
        # zona fácil (SNR alto)
        return random.uniform(easy_min, snr_max)
    elif u < 0.9:
        # zona media
        return random.uniform(mid_min, easy_min)
    else:
        # zona difícil (SNR bajo dentro del rango permitido)
        return random.uniform(snr_min, mid_min)


def sample_isi_for_M(M: int) -> float:
    """
    Versión aleatoria clásica (ya no se usa en el main, pero la dejo
    por si quieres hacer pruebas fuera del barrido determinista).
    """
    isi_min, isi_max = isi_limits_for_M(M)
    span = isi_max - isi_min
    low_max  = isi_min + 0.3 * span
    mid_max  = isi_min + 0.6 * span

    u = random.random()
    if u < 0.6:
        # ISI bajo
        return random.uniform(isi_min, low_max)
    elif u < 0.9:
        # ISI medio
        return random.uniform(low_max, mid_max)
    else:
        # ISI alto dentro del máximo permitido
        return random.uniform(mid_max, isi_max)


def generate_one_sample(root_dir: str,
                        split: str,
                        modulation: str,
                        M: int,
                        snr_db: float,
                        isi: float,
                        csv_writer=None,
                        symbol_rate: float = 1000.0,
                        samples_per_symbol: int = 32,
                        num_symbols: int | None = None):
    """
    Genera UNA imagen y la guarda en:

      root_dir/images/SPLIT/CLASE/ISI xx.xx/SNR BAJO|MEDIO|ALTO/archivo.png

    Ejemplo de estructura:
      D:\\Dataseetes\\images\\train\\ASK_2\\ISI 0.00\\SNR BAJO\\
           ASK_2_snr25.3_isi0.00_seedXXXXX.png
    """
    modulation = modulation.upper()
    # Nombre de clase tipo "ASK_2", "PSK_8", etc.
    class_name = f"{modulation}_{M}"

    # ----- Etiquetas legibles para subcarpetas de ISI y SNR -----
    isi_tag = f"ISI {isi:.2f}"            # p.ej. "ISI 0.00"
    snr_band = snr_band_for_M(M, snr_db)  # "BAJO", "MEDIO" o "ALTO"
    snr_tag = f"SNR {snr_band}"           # p.ej. "SNR BAJO"

    # Carpeta final:
    # images / split / CLASE / ISI xx.xx / SNR XXX /
    img_dir = os.path.join(
        root_dir,
        "images",
        split,
        class_name,
        isi_tag,
        snr_tag
    )
    os.makedirs(img_dir, exist_ok=True)

    if num_symbols is None:
        # Ajuste simple: más símbolos para M grandes
        num_symbols = symbols_for_M(M, base_factor=5, min_syms=80)

    # Seed aleatoria
    seed = random.randint(0, 2**31 - 1)

    (
        tx_pb,
        rx_pb,
        fs,
        sps,
        bits,
        symbols,
        iq_syms,
        tx_bb,
        rx_bb
    ) = generate_signal_once(
        modulation=modulation,
        M=M,
        snr_db=snr_db,
        isi=isi,
        num_symbols=num_symbols,
        samples_per_symbol=samples_per_symbol,
        symbol_rate=symbol_rate,
        seed=seed
    )

    filename = f"{class_name}_snr{snr_db:.1f}_isi{isi:.2f}_seed{seed}.png"
    out_path = os.path.join(img_dir, filename)

    # Guardar imagen (constelación/waveform/PSD) usando RX
    save_cnn_image(
        modulation,
        M,
        tx_pb,
        rx_pb,
        fs,
        sps,
        bits,
        symbols,
        iq_syms,
        tx_bb,
        rx_bb,
        out_path
    )

    # Guardar metadata si hay writer
    if csv_writer is not None:
        # Ruta relativa incluyendo split, CLASE, ISI y SNR
        rel_path = os.path.join(
            "images",
            split,
            class_name,
            isi_tag,
            snr_tag,
            filename
        )
        csv_writer.writerow([rel_path, class_name, modulation, M, snr_db, isi, seed])

# ======================================================================
# 5. MAIN PARA GENERAR DATASET (BARRIDO DETERMINISTA ISI × SNR)
# ======================================================================

if __name__ == "__main__":
    # ====== CONFIGURA AQUÍ LA RUTA DEL DATASET ======
    # Por ejemplo en tu USB:
    # ROOT_DIR = r"E:\Astrid_CNN_Modulations\dataset_v1"
    ROOT_DIR = r"D:\Dataseetes"

    # Lista de clases: modulación + M
    # Nota: se quita QAM_32 porque generate_qam no soporta 32-QAM cuadrada.
    CLASSES = [
        ("ASK", 8), ("ASK", 16), ("ASK", 32), ("ASK", 64),
        ("PSK", 2), ("PSK", 4), ("PSK", 8), ("PSK", 16), ("PSK", 32), ("PSK", 64),
        ("QAM", 4), ("QAM", 8), ("QAM", 16), ("QAM", 64),
        ("FSK", 2), ("FSK", 4), ("FSK", 8), ("FSK", 16), ("FSK", 32), ("FSK", 64),
    ]

    # Barrido determinista:
    # - número de niveles de ISI (entre el min y max permitido por M)
    N_ISI_LEVELS = 5
    # - bandas de SNR
    SNR_BANDS = ["BAJO", "MEDIO", "ALTO"]

    # Imágenes por combinación (mod, M, ISI, banda SNR)
    IMGS_PER_COMBO_TRAIN = 100
    IMGS_PER_COMBO_VAL   = 20
    IMGS_PER_COMBO_TEST  = 20

    # Crear carpeta de metadata
    meta_dir = os.path.join(ROOT_DIR, "metadata")
    os.makedirs(meta_dir, exist_ok=True)
    meta_path = os.path.join(meta_dir, "metadata.csv")

    with open(meta_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["filepath", "class", "modulation", "M", "snr_db", "isi", "seed"])

        for modulation, M in CLASSES:
            class_name = f"{modulation}_{M}"
            print(f"Generando clase {class_name} ...")

            # Niveles deterministas de ISI para este M
            isi_values = isi_levels_for_M(M, n_levels=N_ISI_LEVELS)

            # ---------- TRAIN ----------
            split = "train"
            for isi in isi_values:
                for band in SNR_BANDS:
                    snr_low, snr_high = snr_interval_for_band(M, band)
                    for i in range(IMGS_PER_COMBO_TRAIN):
                        snr_db = random.uniform(snr_low, snr_high)
                        generate_one_sample(ROOT_DIR, split, modulation, M, snr_db, isi,
                                            csv_writer=writer)

            # ---------- VAL ----------
            split = "val"
            for isi in isi_values:
                for band in SNR_BANDS:
                    snr_low, snr_high = snr_interval_for_band(M, band)
                    for i in range(IMGS_PER_COMBO_VAL):
                        snr_db = random.uniform(snr_low, snr_high)
                        generate_one_sample(ROOT_DIR, split, modulation, M, snr_db, isi,
                                            csv_writer=writer)

            # ---------- TEST ----------
            split = "test"
            for isi in isi_values:
                for band in SNR_BANDS:
                    snr_low, snr_high = snr_interval_for_band(M, band)
                    for i in range(IMGS_PER_COMBO_TEST):
                        snr_db = random.uniform(snr_low, snr_high)
                        generate_one_sample(ROOT_DIR, split, modulation, M, snr_db, isi,
                                            csv_writer=writer)

    print("¡Dataset generado con waveform + constelaciones (ASK/PSK/QAM) + espectro, "
          "y waveform + espectro para FSK, usando RX con ruido!")
