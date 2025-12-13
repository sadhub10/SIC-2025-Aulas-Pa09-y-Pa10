import os
import re
import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from sklearn.metrics import classification_report  # NUEVO

# ================================================================
# CONFIGURACIÓN GLOBAL
# ================================================================
DATA_ROOT = r"E:\Dath\images"  # <- ASEGÚRATE que aquí dentro haya train/ y val/
TRAIN_SUBDIR = "train"
VAL_SUBDIR = "val"

IMG_SIZE = 96
BATCH_SIZE = 16
EPOCHS = 8

USE_LABEL_SMOOTHING = True
LABEL_SMOOTHING_ALPHA = 0.1

LEARNING_RATE = 1e-3
WEIGHT_DECAY = 1e-4

NUM_WORKERS = 0  # en Windows pon 0 para evitar problemas

SAVE_BEST_MODEL_PATH = "best_modulation_cnn.pth"
SEED = 42

# ================================================================
# SEED PARA REPRODUCIBILIDAD
# ================================================================
torch.manual_seed(SEED)
np.random.seed(SEED)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Usando dispositivo:", device)

# ================================================================
# DATASET CON RUTA (para luego sacar SNR desde el filename)
# ================================================================
class ImageFolderWithPaths(datasets.ImageFolder):
    """
    Igual que ImageFolder, pero devuelve también la ruta del archivo.
    Salida: (imagen, label, path)
    """
    def __getitem__(self, index):
        img, label = super().__getitem__(index)
        path, _ = self.samples[index]
        return img, label, path

# ================================================================
# TRANSFORMS (AUGMENTATION / NORMALIZACIÓN)
# ================================================================
train_transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.RandomRotation(5),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5]),
])

val_transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5]),
])

# ================================================================
# DATASETS Y DATALOADERS
# ================================================================
train_dir = os.path.join(DATA_ROOT, TRAIN_SUBDIR)
val_dir   = os.path.join(DATA_ROOT, VAL_SUBDIR)

if not os.path.isdir(train_dir):
    raise RuntimeError(f"No se encontró train_dir: {train_dir}")
if not os.path.isdir(val_dir):
    raise RuntimeError(f"No se encontró val_dir: {val_dir}")

train_dataset = ImageFolderWithPaths(root=train_dir, transform=train_transform)
val_dataset   = ImageFolderWithPaths(root=val_dir, transform=val_transform)

train_loader = DataLoader(train_dataset,
                          batch_size=BATCH_SIZE,
                          shuffle=True,
                          num_workers=NUM_WORKERS)

val_loader = DataLoader(val_dataset,
                        batch_size=BATCH_SIZE,
                        shuffle=False,
                        num_workers=NUM_WORKERS)

class_names = train_dataset.classes
num_classes = len(class_names)
print("Clases encontradas:", class_names)
print("Número de clases:", num_classes)

# ================================================================
# MODELO: BLOQUE RESIDUAL Y RED PRINCIPAL
# ================================================================
class BasicBlock(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.conv1 = nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1)
        self.bn1   = nn.BatchNorm2d(out_ch)
        self.conv2 = nn.Conv2d(out_ch, out_ch, kernel_size=3, padding=1)
        self.bn2   = nn.BatchNorm2d(out_ch)

        self.shortcut = nn.Sequential()
        if in_ch != out_ch:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_ch, out_ch, kernel_size=1),
                nn.BatchNorm2d(out_ch)
            )

    def forward(self, x):
        identity = self.shortcut(x)
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += identity
        out = F.relu(out)
        return out

