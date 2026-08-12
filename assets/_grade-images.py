"""
Color grading cinematografico calido para imagenes del hotel.
Replica el look "Aman / Soho House / Edition" descrito por el usuario:
- Tonos beige / dorados / desaturados (warm cast)
- Contraste suave (matte shadows, no negros profundos)
- Bloom natural en highlights
- Grain leve
- Profundidad cinematografica

Uso: python _grade-images.py
Backup automatico en images/_originales_backup/ (preserva estructura).
"""
import shutil
import sys
import time
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageChops

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "images"
BACKUP = SRC / "_originales_backup"
EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def cinematic_grade(img: Image.Image) -> Image.Image:
    """Aplica el grading calido cinematografico."""
    has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
    alpha = None
    if has_alpha:
        img = img.convert("RGBA")
        alpha = img.split()[-1]
        img = img.convert("RGB")
    else:
        img = img.convert("RGB")

    # 1. Saturacion -15% (look desaturado editorial)
    img = ImageEnhance.Color(img).enhance(0.85)

    # 2. Contraste -7% (suave, no agresivo)
    img = ImageEnhance.Contrast(img).enhance(0.93)

    # 3. Brillo +4% (exposicion ligeramente alta)
    img = ImageEnhance.Brightness(img).enhance(1.04)

    # 4. Matte / lift shadows: in 0..255 -> out 10..245
    #    eleva negros (no negros profundos) y baja blancos (highlights suaves)
    lut = [int(round(10 + (245 - 10) * (i / 255))) for i in range(256)]
    img = img.point(lut * 3)

    # 5. Warm cast: blend con overlay tan/dorado al 8%
    warm = Image.new("RGB", img.size, (255, 220, 180))
    img = Image.blend(img, warm, 0.08)

    # 6. Bloom suave en highlights: blur grande blendeado al 12%
    blurred = img.filter(ImageFilter.GaussianBlur(radius=10))
    img = Image.blend(img, blurred, 0.12)

    # 7. Grain leve: noise gaussiano blendeado al 3%
    noise = Image.effect_noise(img.size, 14).convert("RGB")
    img = Image.blend(img, noise, 0.03)

    # Restaurar alpha si la tenia
    if alpha is not None:
        img = img.convert("RGBA")
        img.putalpha(alpha)

    return img


def is_inside_backup(p: Path) -> bool:
    return BACKUP in p.parents or p == BACKUP


def process():
    if not SRC.exists():
        print(f"ERROR: no existe {SRC}")
        sys.exit(1)

    BACKUP.mkdir(exist_ok=True)
    files = [
        p for p in SRC.rglob("*")
        if p.is_file() and p.suffix.lower() in EXTS and not is_inside_backup(p)
    ]
    total = len(files)
    print(f"Encontradas {total} imagenes en {SRC}")
    print(f"Backup en {BACKUP}\n")

    ok = 0
    skipped = 0
    failed = []
    t0 = time.time()

    for i, src_path in enumerate(files, 1):
        rel = src_path.relative_to(SRC)
        backup_path = BACKUP / rel
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Si ya existe backup, no sobrescribir (evita perder original
            # si el script se ejecuta dos veces)
            if not backup_path.exists():
                shutil.copy2(src_path, backup_path)

            img = Image.open(src_path)
            graded = cinematic_grade(img)

            ext = src_path.suffix.lower()
            save_kwargs = {}
            if ext in (".jpg", ".jpeg"):
                save_kwargs.update(quality=88, optimize=True, progressive=True)
            elif ext == ".webp":
                save_kwargs.update(quality=88, method=4)
            elif ext == ".png":
                save_kwargs.update(optimize=True)

            graded.save(src_path, **save_kwargs)
            ok += 1
            print(f"[{i}/{total}] OK  {rel}")
        except Exception as e:
            failed.append((str(rel), str(e)))
            print(f"[{i}/{total}] FAIL {rel}: {e}")

    dt = time.time() - t0
    print(f"\n==========================================")
    print(f"OK: {ok} / {total}  |  Fallidos: {len(failed)}  |  Tiempo: {dt:.1f}s")
    if failed:
        print("\nFallidos:")
        for rel, err in failed:
            print(f"  - {rel}: {err}")


if __name__ == "__main__":
    process()
