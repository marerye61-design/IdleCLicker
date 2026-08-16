import os
import shutil
from PIL import Image

def optimize_image(filepath):
    try:
        orig_sz = os.path.getsize(filepath)
        filename = os.path.basename(filepath)
        name_lower = filename.lower()
        
        with Image.open(filepath) as im:
            # Określenie maksymalnych docelowych wymiarów
            # Tła: maksymalnie 1280x720 (lub 1366x768)
            if any(k in name_lower for k in ['bg', 'tavern', 'combat', 'dungeon', 'menu']):
                max_dim = (1280, 720)
            # Ikony przedmiotów: maksymalnie 160x160
            elif any(k in name_lower for k in ['icon', 'acc_', 'arm_', 'helm_', 'wep_', 'pot_']):
                max_dim = (160, 160)
            # Bossowie i portrety: maksymalnie 450x450
            else:
                max_dim = (450, 450)
                
            im_copy = im.copy()
            if im_copy.size[0] > max_dim[0] or im_copy.size[1] > max_dim[1]:
                im_copy.thumbnail(max_dim, Image.LANCZOS)
                
            # Zapis z optymalizacją
            if name_lower.endswith('.png'):
                if im_copy.mode == 'RGBA':
                    im_copy.save(filepath, format='PNG', optimize=True)
                else:
                    if im_copy.mode != 'RGB':
                        im_copy = im_copy.convert('RGB')
                    im_copy.save(filepath, format='PNG', optimize=True)
            elif name_lower.endswith(('.jpg', '.jpeg')):
                if im_copy.mode in ('RGBA', 'P'):
                    im_copy = im_copy.convert('RGB')
                im_copy.save(filepath, format='JPEG', quality=85, optimize=True, progressive=True)
                
        new_sz = os.path.getsize(filepath)
        return orig_sz, new_sz
    except Exception as e:
        print(f"Błąd optymalizacji {filepath}: {e}")
        return os.path.getsize(filepath), os.path.getsize(filepath)

def process_directory(assets_path):
    print(f"=== Rozpoczynanie optymalizacji katalogu: {assets_path} ===")
    total_before = 0
    total_after = 0
    file_count = 0
    
    for root, dirs, files in os.walk(assets_path):
        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                fp = os.path.join(root, f)
                before, after = optimize_image(fp)
                total_before += before
                total_after += after
                file_count += 1
                diff_pct = ((before - after) / before * 100) if before > 0 else 0
                if diff_pct > 5:
                    print(f"  [Zoptymalizowano] {f}: {before//1024} KB -> {after//1024} KB (-{diff_pct:.1f}%)")
                    
    mb_before = total_before / (1024 * 1024)
    mb_after = total_after / (1024 * 1024)
    saved_mb = mb_before - mb_after
    saved_pct = (saved_mb / mb_before * 100) if mb_before > 0 else 0
    
    print(f"\n--- PODSUMOWANIE DLA {assets_path} ---")
    print(f"Liczba przetworzonych plików graficznych: {file_count}")
    print(f"Rozmiar przed: {mb_before:.2f} MB")
    print(f"Rozmiar po:    {mb_after:.2f} MB")
    print(f"Zaoszczędzono: {saved_mb:.2f} MB (-{saved_pct:.1f}%)\n")

if __name__ == '__main__':
    for p in ['assets', '../IdleClicker/assets']:
        if os.path.exists(p):
            process_directory(p)