class ModulationResNet(nn.Module):
    def __init__(self, num_classes: int, img_size: int = 128):
        super().__init__()
        self.conv_in = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.bn_in   = nn.BatchNorm2d(32)

        self.block1 = BasicBlock(32, 64)
        self.pool1  = nn.MaxPool2d(2, 2)  # img -> img/2
        self.block2 = BasicBlock(64, 128)
        self.pool2  = nn.MaxPool2d(2, 2)  # img/2 -> img/4
        self.block3 = BasicBlock(128, 256)
        self.pool3  = nn.MaxPool2d(2, 2)  # img/4 -> img/8

        # Dimensión final: 256 x (img_size/8) x (img_size/8)
        feat_dim = 256 * (img_size // 8) * (img_size // 8)

        self.dropout = nn.Dropout(0.5)
        self.fc1 = nn.Linear(feat_dim, 512)
        self.fc2 = nn.Linear(512, num_classes)

    def forward(self, x):
        x = F.relu(self.bn_in(self.conv_in(x)))

        x = self.pool1(self.block1(x))
        x = self.pool2(self.block2(x))
        x = self.pool3(self.block3(x))

        x = x.view(x.size(0), -1)
        x = self.dropout(F.relu(self.fc1(x)))
        x = self.fc2(x)
        return x

# ================================================================
# INICIALIZAR MODELO, LOSS, OPTIMIZER, SCHEDULER
# ================================================================
model = ModulationResNet(num_classes=num_classes, img_size=IMG_SIZE).to(device)

if USE_LABEL_SMOOTHING:
    criterion = nn.CrossEntropyLoss(label_smoothing=LABEL_SMOOTHING_ALPHA)
else:
    criterion = nn.CrossEntropyLoss()

optimizer = optim.Adam(
    model.parameters(),
    lr=LEARNING_RATE,
    weight_decay=WEIGHT_DECAY
)

scheduler = optim.lr_scheduler.ReduceLROnPlateau(
    optimizer,
    mode='max',      # maximizamos val_acc
    factor=0.5,
    patience=3,
)

# ================================================================
# FUNCIONES DE ENTRENAMIENTO Y VALIDACIÓN
# ================================================================
def train_one_epoch(epoch, model, loader, optimizer, criterion, device):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels, _paths in loader:  # paths no se usan aquí
        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()

    epoch_loss = running_loss / total
    epoch_acc = correct / total
    print(f"[Epoch {epoch}] Train Loss: {epoch_loss:.4f} | Train Acc: {epoch_acc:.4f}")
    return epoch_loss, epoch_acc

def eval_one_epoch(epoch, model, loader, criterion, device, split_name="Val"):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels, _paths in loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            running_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

    epoch_loss = running_loss / total
    epoch_acc = correct / total
    print(f"[Epoch {epoch}] {split_name} Loss: {epoch_loss:.4f} | {split_name} Acc: {epoch_acc:.4f}")
    return epoch_loss, epoch_acc

# ================================================================
# ENTRENAMIENTO PRINCIPAL (CON TRACKING DE LR)
# ================================================================
best_val_acc = 0.0

for epoch in range(1, EPOCHS + 1):
    # --- Entrenamiento ---
    train_loss, train_acc = train_one_epoch(
        epoch, model, train_loader, optimizer, criterion, device
    )

    # --- Validación ---
    val_loss, val_acc = eval_one_epoch(
        epoch, model, val_loader, criterion, device, split_name="Val"
    )

    # --- LR antes del scheduler ---
    old_lrs = [g["lr"] for g in optimizer.param_groups]
    print(f"[Epoch {epoch}] LR antes del scheduler: {old_lrs}")

    # --- Scheduler (ReduceLROnPlateau usa val_acc) ---
    scheduler.step(val_acc)

    # --- LR después del scheduler ---
    new_lrs = [g["lr"] for g in optimizer.param_groups]
    if new_lrs != old_lrs:
        print(f"[Scheduler] LR cambiado en Epoch {epoch}: {old_lrs} -> {new_lrs}")
    else:
        print(f"[Scheduler] LR sin cambios en Epoch {epoch}: {new_lrs}")

    # --- Guardar mejor modelo según Val Acc ---
    if val_acc > best_val_acc:
        best_val_acc = val_acc
        torch.save(model.state_dict(), SAVE_BEST_MODEL_PATH)
        print(f"  -> Nuevo mejor modelo guardado: {SAVE_BEST_MODEL_PATH} (Val Acc = {best_val_acc:.4f})")

print("Entrenamiento finalizado.")
print(f"Mejor Val Acc: {best_val_acc:.4f}")

# ================================================================
# EVALUACIÓN DETALLADA: MATRIZ DE CONFUSIÓN Y ACCURACY POR SNR
# ================================================================
def compute_confusion_matrix(model, loader, device, num_classes):
    model.eval()
    cm = np.zeros((num_classes, num_classes), dtype=np.int64)

    all_labels = []
    all_preds = []

    with torch.no_grad():
        for images, labels, _paths in loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            _, predicted = outputs.max(1)

            for t, p in zip(labels.cpu().numpy(), predicted.cpu().numpy()):
                cm[t, p] += 1

            all_labels.extend(labels.cpu().numpy().tolist())
            all_preds.extend(predicted.cpu().numpy().tolist())

    return cm, np.array(all_labels), np.array(all_preds)

def extract_snr_from_path(path):
    """
    Intenta extraer el SNR desde el filename.
    Espera algo tipo: ..._snr10_... o ...snr-5...
    Si no encuentra nada, devuelve None.
    """
    filename = os.path.basename(path).lower()
    m = re.search(r"snr(-?\d+)", filename)
    if m:
        return int(m.group(1))
    return None

def evaluate_by_snr(model, loader, device):
    """
    Calcula accuracy por SNR, asumiendo que el SNR está en el nombre del archivo.
    Si no encuentra SNR en ningún archivo, avisa y se sale.
    """
    model.eval()
    snr_stats = {}  # snr -> {"correct": x, "total": y}

    with torch.no_grad():
        for images, labels, paths in loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            _, predicted = outputs.max(1)

            for t, p, path in zip(labels.cpu().numpy(),
                                  predicted.cpu().numpy(),
                                  paths):
                snr = extract_snr_from_path(path)
                if snr is None:
                    continue
                if snr not in snr_stats:
                    snr_stats[snr] = {"correct": 0, "total": 0}
                snr_stats[snr]["total"] += 1
                if t == p:
                    snr_stats[snr]["correct"] += 1

    if not snr_stats:
        print("No se pudo extraer SNR de los filenames (no se encontró 'snrXX').")
        return

    print("\nAccuracy por SNR (usando conjunto de validación):")
    for snr in sorted(snr_stats.keys()):
        correct = snr_stats[snr]["correct"]
        total = snr_stats[snr]["total"]
        acc = correct / total if total > 0 else 0.0
        print(f"  SNR = {snr:>3} dB -> Acc = {acc:.4f}  (n={total})")

# ------------------------------------------------
# Helpers para agrupar por tipo de modulación y por M  (NUEVO)
# ------------------------------------------------
def parse_class_name(name: str):
    """
    Convierte 'QAM_64' -> ('QAM', 64).
    Si el formato no es 'TIPO_M', lanza un error.
    """
    parts = name.split('_')
    if len(parts) != 2:
        raise ValueError(f"Nombre de clase inesperado (se esperaba 'TIPO_M'): {name}")
    mod_type = parts[0]
    M = int(parts[1])
    return mod_type, M

def summarize_group_metrics(report_dict, class_names):
    """
    Toma el dict de classification_report(output_dict=True)
    y colapsa métricas por:
      - tipo de modulación (ASK, PSK, QAM, FSK, ...)
      - orden M (2, 4, 8, 16, ...)
    Imprime macro-average y weighted-average dentro de cada grupo.
    """
    # ---- Por tipo de modulación ----
    type_stats = {}  # mod_type -> acumuladores

    # ---- Por orden M ----
    M_stats = {}     # M -> acumuladores

    for name in class_names:
        if name not in report_dict:
            continue  # por si acaso

        mod_type, M = parse_class_name(name)
        metrics = report_dict[name]

        prec = metrics["precision"]
        rec  = metrics["recall"]
        f1   = metrics["f1-score"]
        sup  = metrics["support"]

        # --- Acumular por tipo de modulación ---
        if mod_type not in type_stats:
            type_stats[mod_type] = {
                "macro_prec_sum": 0.0,
                "macro_rec_sum":  0.0,
                "macro_f1_sum":   0.0,
                "n_classes":      0,
                "weighted_prec_sum": 0.0,
                "weighted_rec_sum":  0.0,
                "weighted_f1_sum":   0.0,
                "support_total":     0.0,
            }

        t = type_stats[mod_type]
        t["macro_prec_sum"] += prec
        t["macro_rec_sum"]  += rec
        t["macro_f1_sum"]   += f1
        t["n_classes"]      += 1

        t["weighted_prec_sum"] += prec * sup
        t["weighted_rec_sum"]  += rec  * sup
        t["weighted_f1_sum"]   += f1   * sup
        t["support_total"]     += sup

        # --- Acumular por orden M ---
        if M not in M_stats:
            M_stats[M] = {
                "macro_prec_sum": 0.0,
                "macro_rec_sum":  0.0,
                "macro_f1_sum":   0.0,
                "n_classes":      0,
                "weighted_prec_sum": 0.0,
                "weighted_rec_sum":  0.0,
                "weighted_f1_sum":   0.0,
                "support_total":     0.0,
            }

        m = M_stats[M]
        m["macro_prec_sum"] += prec
        m["macro_rec_sum"]  += rec
        m["macro_f1_sum"]   += f1
        m["n_classes"]      += 1

        m["weighted_prec_sum"] += prec * sup
        m["weighted_rec_sum"]  += rec  * sup
        m["weighted_f1_sum"]   += f1   * sup
        m["support_total"]     += sup

    # ---- Imprimir resumen por tipo ----
    print("\nMétricas agregadas por TIPO de modulación:")
    for mod_type, stats in type_stats.items():
        n = stats["n_classes"]
        sup_tot = stats["support_total"]

        macro_prec = stats["macro_prec_sum"] / n
        macro_rec  = stats["macro_rec_sum"]  / n
        macro_f1   = stats["macro_f1_sum"]   / n

        weighted_prec = stats["weighted_prec_sum"] / sup_tot
        weighted_rec  = stats["weighted_rec_sum"]  / sup_tot
        weighted_f1   = stats["weighted_f1_sum"]   / sup_tot

        print(f"  {mod_type}:")
        print(f"    Macro    -> P={macro_prec:.4f}, R={macro_rec:.4f}, F1={macro_f1:.4f}, clases={n}")
        print(f"    Weighted -> P={weighted_prec:.4f}, R={weighted_rec:.4f}, F1={weighted_f1:.4f}, muestras={int(sup_tot)}")

    # ---- Imprimir resumen por orden M ----
    print("\nMétricas agregadas por ORDEN M:")
    for M, stats in sorted(M_stats.items(), key=lambda x: x[0]):  # ordenar por M
        n = stats["n_classes"]
        sup_tot = stats["support_total"]

        macro_prec = stats["macro_prec_sum"] / n
        macro_rec  = stats["macro_rec_sum"]  / n
        macro_f1   = stats["macro_f1_sum"]   / n

        weighted_prec = stats["weighted_prec_sum"] / sup_tot
        weighted_rec  = stats["weighted_rec_sum"]  / sup_tot
        weighted_f1   = stats["weighted_f1_sum"]   / sup_tot

        print(f"  M = {M}:")
        print(f"    Macro    -> P={macro_prec:.4f}, R={macro_rec:.4f}, F1={macro_f1:.4f}, clases={n}")
        print(f"    Weighted -> P={weighted_prec:.4f}, R={weighted_rec:.4f}, F1={weighted_f1:.4f}, muestras={int(sup_tot)}")

# ================================================================
# CARGAR MEJOR MODELO Y EVALUAR
# ================================================================
if os.path.isfile(SAVE_BEST_MODEL_PATH):
    print(f"\nCargando mejor modelo desde: {SAVE_BEST_MODEL_PATH}")
    model.load_state_dict(torch.load(SAVE_BEST_MODEL_PATH, map_location=device))
    model.to(device)
else:
    print("\n[AVISO] No se encontró el fichero del mejor modelo, usando último estado de entrenamiento.")

# Matriz de confusión en validación
cm, all_labels, all_preds = compute_confusion_matrix(model, val_loader, device, num_classes)

print("\nMatriz de confusión (filas = verdadero, columnas = predicho):")
print(cm)

print("\nEtiquetas de clase:")
for idx, name in enumerate(class_names):
    print(f"  {idx}: {name}")

# ================================================================
# REPORTE: PRECISION, RECALL, F1-SCORE, SUPPORT (por clase)
# ================================================================
print("\nReporte de clasificación (precision, recall, f1-score, support):")
print(classification_report(
    all_labels,
    all_preds,
    target_names=class_names,
    digits=4
))

# Para agrupar por tipo y por M usamos output_dict=True
report_dict = classification_report(
    all_labels,
    all_preds,
    target_names=class_names,
    digits=4,
    output_dict=True
)

summarize_group_metrics(report_dict, class_names)  # NUEVO: resumen por tipo y M

# Accuracy por SNR (si los filenames lo permiten)
evaluate_by_snr(model, val_loader, device)
