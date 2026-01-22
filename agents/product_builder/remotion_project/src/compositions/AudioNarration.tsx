import React from "react";
import { AbsoluteFill, Audio, staticFile } from "remotion";

interface AudioNarrationProps {
  title: string;
  audioScript: string;
  voiceId: string;
}

/**
 * Audio-only composition for narration.
 * Can be combined with TTS or pre-recorded audio.
 */
export const AudioNarration: React.FC<AudioNarrationProps> = ({
  title,
  audioScript,
  voiceId,
}) => {
  // In a full implementation, this would:
  // 1. Call a TTS API (ElevenLabs, OpenAI, etc.) to generate audio
  // 2. Load the generated audio file
  // 3. Return a composition with just audio

  // For now, we output nothing visible (audio-only composition)
  return (
    <AbsoluteFill style={{ backgroundColor: "transparent" }}>
      {/* 
        Audio would be added here:
        <Audio src={generatedAudioUrl} />
        
        The audio generation happens in the Python layer before rendering.
        The audioScript prop contains the text to synthesize.
      */}
      
      {/* Metadata for debugging */}
      <div style={{ display: "none" }}>
        <p>Title: {title}</p>
        <p>Script: {audioScript}</p>
        <p>Voice: {voiceId}</p>
      </div>
    </AbsoluteFill>
  );
};
