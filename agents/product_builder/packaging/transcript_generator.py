"""
Transcript Generator
Creates subtitles (SRT) and searchable transcripts from audio/video content.
"""

import logging
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)


@dataclass
class TranscriptSegment:
    """Single segment of a transcript."""
    start_time: float  # Seconds
    end_time: float
    text: str
    speaker: str = ""
    
    def to_srt_time(self, seconds: float) -> str:
        """Convert seconds to SRT time format (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def to_srt(self, index: int) -> str:
        """Convert to SRT format."""
        return f"""{index}
{self.to_srt_time(self.start_time)} --> {self.to_srt_time(self.end_time)}
{self.text}
"""


@dataclass
class Transcript:
    """Complete transcript with segments."""
    title: str
    segments: List[TranscriptSegment]
    
    @property
    def full_text(self) -> str:
        """Get complete transcript as plain text."""
        return "\n".join(seg.text for seg in self.segments)
    
    @property
    def duration_seconds(self) -> float:
        """Total duration in seconds."""
        if not self.segments:
            return 0
        return self.segments[-1].end_time
    
    @property
    def word_count(self) -> int:
        """Total word count."""
        return len(self.full_text.split())


class TranscriptGenerator:
    """
    Generates subtitles and transcripts.
    
    Supports:
    - SRT format (subtitles)
    - VTT format (web subtitles)
    - Plain text transcripts
    - Searchable HTML transcripts
    """
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("./transcripts")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_from_audio(
        self,
        audio_path: str,
        title: str = "Transcript"
    ) -> Transcript:
        """
        Generate transcript from audio file using speech recognition.
        
        Requires: whisper or similar STT engine
        """
        logger.info(f"🎙️ Transcribing: {audio_path}")
        
        try:
            # Try using OpenAI Whisper
            import whisper
            
            model = whisper.load_model("base")
            result = model.transcribe(audio_path)
            
            segments = []
            for seg in result.get("segments", []):
                segments.append(TranscriptSegment(
                    start_time=seg["start"],
                    end_time=seg["end"],
                    text=seg["text"].strip()
                ))
            
            logger.info(f"✅ Transcribed {len(segments)} segments")
            return Transcript(title=title, segments=segments)
            
        except ImportError:
            logger.warning("Whisper not installed. Using placeholder.")
            return self._create_placeholder_transcript(title)
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return self._create_placeholder_transcript(title)
    
    def generate_from_script(
        self,
        script: str,
        title: str = "Transcript",
        words_per_minute: int = 150
    ) -> Transcript:
        """
        Generate timed transcript from a script.
        Uses average speaking pace to estimate timing.
        """
        logger.info(f"📝 Generating transcript from script...")
        
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', script)
        
        segments = []
        current_time = 0.0
        
        for sentence in sentences:
            if not sentence.strip():
                continue
            
            word_count = len(sentence.split())
            duration = (word_count / words_per_minute) * 60  # seconds
            
            segments.append(TranscriptSegment(
                start_time=current_time,
                end_time=current_time + duration,
                text=sentence.strip()
            ))
            
            current_time += duration
        
        logger.info(f"✅ Generated {len(segments)} segments ({current_time:.1f}s)")
        return Transcript(title=title, segments=segments)
    
    def export_srt(self, transcript: Transcript, output_name: str = None) -> str:
        """Export transcript to SRT format."""
        output_name = output_name or transcript.title.replace(" ", "_").lower()
        output_path = self.output_dir / f"{output_name}.srt"
        
        content = ""
        for i, segment in enumerate(transcript.segments, 1):
            content += segment.to_srt(i) + "\n"
        
        output_path.write_text(content)
        logger.info(f"✅ SRT exported: {output_path}")
        return str(output_path)
    
    def export_vtt(self, transcript: Transcript, output_name: str = None) -> str:
        """Export transcript to WebVTT format."""
        output_name = output_name or transcript.title.replace(" ", "_").lower()
        output_path = self.output_dir / f"{output_name}.vtt"
        
        content = "WEBVTT\n\n"
        for i, segment in enumerate(transcript.segments, 1):
            start = self._seconds_to_vtt_time(segment.start_time)
            end = self._seconds_to_vtt_time(segment.end_time)
            content += f"{start} --> {end}\n{segment.text}\n\n"
        
        output_path.write_text(content)
        logger.info(f"✅ VTT exported: {output_path}")
        return str(output_path)
    
    def export_text(self, transcript: Transcript, output_name: str = None) -> str:
        """Export transcript as plain text."""
        output_name = output_name or transcript.title.replace(" ", "_").lower()
        output_path = self.output_dir / f"{output_name}.txt"
        
        content = f"# {transcript.title}\n\n"
        content += f"Duration: {self._format_duration(transcript.duration_seconds)}\n"
        content += f"Words: {transcript.word_count}\n\n"
        content += "---\n\n"
        content += transcript.full_text
        
        output_path.write_text(content)
        logger.info(f"✅ Text exported: {output_path}")
        return str(output_path)
    
    def export_searchable_html(self, transcript: Transcript, output_name: str = None) -> str:
        """Export transcript as searchable HTML with timestamps."""
        output_name = output_name or transcript.title.replace(" ", "_").lower()
        output_path = self.output_dir / f"{output_name}.html"
        
        segments_html = ""
        for segment in transcript.segments:
            time_str = self._format_duration(segment.start_time)
            segments_html += f"""
        <div class="segment" data-time="{segment.start_time}">
            <span class="timestamp">[{time_str}]</span>
            <span class="text">{segment.text}</span>
        </div>"""
        
        content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{transcript.title} - Transcript</title>
    <style>
        body {{ font-family: system-ui, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #1a202c; }}
        .meta {{ color: #718096; margin-bottom: 20px; }}
        .search {{ width: 100%; padding: 12px; font-size: 16px; margin-bottom: 20px; border: 1px solid #e2e8f0; border-radius: 8px; }}
        .segment {{ padding: 8px 0; border-bottom: 1px solid #f7fafc; }}
        .segment:hover {{ background: #f7fafc; }}
        .timestamp {{ color: #9F7AEA; font-family: monospace; margin-right: 12px; cursor: pointer; }}
        .text {{ color: #2d3748; }}
        .highlight {{ background: yellow; }}
    </style>
</head>
<body>
    <h1>{transcript.title}</h1>
    <div class="meta">
        Duration: {self._format_duration(transcript.duration_seconds)} | 
        Words: {transcript.word_count}
    </div>
    <input type="text" class="search" placeholder="Search transcript..." id="search">
    <div class="transcript">
        {segments_html}
    </div>
    <script>
        document.getElementById('search').addEventListener('input', function(e) {{
            const query = e.target.value.toLowerCase();
            document.querySelectorAll('.segment').forEach(seg => {{
                const text = seg.querySelector('.text');
                if (query && text.textContent.toLowerCase().includes(query)) {{
                    seg.style.display = 'block';
                    text.innerHTML = text.textContent.replace(
                        new RegExp('(' + query + ')', 'gi'),
                        '<span class="highlight">$1</span>'
                    );
                }} else if (query) {{
                    seg.style.display = 'none';
                }} else {{
                    seg.style.display = 'block';
                    text.innerHTML = text.textContent;
                }}
            }});
        }});
    </script>
</body>
</html>"""
        
        output_path.write_text(content)
        logger.info(f"✅ HTML transcript exported: {output_path}")
        return str(output_path)
    
    def _seconds_to_vtt_time(self, seconds: float) -> str:
        """Convert seconds to VTT time format (HH:MM:SS.mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration nicely."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        if minutes > 60:
            hours = minutes // 60
            minutes = minutes % 60
            return f"{hours}h {minutes}m {secs}s"
        return f"{minutes}m {secs}s"
    
    def _create_placeholder_transcript(self, title: str) -> Transcript:
        """Create a placeholder transcript."""
        return Transcript(
            title=title,
            segments=[
                TranscriptSegment(
                    start_time=0,
                    end_time=5,
                    text="[Transcript generation requires whisper: pip install openai-whisper]"
                )
            ]
        )
