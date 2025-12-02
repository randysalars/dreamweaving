#!/bin/bash
set -e

SESSION_DIR="/home/rsalars/Projects/dreamweaving/sessions/iron-soul-forge"
IMG_DIR="$SESSION_DIR/images/uploaded"
OUTPUT_DIR="$SESSION_DIR/output/video"
AUDIO="$SESSION_DIR/output/iron-soul-forge-atlas-enhanced-final.mp3"

# Get audio duration
DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$AUDIO")
echo "Audio duration: $DURATION seconds"

# Images in narrative order
IMAGES=(
    "rsalars_A_warrior_descending_stone_steps_into_a_massive_volca_f3304557-23cc-4681-9b3a-0ef127db21e6_3.png"
    "rsalars_A_massive_anvil_of_black_star-metal_in_the_center_of__473c7485-996c-4947-b221-c653b56b69af_1.png"
    "rsalars_An_ancient_god-smith_seated_on_a_throne_of_cooled_vol_ed6cb5bf-46ec-4564-80a2-afbfdcb7aaa1_0.png"
    "rsalars_Multiple_Hammer_Spirits_striking_in_synchronized_rhyt_7cd35086-ecf0-4dbc-a56a-d70965a3c5f2_0.png"
    "rsalars_A_massive_ceremonial_hammer_made_of_living_fire_strik_d1123801-b7bc-476b-af78-3a530be54ae4_2.png"
    "rsalars_lemental_beings_made_of_living_iron_and_flame_surroun_fb3b6432-958c-4ec8-8b6d-c618cb203d33_0.png"
    "rsalars_Human_hands_pressed_against_a_black_star-metal_anvil__4e17db8e-e050-4f8e-82f2-12f257894d9f_0.png"
    "rsalars_A_human_figure_standing_before_the_Soul_Forge_with_an_15a182dc-1250-4747-8389-11cedc452e60_3.png"
    "rsalars_A_dramatic_close-up_of_the_black_star-metal_anvil_wit_5da95af4-2810-409a-9fee-b1bca41537ee_3.png"
    "rsalars_A_warrior_figure_made_of_tempered_steel_emerging_from_5cb1e732-c11b-4708-867d-aa83fd337211_2.png"
    "rsalars_A_warrior_ascending_stone_steps_from_a_volcanic_caver_adf09c65-dab5-46e6-a415-f2f2a8d46fb8_3.png"
)

NUM_IMAGES=${#IMAGES[@]}
# Use integer math - 1800/11 = 163 seconds per image
IMAGE_DURATION=163
FADE_DURATION=3

echo "Number of images: $NUM_IMAGES"
echo "Duration per image: $IMAGE_DURATION seconds"

# Create a concat file for FFmpeg
CONCAT_FILE="$OUTPUT_DIR/concat.txt"
rm -f "$CONCAT_FILE"

for img in "${IMAGES[@]}"; do
    echo "file '$IMG_DIR/$img'" >> "$CONCAT_FILE"
    echo "duration $IMAGE_DURATION" >> "$CONCAT_FILE"
done
# Add last image again (required by concat demuxer)
echo "file '$IMG_DIR/${IMAGES[-1]}'" >> "$CONCAT_FILE"

echo "Concat file created at $CONCAT_FILE"
cat "$CONCAT_FILE"

echo ""
echo "Building video with crossfades..."

# Simpler approach: scale images, concat, add audio
ffmpeg -y \
    -f concat -safe 0 -i "$CONCAT_FILE" \
    -i "$AUDIO" \
    -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30" \
    -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
    -c:a aac -b:a 192k \
    -shortest \
    "$OUTPUT_DIR/iron-soul-forge-final.mp4"

echo ""
echo "Video created: $OUTPUT_DIR/iron-soul-forge-final.mp4"
