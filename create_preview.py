from PIL import Image
import os

img_path = "menu-bg.png"
out_path = "menu-bg-preview.jpg"

if os.path.exists(img_path):
    with Image.open(img_path) as img:
        width, height = img.size
        print(f"Original: {width}x{height}")
        
        # Target a reasonable width for editor (e.g., 2000px)
        # Original is likely ~3600px (12in * 300dpi)
        target_width = 1500
        scale = target_width / width
        target_height = int(height * scale)
        
        print(f"Resizing to: {target_width}x{target_height}")
        # Use LANCZOS (high quality) but save as compressed JPG
        preview = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
        preview = preview.convert("RGB") # JPG requires RGB
        preview.save(out_path, "JPEG", quality=70, optimize=True)
        
        print(f"Saved optimized preview to {out_path}")
        print(f"Preview size: {os.path.getsize(out_path) / 1024:.2f} KB")
else:
    print(f"Error: {img_path} not found")
