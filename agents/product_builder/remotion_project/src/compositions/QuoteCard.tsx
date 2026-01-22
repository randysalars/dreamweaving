import React from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  spring,
  useVideoConfig,
} from "remotion";

interface QuoteCardProps {
  quote: string;
  author: string;
  context?: string;
  theme?: {
    primaryColor: string;
    backgroundColor: string;
    textColor: string;
  };
}

/**
 * Quote Card Animation
 * Elegant quote display with attribution.
 */
export const QuoteCard: React.FC<QuoteCardProps> = ({
  quote,
  author,
  context,
  theme = {
    primaryColor: "#9F7AEA",
    backgroundColor: "#FAF5FF",
    textColor: "#2D3748",
  },
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const cardSpring = spring({
    frame,
    fps,
    config: { damping: 20, stiffness: 80 },
  });

  const quoteSpring = spring({
    frame: frame - 20,
    fps,
    config: { damping: 15, stiffness: 60 },
  });

  const authorSpring = spring({
    frame: frame - 50,
    fps,
    config: { damping: 15, stiffness: 60 },
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: theme.backgroundColor,
        justifyContent: "center",
        alignItems: "center",
        padding: 100,
      }}
    >
      {/* Quote card */}
      <div
        style={{
          backgroundColor: "#ffffff",
          borderRadius: 24,
          padding: 80,
          maxWidth: 1200,
          boxShadow: "0 20px 60px rgba(0,0,0,0.1)",
          transform: `scale(${cardSpring})`,
          borderLeft: `6px solid ${theme.primaryColor}`,
        }}
      >
        {/* Quote mark */}
        <div
          style={{
            fontSize: 120,
            color: theme.primaryColor,
            opacity: 0.3,
            lineHeight: 0.5,
            marginBottom: -20,
          }}
        >
          "
        </div>

        {/* Quote text */}
        <p
          style={{
            fontSize: 42,
            fontWeight: 500,
            color: theme.textColor,
            lineHeight: 1.5,
            fontStyle: "italic",
            opacity: quoteSpring,
            transform: `translateY(${interpolate(quoteSpring, [0, 1], [20, 0])}px)`,
          }}
        >
          {quote}
        </p>

        {/* Author */}
        <div
          style={{
            marginTop: 40,
            opacity: authorSpring,
            transform: `translateY(${interpolate(authorSpring, [0, 1], [15, 0])}px)`,
          }}
        >
          <span
            style={{
              fontSize: 28,
              fontWeight: 600,
              color: theme.primaryColor,
            }}
          >
            — {author}
          </span>
          {context && (
            <span
              style={{
                fontSize: 22,
                color: theme.textColor,
                opacity: 0.6,
                marginLeft: 12,
              }}
            >
              {context}
            </span>
          )}
        </div>
      </div>
    </AbsoluteFill>
  );
};
