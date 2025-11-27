#!/usr/bin/env python3
"""
Generate enhanced voice track V2 with complete pretalk and closing
Uses chunked generation for the larger script file
"""

import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'scripts/core'))

# Import the chunked generator
from generate_audio_chunked import synthesize_ssml_file_chunked, print_header

def main():
    """Generate enhanced voice V2 with chunking"""

    print_header()

    ssml_file = "working_files/voice_script_enhanced_v2.ssml"
    output_file = "working_files/voice_neural_navigator_enhanced_v2.mp3"
    voice_name = "en-US-Wavenet-C"  # Natural female voice (WaveNet)

    print("=" * 70)
    print("   Enhanced Version 2: Complete Pretalk & Closing")
    print("=" * 70)
    print()
    print("Enhancements:")
    print("  • Detailed explanation of journey benefits in pretalk")
    print("  • Proper countdown from 1-10 for awakening")
    print("  • 5 post-hypnotic anchors for daily use")
    print("  • Sleep/dream suggestions for continued integration")
    print("  • Extended pauses on transitions")
    print("  • Full-duration journey content")
    print()

    synthesize_ssml_file_chunked(ssml_file, output_file, voice_name)

    return 0

if __name__ == "__main__":
    exit(main())
