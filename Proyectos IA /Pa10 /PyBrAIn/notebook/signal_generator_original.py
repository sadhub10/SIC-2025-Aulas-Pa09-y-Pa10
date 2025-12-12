import numpy as np
import matplotlib.pyplot as plt

# ==============================================================================
# 1. CLASE GENERADORA (CANAL DISPERSIVO ALEATORIO + AWGN)
# ==============================================================================

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
            FACTOR_VISUAL = 0.3
            eff_snr = max(snr_db * FACTOR_VISUAL, 0.0)
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
            # QAM cuadrada (M = 16, 64, 256, ...)
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
        - El diseño del span alrededor de fc es el MISMO que el de la versión
          anterior (mismo espectro).
        - FSK de amplitud constante: |tx_bb[n]| = 1.
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
            span_max = 0.4 * nyq

        # Usamos el 80 % de ese rango para dejar margen en los bordes
        span = 0.8 * span_max

        # 4) M offsets de frecuencia equiespaciados entre -span y +span
        if M == 1:
            offsets = np.array([0.0], dtype=float)
        else:
            offsets = np.linspace(-span, span, M, dtype=float)

        # Frecuencia (offset respecto a fc) asociada a cada símbolo
        freq_offset_syms = offsets[symbols]          # shape: (num_symbols,)
        freq_offset_up   = np.repeat(freq_offset_syms, sps)

        # 5) CPFSK: fase continua = integral discreta de la frecuencia
        phi0 = 2.0 * np.pi * self.rng.random()
        phase_bb = phi0 + 2.0 * np.pi * np.cumsum(freq_offset_up) * dt
        tx_bb = np.exp(1j * phase_bb)   # |tx_bb| = 1 → amplitud constante

        # 6) Canal complejo (ISI + AWGN)
        rx_bb = self._apply_channel(tx_bb, snr_db, isi)

        # 7) Conversión a pasabanda real usando la misma fc (Nc_fsk)
        tx_pb = self._to_passband(tx_bb, "FSK", Nc=Nc_fsk)
        rx_pb = self._to_passband(rx_bb, "FSK", Nc=Nc_fsk)

        iq_syms = None
        return tx_pb, rx_pb, bits, symbols, iq_syms, tx_bb, rx_bb


# ==============================================================================
# 2. FUNCIÓN DE VISUALIZACIÓN (bits → símbolos → TX/RX + CONSTELACIÓN/PSD)
# ==============================================================================

def _upsample_for_plot(x, t, factor: int = 8):
    """
    Interpolación bandlimitada para dibujar senoidales suaves.
    No cambia la señal original, solo genera una versión densa para la gráfica.
    """
    x = np.asarray(x, dtype=float)
    N = len(x)
    if factor <= 1 or N < 2:
        return t, x

    # FFT de la señal original
    X = np.fft.fft(x)
    N_up = N * factor
    X_up = np.zeros(N_up, dtype=complex)

    if N % 2 == 0:
        half = N // 2
        X_up[:half] = X[:half]
        X_up[-half:] = X[-half:]
    else:
        half = (N - 1) // 2
        X_up[:half + 1] = X[:half + 1]
        X_up[-half:] = X[-half:]

    # IFFT → señal sobre-muestreada
    y_up = np.fft.ifft(X_up) * factor
    t_up = np.linspace(t[0], t[-1], N_up)

    return t_up, y_up.real


