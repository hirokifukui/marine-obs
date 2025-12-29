#!/usr/bin/env python3
"""
カラースキーム調整スクリプト
落ち着いた科学的トーンに統一
"""

# Read file
with open("/Users/hirokifukui/Dropbox (個人)/Scripts/claude/outputs/marine-obs-pilot/index.html", "r", encoding="utf-8") as f:
    content = f.read()

# Color replacements
replacements = [
    # 警報赤系 → 落ち着いた赤茶
    ("#e74c3c", "#a65d5d"),
    ("#c53030", "#996060"),
    ("#c0392b", "#8b5a5a"),
    
    # 警報黄系 → 落ち着いた琥珀
    ("#f9a825", "#c4a35a"),
    ("#ff8f00", "#b8956a"),
    ("#744210", "#6b5a3d"),
    
    # 緑/ティール系 → 深いティール（ヒーローと調和）
    ("#4ecdc4", "#5b9a94"),
    ("#4fd1c5", "#5b9a94"),
    ("#007a6c", "#3d7a73"),
    ("#005f54", "#2d5f5a"),
    ("#004a42", "#1d4a45"),
    ("#48bb78", "#5a9a7a"),  # good status
    ("#22543d", "#2a4a3d"),
    ("#27ae60", "#4a8a6a"),
    ("#c6f6d5", "#d4e8e0"),  # badge background
    
    # その他調整
    ("#81e6d9", "#7ab8b0"),  # hover state
]

for old, new in replacements:
    content = content.replace(old, new)

# Write back
with open("/Users/hirokifukui/Dropbox (個人)/Scripts/claude/outputs/marine-obs-pilot/index.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Color scheme updated!")
print("\nReplacements made:")
for old, new in replacements:
    print(f"  {old} → {new}")
