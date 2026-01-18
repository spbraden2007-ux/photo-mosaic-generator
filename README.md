# 🎨 Photo Mosaic Generator

Transform any image into a stunning mosaic artwork composed of thousands of smaller tile images using KDTree-based color matching.

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white)
![Pillow](https://img.shields.io/badge/Pillow-PIL-green?style=flat)

---

## 📖 Origin Story

<table>
<tr>
<td width="50%" valign="top">

### 🖼️ 2021: By Hand

In Fall 2021, I participated in my school's art competition with a photo mosaic piece — **placing 2nd overall**. Back then, I assembled every single tile manually: selecting images, matching colors by eye, and arranging thousands of pieces by hand. The process took weeks.

</td>
<td width="50%" valign="top">

### 💻 2025: By Algorithm

Three years later, after learning to code, I revisited this art form with a new perspective. What once took weeks now takes seconds. The same creative vision, now powered by KDTree color matching and computational optimization.

**From manual craft to computational art.**

</td>
</tr>
</table>

---

## 🖼️ Example

<table>
<tr>
<td align="center" width="50%"><b>Input Library</b></td>
<td align="center" width="50%"><b>Final Output</b></td>
</tr>
<tr>
<td align="center" bgcolor="#f8f9fa">
  <br/><br/>
  <h1 style="color: #3776AB; font-family: sans-serif;">650+</h1>
  <p style="color: #666; font-family: sans-serif;">Original Images & Artworks</p>
  <br/><br/>
</td>
<td>
  <img src="output/output.jpg" width="400" alt="Generated Photo Mosaic Output"/>
</td>
</tr>
</table>

> *All tile images are original: personal photographs, family memories, and my own digital artwork.*

---

## ✨ Features

- **KDTree Color Matching**: Efficient nearest-neighbor search in RGB color space for optimal tile selection
- **Automatic Grid Sizing**: Preserves aspect ratio while optimizing tile density
- **Anti-Repetition**: Randomized selection from top-K matches to reduce visual patterns
- **Smart Blending**: Automatic alpha blending for artistic balance between mosaic and original
- **High Quality Output**: Lanczos resampling + UnsharpMask for crisp results

---

## 🔧 Algorithm

```
┌─────────────────────────────────────────────────────────────────┐
│                        MOSAIC PIPELINE                          │
└─────────────────────────────────────────────────────────────────┘

1. PREPROCESSING
   ┌──────────────┐      ┌──────────────┐
   │  Load 650+   │ ──→  │  Resize to   │ ──→  Compute average RGB
   │  tile images │      │  40×40 px    │      for each tile
   └──────────────┘      └──────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │  Build KDTree with  │
                    │  650+ RGB vectors   │
                    └─────────────────────┘

2. COLOR MATCHING
   ┌──────────────┐      ┌──────────────────┐      ┌─────────────┐
   │ Main image   │ ──→  │ Downscale to     │ ──→  │ Each pixel  │
   │ (any size)   │      │ grid (cols×rows) │      │ = 1 cell    │
   └──────────────┘      └──────────────────┘      └─────────────┘
                                                          │
                                                          ▼
                                               ┌─────────────────────┐
                                               │ Query KDTree:       │
                                               │ Find top-K nearest  │
                                               │ tiles by RGB color  │
                                               └─────────────────────┘
                                                          │
                                                          ▼
                                               ┌─────────────────────┐
                                               │ Random selection    │
                                               │ from candidates     │
                                               │ (avoid repetition)  │
                                               └─────────────────────┘

3. COMPOSITION
   ┌──────────────────────────────────────────────────────────────┐
   │  Paste selected tiles onto canvas → Blend with original     │
   │  → Apply UnsharpMask → Save high-quality output             │
   └──────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
photo-mosaic-generator/
├── mosaic.py           # Main script
├── Main.jpg            # Input image
├── tiles/              # 650+ tile images
│   ├── tile_001.jpg
│   ├── tile_002.jpg
│   └── ...
└── output/
    └── output.jpg      # Generated mosaic
```

---

## 🚀 Usage

### Prerequisites

```bash
pip install numpy pillow scipy
```

### Run

```bash
python mosaic.py
```

### Configuration

Edit parameters in `mosaic.py`:

```python
# Tile size (bigger = more recognizable tiles)
TILE_W = 40
TILE_H = 40

# Grid density
MIN_COLS = 60
MAX_COLS = 160

# Top-K candidates for variety
TOP_K = 50

# Blend strength (auto-calculated, or override)
ALPHA_MIN = 0.18
ALPHA_MAX = 0.45
```

---

## 🧮 Technical Details

### KDTree Color Matching

The algorithm uses a **k-dimensional tree** for efficient nearest-neighbor search in 3D RGB color space:

```python
# Each tile becomes a point in RGB space
colors = np.vstack([average_rgb(tile) for tile in tiles])  # (N, 3)
tree = KDTree(colors)

# Query: find tiles closest to target color
distances, indices = tree.query(target_color, k=TOP_K)
```

**Complexity**: O(log N) per query vs O(N) brute force — critical for 650+ tiles × 10,000+ cells

### Anti-Repetition Strategy

To avoid visible patterns, we:
1. Query top-K nearest matches (not just the best)
2. Randomly select from candidates
3. Track last-used tile to avoid immediate repeats

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| Tile Library | 650+ images |
| Grid Size | ~120×90 (auto) |
| Total Cells | ~10,800 |
| Processing Time | ~5-10 sec |
| Output Resolution | 4800×3600 px |

---

## 🎯 Applications

- **Personalized Art**: Create mosaics from personal photo collections
- **Corporate Gifts**: Company logos from employee photos
- **Event Memorabilia**: Group photos from event snapshots
- **Digital Art**: Computational art generation

---

## 🏆 Recognition

- **2nd Place** — School Art Competition, Fall 2021 (manual mosaic artwork)

---

## 📜 License

MIT License

All tile images in this project are original works: personal photographs, family photos, and digital artwork created by the author.

---

## 👤 Author

**Seohyun Park**  
University of Waterloo, Computer Science  
Korea Presidential Science Scholarship Recipient

[![GitHub](https://img.shields.io/badge/GitHub-seohyunpark-181717?style=flat&logo=github)](https://github.com/spbraden2007-ux)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-seohyunpark-0A66C2?style=flat&logo=linkedin)](https://linkedin.com/in/sp-park)