def plot_modulation_analysis(name, tx_pb, rx_pb,
                             bits, symbols, M, fs, sps,
                             rx_complex=None, tx_complex=None,
                             ideal_syms=None):
    # ----------------- Ventana de tiempo -----------------
    total_symbols_avail = min(len(tx_pb), len(rx_pb)) // sps
    vis_symbols = min(12, total_symbols_avail)
    total_samples = vis_symbols * sps

    t = np.arange(total_samples) / fs
    tx_seg = tx_pb[:total_samples]
    rx_seg = rx_pb[:total_samples]

    # Bits por símbolo
    if M > 1:
        bps = int(np.log2(M))
    else:
        bps = 1

    bits_per_symbol = bps
    total_bits_needed = vis_symbols * bits_per_symbol
    bits_seg = bits[:total_bits_needed]

    mod_upper = name.upper()
    is_ask = "ASK" in mod_upper
    is_psk = "PSK" in mod_upper and "FSK" not in mod_upper
    is_qam = "QAM" in mod_upper
    is_fsk = "FSK" in mod_upper

    # =====================================================
    # 1) BIT FLOW (NRZ 0/1) + TEXTO CON LA SECUENCIA
    # =====================================================
    bit_wave = np.zeros(total_samples)
    bit_centers_t = []
    bit_values = []

    for k in range(vis_symbols):
        base = k * sps
        cuts = np.linspace(base, base + sps, bits_per_symbol + 1, dtype=int)
        for j in range(bits_per_symbol):
            start = cuts[j]
            end = cuts[j + 1]
            b_val = bits_seg[k * bits_per_symbol + j]
            bit_wave[start:end] = b_val

            center_sample = 0.5 * (start + end)
            bit_centers_t.append(center_sample / fs)
            bit_values.append(int(b_val))

    # =====================================================
    # 2) SYMBOL / PHASE FLOW
    # =====================================================
    if is_psk:
        if ideal_syms is not None:
            sym_c = np.array(ideal_syms[:vis_symbols], dtype=np.complex128)
        else:
            phases = 2 * np.pi * np.arange(M) / M
            sym_c = np.exp(1j * phases[symbols[:vis_symbols]])
        phase_vals = np.degrees(np.angle(sym_c))
        phase_wave = np.repeat(phase_vals, sps)

    elif is_qam:
        if ideal_syms is not None:
            sym_c = np.array(ideal_syms[:vis_symbols], dtype=np.complex128)
        elif tx_complex is not None:
            sym_c = tx_complex[sps // 2::sps][:vis_symbols]
        else:
            sym_c = np.zeros(vis_symbols, dtype=np.complex128)

        I_vals = sym_c.real
        Q_vals = sym_c.imag
        I_wave = np.repeat(I_vals, sps)
        Q_wave = np.repeat(Q_vals, sps)

    else:
        if ideal_syms is not None:
            sym_vals = np.array(ideal_syms[:vis_symbols])
            if np.iscomplexobj(sym_vals):
                sym_vals = sym_vals.real
        else:
            sym_vals = symbols[:vis_symbols].astype(float)
        sym_wave = np.repeat(sym_vals, sps)

    # =====================================================
    # FIGURA 1: Bits + Símbolos / Fases / I-Q
    # =====================================================
    if is_qam:
        fig1, (ax1, axI, axQ) = plt.subplots(3, 1, sharex=True, figsize=(12, 5))
        axes_fig1 = (ax1, axI, axQ)
    else:
        fig1, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(12, 4))
        axes_fig1 = (ax1, ax2)

    fig1.suptitle(f"{name} – Bit flow y Symbol/Phase flow",
                  fontsize=14, fontweight="bold")

    # -------- Eje 1: Bits --------
    ax1.step(t, bit_wave, where="post", linewidth=1.5)
    ax1.set_ylabel("Bits")
    ax1.set_yticks([])
    ax1.set_ylim(-0.3, 1.5)
    ax1.set_title("Bitstream (secuencia de bits)")

    for tb, b in zip(bit_centers_t, bit_values):
        ax1.text(tb, 1.15, str(b),
                 ha="center", va="bottom", fontsize=8)

    # -------- Ejes de símbolos --------
    if is_psk:
        ax2.step(t, phase_wave, where="post", linewidth=1.5)
        ax2.set_ylabel("Fase [°]")
        phase_unique = np.unique(np.round(phase_vals, 1))
        if len(phase_unique) == 1:
            y_min = phase_unique[0] - 30.0
            y_max = phase_unique[0] + 30.0
        else:
            margin = 15.0
            y_min = phase_unique.min() - margin
            y_max = phase_unique.max() + margin
        ax2.set_ylim(y_min, y_max)
        ax2.set_yticks(phase_unique)
        ax2.set_title("Flujo de fases PSK asignadas a los bits")

    elif is_qam:
        # I
        axI.step(t, I_wave, where="post", linewidth=1.5)
        axI.set_ylabel("Nivel I")

        # Q
        axQ.step(t, Q_wave, where="post", linewidth=1.5)
        axQ.set_ylabel("Nivel Q")
        axQ.set_xlabel("Tiempo [s]")
        axQ.set_title("Flujo de símbolos QAM (componentes I y Q)")

        L = max(np.max(np.abs(I_vals)), np.max(np.abs(Q_vals))) + 1e-12
        ylim = 1.2 * L
        for ax in (axI, axQ):
            ax.set_ylim(-ylim, ylim)
            ax.set_yticks(np.linspace(-ylim, ylim, 5))

    else:
        ax2.step(t, sym_wave, where="post", linewidth=1.5)
        ax2.set_ylabel("Nivel")

        if is_ask:
            y_min, y_max = 0.0, float(M - 1)
            ax2.set_ylim(y_min, y_max)

            if M <= 32:
                ticks = np.arange(0, M, 1)   # 0..M-1
            else:
                max_ticks = 9
                step = max(1, int(np.ceil((M - 1) / (max_ticks - 1))))
                ticks = np.arange(0, M, step)
                if ticks[-1] != M - 1:
                    ticks = np.append(ticks, M - 1)
            ax2.set_yticks(ticks)
        else:
            sym_min = float(np.min(sym_vals))
            sym_max = float(np.max(sym_vals))
            margin = 0.2 * (sym_max - sym_min + 1e-12)
            ax2.set_ylim(sym_min - margin, sym_max + margin)

        ax2.set_title("Flujo de símbolos (niveles asignados a los bits)")

    # Líneas verticales en bordes de símbolo (figura 1)
    for k in range(vis_symbols + 1):
        tk = (k * sps) / fs
        for ax in axes_fig1:
            ax.axvline(tk, linestyle="--", alpha=0.15)

    for ax in axes_fig1:
        ax.grid(True, alpha=0.3)

    fig1.tight_layout(rect=[0, 0.03, 1, 0.95])

    # =====================================================
    # FIGURA 2: TX/RX pasabanda
    # =====================================================
    fig2, (ax3, ax4) = plt.subplots(2, 1, sharex=True, figsize=(12, 4))
    fig2.suptitle(f"{name} – señales pasabanda TX/RX",
                  fontsize=14, fontweight="bold")

    # Versión base (sin upsampling)
    if is_psk or is_qam:
        tx_base = tx_seg.copy()
        rx_base = rx_seg.copy()
        for k in range(1, vis_symbols):
            idx = k * sps
            if idx < len(tx_base):
                tx_base[idx] = np.nan
            if idx < len(rx_base):
                rx_base[idx] = np.nan
    else:
        tx_base = tx_seg
        rx_base = rx_seg

    # Para FSK: suavizamos solo para la gráfica
    if is_fsk:
        t_plot, tx_plot = _upsample_for_plot(tx_base, t, factor=8)
        _,      rx_plot = _upsample_for_plot(rx_base, t, factor=8)
    else:
        t_plot = t
        tx_plot = tx_base
        rx_plot = rx_base

    # -------- Eje 3: TX pasabanda --------
    ax3.plot(t_plot, tx_plot, linewidth=1.5, label="TX pasabanda")
    ax3.set_ylabel("Amplitud")
    ax3.set_title("Señal modulada TX (pasabanda, antes del canal)")

    # -------- Eje 4: RX pasabanda --------
    ax4.plot(t_plot, rx_plot, linewidth=1.0, linestyle="--", label="RX pasabanda")
    ax4.set_ylabel("Amplitud")
    ax4.set_xlabel("Tiempo [s]")
    ax4.set_title("Señal recibida RX (después del canal, pasabanda)")

    if is_ask:
        amp_lim = float(M - 1)
        if amp_lim <= 0:
            maxy = max(np.max(np.abs(tx_seg)), np.max(np.abs(rx_seg))) + 1e-12
            amp_lim = 1.2 * maxy
        ax3.set_ylim(-amp_lim, amp_lim)
        ax4.set_ylim(-amp_lim, amp_lim)

        if M <= 32:
            pos_ticks = np.arange(0, M, 1)
        else:
            max_ticks = 9
            step = max(1, int(np.ceil((M - 1) / (max_ticks - 1))))
            pos_ticks = np.arange(0, M, step)
            if pos_ticks[-1] != M - 1:
                pos_ticks = np.append(pos_ticks, M - 1)

        pos_nonzero = pos_ticks[pos_ticks > 0]
        ticks_sym = np.concatenate((-pos_nonzero[::-1], [0.0], pos_nonzero))
        ax3.set_yticks(ticks_sym)
        ax4.set_yticks(ticks_sym)
    else:
        maxy = max(np.max(np.abs(tx_seg)), np.max(np.abs(rx_seg))) + 1e-12
        ax3.set_ylim(-1.2 * maxy, 1.2 * maxy)
        ax4.set_ylim(-1.2 * maxy, 1.2 * maxy)

    for k in range(vis_symbols + 1):
        tk = (k * sps) / fs
        for ax in (ax3, ax4):
            ax.axvline(tk, linestyle="--", alpha=0.15)

    for ax in (ax3, ax4):
        ax.grid(True, alpha=0.3)
    ax3.legend(loc="upper right")
    ax4.legend(loc="upper right")

    fig2.tight_layout(rect=[0, 0.03, 1, 0.95])

    # =====================================================
    # 5) DIAGRAMA DE CONSTELACIÓN (NO PARA FSK)
    # =====================================================
    if (rx_complex is not None) and (not is_fsk):
        plt.figure(figsize=(5, 5))

        # Muestreo en el centro de símbolo
        sampled_rx = np.array(rx_complex[sps // 2::sps], dtype=np.complex128)

        # Ajuste de BPSK (rotación coherente)
        if is_psk and M == 2:
            sampled_rx *= (-1j)

        plt.scatter(sampled_rx.real, sampled_rx.imag,
                    s=10, alpha=0.5, label="Muestras recibidas")

        if ideal_syms is not None:
            ideal_const = np.array(ideal_syms, dtype=np.complex128)
            ideal_const = np.unique(ideal_const)
            plt.scatter(ideal_const.real, ideal_const.imag,
                        marker="x", s=70, label="Constelación ideal")

        plt.legend(loc="best")
        plt.title(f"{name} – Diagrama de Constelación")
        plt.xlabel("In-Phase (I)")
        plt.ylabel("Quadrature (Q)")
        plt.axhline(0, linewidth=1)
        plt.axvline(0, linewidth=1)
        plt.grid(True, linestyle="--", alpha=0.3)
        plt.axis("equal")
        plt.tight_layout()

    # =====================================================
    # 6) PSD de RX PASABANDA – 2 lados, tipo analizador
    # =====================================================
    NFFT = 4096
    seg_len = NFFT
    step = seg_len // 2
    window = np.hanning(seg_len)

    psd_accum = None
    num_segs = 0

    if len(rx_pb) < seg_len:
        seg = rx_pb
        if len(seg) < NFFT:
            seg = np.pad(seg, (0, NFFT - len(seg)))
        seg_win = seg * np.hanning(len(seg))
        F = np.fft.fft(seg_win, NFFT)
        F = np.fft.fftshift(F)
        psd_accum = np.abs(F) ** 2
        num_segs = 1
    else:
        for start in range(0, len(rx_pb) - seg_len + 1, step):
            seg = rx_pb[start:start + seg_len]
            seg_win = seg * window
            F = np.fft.fft(seg_win, NFFT)
            F = np.fft.fftshift(F)
            psd = np.abs(F) ** 2

            if psd_accum is None:
                psd_accum = psd
            else:
                psd_accum += psd
            num_segs += 1

    psd_mean = psd_accum / max(num_segs, 1)
    psd_mean /= np.max(psd_mean) + 1e-15
    psd_db = 10.0 * np.log10(psd_mean + 1e-15)
    freqs = np.fft.fftshift(np.fft.fftfreq(NFFT, d=1.0 / fs))

    plt.figure(figsize=(10, 4))
    plt.plot(freqs, psd_db, linewidth=1.0)
    plt.title(f"{name} – Densidad Espectral de Potencia (RX pasabanda)")
    plt.xlabel("Frecuencia [Hz]")
    plt.ylabel("PSD [dB]")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()

    plt.show()


# ==============================================================================
# 3. CONFIGURACIÓN MANUAL / PRUEBA
# ==============================================================================

def symbols_for_M(M, base_factor=20, min_syms=40):
    """
    El número de símbolos se ajusta automáticamente según M:
    num_symbols = max(min_syms, base_factor * M)
    """
    return max(min_syms, base_factor * M)


if __name__ == "__main__":
    ISI_LEVEL = "ninguno"
    if ISI_LEVEL == "ninguno":
        MI_ISI = 0.0
    elif ISI_LEVEL == "bajo":
        MI_ISI = float(np.random.uniform(0.1, 0.3))
    elif ISI_LEVEL == "medio":
        MI_ISI = float(np.random.uniform(0.4, 0.7))
    elif ISI_LEVEL == "alto":
        MI_ISI = float(np.random.uniform(0.8, 1.0))
    else:
        raise ValueError("ISI_LEVEL debe ser: 'ninguno', 'bajo', 'medio' o 'alto'")

    print(f"Nivel ISI: {ISI_LEVEL}, MI_ISI={MI_ISI:.3f}")

    # IMPORTANTE:
    # - Si quieres canal IDEAL: pon MI_SNR = None
    # - Si quieres canal con ruido pequeño: pon MI_SNR alto (p.ej. 40, 60, 100)
    MI_SNR = 1500   # o None para constelación perfecta

    # Modos
    M_ASK = 64
    M_PSK = 64
    M_QAM = 64
    M_FSK = 64   # puedes cambiar de 2 a 64 (incluso 256) sin romper nada

    print(f"Generando con SNR_visual={MI_SNR} dB, ISI={ISI_LEVEL} (MI_ISI={MI_ISI:.3f}) ...\n")

    # ================= ASK =================
    num_ask = symbols_for_M(M_ASK)
    print(f"{M_ASK}-ASK con {num_ask} símbolos")
    gen_ask = SignalGenerator(samples_per_symbol=32,
                              num_symbols=num_ask,
                              symbol_rate=1000,
                              seed=None)
    tx_pb, rx_pb, bits, symbols, iq_syms, tx_bb, rx_bb = gen_ask.generate_ask(M_ASK, MI_SNR, MI_ISI)
    plot_modulation_analysis(f"{M_ASK}-ASK", tx_pb, rx_pb, bits, symbols, M_ASK,
                             gen_ask.fs, gen_ask.samples_per_symbol,
                             rx_complex=rx_bb, tx_complex=tx_bb,
                             ideal_syms=iq_syms)

    # ================= PSK =================
    num_psk = symbols_for_M(M_PSK)
    print(f"{M_PSK}-PSK con {num_psk} símbolos")
    gen_psk = SignalGenerator(samples_per_symbol=32,
                              num_symbols=num_psk,
                              symbol_rate=1000,
                              seed=None)
    tx_pb, rx_pb, bits, symbols, iq_syms, tx_bb, rx_bb = gen_psk.generate_psk(M_PSK, MI_SNR, MI_ISI)
    plot_modulation_analysis(f"{M_PSK}-PSK", tx_pb, rx_pb, bits, symbols, M_PSK,
                             gen_psk.fs, gen_psk.samples_per_symbol,
                             rx_complex=rx_bb, tx_complex=tx_bb,
                             ideal_syms=iq_syms)

    # ================= QAM =================
    num_qam = symbols_for_M(M_QAM)
    print(f"{M_QAM}-QAM con {num_qam} símbolos")
    gen_qam = SignalGenerator(samples_per_symbol=32,
                              num_symbols=num_qam,
                              symbol_rate=1000,
                              seed=None)
    tx_pb, rx_pb, bits, symbols, iq_syms, tx_bb, rx_bb = gen_qam.generate_qam(M_QAM, MI_SNR, MI_ISI)
    plot_modulation_analysis(f"{M_QAM}-QAM", tx_pb, rx_pb, bits, symbols, M_QAM,
                             gen_qam.fs, gen_qam.samples_per_symbol,
                             rx_complex=rx_bb, tx_complex=tx_bb,
                             ideal_syms=iq_syms)

    # ================= FSK =================
    num_fsk = symbols_for_M(M_FSK)
    print(f"{M_FSK}-FSK con {num_fsk} símbolos")
    gen_fsk = SignalGenerator(samples_per_symbol=128,
                              num_symbols=num_fsk,
                              symbol_rate=1000,
                              seed=None)
    tx_pb, rx_pb, bits, symbols, iq_syms, tx_bb, rx_bb = gen_fsk.generate_fsk(M_FSK, MI_SNR, MI_ISI)
    plot_modulation_analysis(f"{M_FSK}-FSK", tx_pb, rx_pb, bits, symbols, M_FSK,
                             gen_fsk.fs, gen_fsk.samples_per_symbol,
                             rx_complex=rx_bb, tx_complex=tx_bb,
                             ideal_syms=None)
