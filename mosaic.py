import os
import glob
import random

import numpy as np
from PIL import Image, ImageOps, ImageFilter
from scipy.spatial import KDTree


# ----------------------------
# Fixed paths 
# ----------------------------
MAIN_IMAGE_PATH = "Main.jpg"
TILES_DIR = "tiles"
SAVE_DIR = "output"
OUTPUT_PATH = os.path.join(SAVE_DIR, "output.jpg")

# ----------------------------
# Style + Quality settings (tuned for "Image 1" look by default)
# ----------------------------
# Tile size (bigger tiles = less noisy, more recognizable tiles)
TILE_W = 40
TILE_H = 40

# Auto grid:
# We choose the number of columns from the base image width,
# then compute rows to preserve aspect ratio (no forced 1:1).
MIN_COLS = 60
MAX_COLS = 160

# To reduce repetitive patterns:
# We query top K nearest tiles and randomly pick one of them.
TOP_K = 50

# Make the "Image 1" style: blend original image on top of mosaic.
# We compute alpha automatically based on how dense the grid is.
# Lower alpha => mosaic more transparent (original more visible).
ALPHA_MIN = 0.18
ALPHA_MAX = 0.45

# Optional: fixed seed for reproducibility (None = random each run)
SEED = None

VALID_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff")


# ----------------------------
# Utility functions
# ----------------------------
def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


def load_rgb_image(path):
    # Load and force RGB for consistent processing
    img = Image.open(path)
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img


def load_tile_images(tiles_dir):
    # Load all tile images in tiles_dir 
    paths = []
    for ext in VALID_EXTS:
        paths += glob.glob(os.path.join(tiles_dir, "*" + ext))
        paths += glob.glob(os.path.join(tiles_dir, "*" + ext.upper()))

    images = []
    for p in sorted(set(paths)):
        try:
            images.append(load_rgb_image(p))
        except Exception:
            continue
    return images


def fit_to_size(img, size):
    # Center-crop + resize to make every tile the exact same size
    return ImageOps.fit(img, size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))


def average_rgb(img):
    # Average RGB color as a 3D vector [R,G,B]
    arr = np.asarray(img, dtype=np.float32)
    return arr.mean(axis=(0, 1))


def build_kdtree(tile_imgs, tile_size):
    # Resize tiles and compute their average colors, then build KDTree
    resized_tiles = [fit_to_size(im, tile_size) for im in tile_imgs]
    colors = np.vstack([average_rgb(im) for im in resized_tiles])  # (N, 3)
    tree = KDTree(colors)
    return resized_tiles, tree


def choose_grid_size(main_w, main_h, tile_w, tile_h):
    # Choose cols from image width, then compute rows to preserve aspect ratio
    # This avoids forcing the output into a square.
    cols = main_w // tile_w
    cols = clamp(cols, MIN_COLS, MAX_COLS)

    # Preserve aspect ratio: rows/cols ~ main_h/main_w
    rows = int(round(cols * (main_h / float(main_w))))

    # Safety: avoid 0 rows
    rows = max(1, rows)
    return int(cols), int(rows)


def auto_tile_alpha(cols, rows):
    # Heuristic:
    # If grid is dense (lots of small tiles), mosaics look noisy => reduce alpha (more original visible).
    # If grid is coarse (few large tiles), we can increase alpha a bit (tiles still visible).
    density = cols * rows

    # Typical densities might be ~ (80*60=4800) to (160*120=19200)
    # Map density to alpha range:
    # higher density -> smaller alpha
    # lower density -> bigger alpha
    # This curve is intentionally gentle.
    alpha = 0.42 - 0.000008 * density
    return clamp(alpha, ALPHA_MIN, ALPHA_MAX)


def make_mosaic(main_img, resized_tiles, tree, cols, rows, tile_w, tile_h, top_k):
    # Step 1) Shrink the main image to (cols x rows)
    # Each pixel is the target color for one mosaic cell.
    main_small = main_img.resize((cols, rows), resample=Image.Resampling.BILINEAR)
    target_colors = np.asarray(main_small, dtype=np.float32)  # (rows, cols, 3)

    # Step 2) Create the final canvas
    canvas = Image.new("RGB", (cols * tile_w, rows * tile_h))

    # Step 3) For each cell, query KDTree for nearest tiles and paste one
    n_tiles = len(resized_tiles)
    k = min(top_k, n_tiles)

    # Optional: reduce immediate repeats by tracking last chosen tile
    last_idx = -1

    for y in range(rows):
        for x in range(cols):
            color = target_colors[y, x]

            dists, idxs = tree.query(color, k=k)

            # Normalize idxs to a list
            if np.isscalar(idxs):
                candidates = [int(idxs)]
            else:
                candidates = [int(i) for i in idxs]

            # Avoid choosing the same tile as last cell if possible
            if len(candidates) > 1:
                filtered = [i for i in candidates if i != last_idx]
                if filtered:
                    chosen = random.choice(filtered)
                else:
                    chosen = random.choice(candidates)
            else:
                chosen = candidates[0]

            tile = resized_tiles[chosen]
            canvas.paste(tile, (x * tile_w, y * tile_h))
            last_idx = chosen

    return canvas


def blend_to_image1_style(main_img, mosaic_img, cols, rows):
    # Resize original to match mosaic output size
    original_resized = main_img.resize(mosaic_img.size, resample=Image.Resampling.LANCZOS)

    # Automatic alpha for consistent "Image 1" look
    alpha = auto_tile_alpha(cols, rows)

    # Blend:
    # result = (1-alpha)*original + alpha*mosaic
    blended = Image.blend(original_resized, mosaic_img, alpha)

    # Optional: subtle sharpening to make the original feel crisp like "Image 1"
    blended = blended.filter(ImageFilter.UnsharpMask(radius=1.5, percent=140, threshold=3))

    return blended, alpha


def main():
    if SEED is not None:
        random.seed(SEED)

    if not os.path.exists(MAIN_IMAGE_PATH):
        raise FileNotFoundError("Main image not found: " + MAIN_IMAGE_PATH)
    if not os.path.isdir(TILES_DIR):
        raise NotADirectoryError("Tiles folder not found: " + TILES_DIR)

    main_img = load_rgb_image(MAIN_IMAGE_PATH)
    tile_imgs = load_tile_images(TILES_DIR)

    # You can run with fewer tiles, but quality improves with more variety.
    if len(tile_imgs) < 20:
        raise RuntimeError("Not enough tile images in tiles/ (need at least ~20). Found: " + str(len(tile_imgs)))

    main_w, main_h = main_img.size
    cols, rows = choose_grid_size(main_w, main_h, TILE_W, TILE_H)

    tile_size = (TILE_W, TILE_H)
    resized_tiles, tree = build_kdtree(tile_imgs, tile_size)

    mosaic_img = make_mosaic(
        main_img=main_img,
        resized_tiles=resized_tiles,
        tree=tree,
        cols=cols,
        rows=rows,
        tile_w=TILE_W,
        tile_h=TILE_H,
        top_k=TOP_K,
    )

    final, alpha = blend_to_image1_style(main_img, mosaic_img, cols, rows)

    # Save inside tiles/ as result.jpg
    final.save(OUTPUT_PATH, quality=95)
    print("[OK] Saved:", OUTPUT_PATH)
    print("[INFO] Grid:", cols, "x", rows, "(tiles)")
    print("[INFO] Tile size:", TILE_W, "x", TILE_H, "(px)")
    print("[INFO] Output size:", final.size, "(px)")
    print("[INFO] Blend alpha (mosaic strength):", round(alpha, 3))


if __name__ == "__main__":
    main()
