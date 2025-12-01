#!/usr/bin/env python3
"""
Create TikTok Preview Video for ATLAS Starship Session
Vertical 9:16 format, 18 seconds with text overlays
"""

import subprocess
import os

SESSION_DIR = "/home/rsalars/Projects/dreamweaving/sessions/atlas-starship-ancient-future"
IMAGES_DIR = f"{SESSION_DIR}/images/uploaded"
OUTPUT_DIR = f"{SESSION_DIR}/output/tiktok"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_tiktok_preview():
    print("=" * 60)
    print("Creating TikTok Preview Video")
    print("=" * 60)

    # Build the ffmpeg command
    cmd = [
        'ffmpeg', '-y',
        # Input images (5 seconds each)
        '-loop', '1', '-t', '5', '-i', f'{IMAGES_DIR}/01_pretalk.png',
        '-loop', '1', '-t', '5', '-i', f'{IMAGES_DIR}/02_induction.png',
        '-loop', '1', '-t', '5', '-i', f'{IMAGES_DIR}/05_helm_attunement.png',
        '-loop', '1', '-t', '5', '-i', f'{IMAGES_DIR}/06_gift_download.png',
        # Audio (from induction section - most engaging)
        '-ss', '150', '-t', '20', '-i', f'{SESSION_DIR}/output/atlas_starship_final.mp3',
        '-filter_complex',
        # Scale to vertical 9:16 (1080x1920), crossfade between images, add text
        '''
        [0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30[v0];
        [1:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30[v1];
        [2:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30[v2];
        [3:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30[v3];
        [v0][v1]xfade=transition=fade:duration=0.5:offset=4.5[x1];
        [x1][v2]xfade=transition=fade:duration=0.5:offset=9[x2];
        [x2][v3]xfade=transition=fade:duration=0.5:offset=13.5[vbase];
        [vbase]
        drawtext=text='ATLAS':fontsize=90:fontcolor=white:x=(w-text_w)/2:y=h*0.15:alpha='if(lt(t,1),t,if(lt(t,3),1,if(lt(t,4),4-t,0)))':shadowcolor=black:shadowx=3:shadowy=3,
        drawtext=text='The Starship of the Ancient Future':fontsize=32:fontcolor=white:x=(w-text_w)/2:y=h*0.22:alpha='if(lt(t,1.5),0,if(lt(t,2.5),t-1.5,if(lt(t,4),1,if(lt(t,5),5-t,0))))':shadowcolor=black:shadowx=2:shadowy=2,
        drawtext=text='Deep Theta Meditation':fontsize=48:fontcolor=cyan:x=(w-text_w)/2:y=h*0.45:alpha='if(lt(t,5),0,if(lt(t,6),t-5,if(lt(t,9),1,if(lt(t,10),10-t,0))))':shadowcolor=black:shadowx=2:shadowy=2,
        drawtext=text='432 Hz Binaural Beats':fontsize=36:fontcolor=white:x=(w-text_w)/2:y=h*0.52:alpha='if(lt(t,6),0,if(lt(t,7),t-6,if(lt(t,9),1,if(lt(t,10),10-t,0))))':shadowcolor=black:shadowx=2:shadowy=2,
        drawtext=text='Awaken Your':fontsize=42:fontcolor=white:x=(w-text_w)/2:y=h*0.40:alpha='if(lt(t,10),0,if(lt(t,11),t-10,if(lt(t,14),1,if(lt(t,15),15-t,0))))':shadowcolor=black:shadowx=2:shadowy=2,
        drawtext=text='COSMIC PATTERN':fontsize=54:fontcolor=magenta:x=(w-text_w)/2:y=h*0.47:alpha='if(lt(t,10.5),0,if(lt(t,11.5),t-10.5,if(lt(t,14),1,if(lt(t,15),15-t,0))))':shadowcolor=black:shadowx=3:shadowy=3,
        drawtext=text='RECOGNITION':fontsize=54:fontcolor=magenta:x=(w-text_w)/2:y=h*0.53:alpha='if(lt(t,11),0,if(lt(t,12),t-11,if(lt(t,14),1,if(lt(t,15),15-t,0))))':shadowcolor=black:shadowx=3:shadowy=3,
        drawtext=text='Full Journey on YouTube':fontsize=42:fontcolor=yellow:x=(w-text_w)/2:y=h*0.75:alpha='if(lt(t,15),0,if(lt(t,16),t-15,1))':shadowcolor=black:shadowx=2:shadowy=2,
        drawtext=text='Link in Bio':fontsize=36:fontcolor=white:x=(w-text_w)/2:y=h*0.82:alpha='if(lt(t,16),0,if(lt(t,17),t-16,1))':shadowcolor=black:shadowx=2:shadowy=2,
        fade=t=in:st=0:d=0.5,fade=t=out:st=17:d=1[outv];
        [4:a]afade=t=in:st=0:d=1,afade=t=out:st=17:d=1,volume=1.5[outa]
        ''',
        '-map', '[outv]', '-map', '[outa]',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '256k',
        '-t', '18',
        f'{OUTPUT_DIR}/atlas_tiktok_preview.mp4'
    ]

    print("\nGenerating video...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: {result.stderr[-1500:]}")
        return False

    # Verify output
    output_path = f'{OUTPUT_DIR}/atlas_tiktok_preview.mp4'
    if os.path.exists(output_path):
        size_mb = os.path.getsize(output_path) / (1024 * 1024)

        # Get duration
        probe = subprocess.run([
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'csv=p=0',
            output_path
        ], capture_output=True, text=True)
        duration = float(probe.stdout.strip())

        print(f"\n✓ TikTok preview created!")
        print(f"  File: {output_path}")
        print(f"  Size: {size_mb:.1f} MB")
        print(f"  Duration: {duration:.1f} seconds")
        print(f"  Format: 1080x1920 (9:16 vertical)")
        return True

    return False

if __name__ == "__main__":
    create_tiktok_preview()
