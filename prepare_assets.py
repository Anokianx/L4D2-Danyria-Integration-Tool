# =============================================================================
# 模块说明：生成 Windows 图标资源，供打包 exe 时使用。
# Module overview: Generates Windows icon assets for exe packaging.
# =============================================================================

from pathlib import Path

# ---------------------------------------------------------------------------
# 定位 assets 目录并选择头像源图。
# Locates the assets folder and selects the avatar source image.
# ---------------------------------------------------------------------------
root = Path(__file__).resolve().parent
assets = root / "assets"
avatar = assets / "avatar_normal.png"
if not avatar.exists():
    avatar = assets / "avatar.png"
ico = assets / "avatar.ico"

if not avatar.exists():
    print("avatar_normal.png / avatar.png not found.")
    raise SystemExit(0)

# ---------------------------------------------------------------------------
# 加载 Pillow 并生成多尺寸 ico。
# Loads Pillow and generates a multi-size ico file.
# ---------------------------------------------------------------------------
try:
    from PIL import Image
except Exception:
    print("Pillow not installed. Run: py -3 -m pip install Pillow")
    raise

img = Image.open(avatar).convert("RGBA")
img.save(ico, sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
print("Generated", ico)
