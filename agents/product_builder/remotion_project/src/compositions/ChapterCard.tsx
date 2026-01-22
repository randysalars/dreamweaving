import React from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  spring,
  useVideoConfig,
} from "remotion";

interface ChapterCardProps {
  chapterNumber: number;
  chapterTitle: string;
  keyTakeaway: string;
}

/**
 * Chapter card for social media sharing.
 * Animated 5-second card with chapter info.
 */
export const ChapterCard: React.FC<ChapterCardProps> = ({
  chapterNumber,
  chapterTitle,
  keyTakeaway,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const cardSpring = spring({
    frame,
    fps,
    config: { damping: 20, stiffness: 100 },
  });

  const contentSpring = spring({
    frame: frame - 15,
    fps,
    config: { damping: 18, stiffness: 80 },
  });

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        padding: 60,
        justifyContent: "center",
      }}
    >
      {/* Card */}
      <div
        style={{
          backgroundColor: "#ffffff",
          borderRadius: 24,
          padding: 50,
          boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
          transform: `scale(${cardSpring})`,
        }}
      >
        {/* Chapter badge */}
        <div
          style={{
            display: "inline-block",
            backgroundColor: "#9F7AEA",
            color: "#ffffff",
            padding: "8px 20px",
            borderRadius: 20,
            fontSize: 18,
            fontWeight: 600,
            marginBottom: 20,
            opacity: contentSpring,
          }}
        >
          Chapter {chapterNumber}
        </div>

        {/* Title */}
        <h2
          style={{
            fontSize: 48,
            fontWeight: 700,
            color: "#1a202c",
            marginBottom: 24,
            opacity: contentSpring,
            transform: `translateY(${interpolate(contentSpring, [0, 1], [20, 0])}px)`,
          }}
        >
          {chapterTitle}
        </h2>

        {/* Key takeaway */}
        <p
          style={{
            fontSize: 24,
            color: "#4a5568",
            lineHeight: 1.5,
            opacity: contentSpring,
            transform: `translateY(${interpolate(contentSpring, [0, 1], [15, 0])}px)`,
          }}
        >
          💡 {keyTakeaway}
        </p>

        {/* Branding */}
        <div
          style={{
            marginTop: 30,
            fontSize: 16,
            color: "#9F7AEA",
            fontWeight: 500,
            opacity: contentSpring,
          }}
        >
          SalarsNet • Dreamweaving
        </div>
      </div>
    </AbsoluteFill>
  );
};
