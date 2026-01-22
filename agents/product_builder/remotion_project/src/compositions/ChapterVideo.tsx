import React from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  spring,
  Sequence,
} from "remotion";

interface ChapterVideoProps {
  title: string;
  content: string;
  slides: Array<{
    type: "text" | "image" | "diagram";
    content: string;
    duration?: number;
  }>;
  style: Record<string, unknown>;
  theme: {
    primaryColor: string;
    backgroundColor: string;
    textColor: string;
    fontFamily: string;
  };
}

/**
 * Main chapter video composition.
 * Displays title, content slides with animations.
 */
export const ChapterVideo: React.FC<ChapterVideoProps> = ({
  title,
  content,
  slides,
  theme,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Title animation
  const titleSpring = spring({
    frame,
    fps,
    config: { damping: 20, stiffness: 80 },
  });

  const titleOpacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateRight: "clamp",
  });

  const titleY = interpolate(titleSpring, [0, 1], [50, 0]);

  // Content fade in
  const contentOpacity = interpolate(frame, [30, 60], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: theme.backgroundColor,
        fontFamily: theme.fontFamily,
      }}
    >
      {/* Title Section */}
      <Sequence from={0} durationInFrames={90}>
        <AbsoluteFill
          style={{
            justifyContent: "center",
            alignItems: "center",
            padding: 80,
          }}
        >
          <h1
            style={{
              fontSize: 72,
              fontWeight: 700,
              color: theme.textColor,
              opacity: titleOpacity,
              transform: `translateY(${titleY}px)`,
              textAlign: "center",
              maxWidth: 1200,
            }}
          >
            {title}
          </h1>
        </AbsoluteFill>
      </Sequence>

      {/* Content Section */}
      <Sequence from={90}>
        <AbsoluteFill
          style={{
            padding: 80,
            opacity: contentOpacity,
          }}
        >
          <div
            style={{
              fontSize: 32,
              lineHeight: 1.6,
              color: theme.textColor,
              maxWidth: 1400,
              margin: "0 auto",
            }}
          >
            {content.split("\n").map((paragraph, i) => (
              <p key={i} style={{ marginBottom: 24 }}>
                {paragraph}
              </p>
            ))}
          </div>
        </AbsoluteFill>
      </Sequence>

      {/* Slides */}
      {slides.map((slide, index) => {
        const startFrame = 90 + index * 120; // Each slide: 4 seconds
        return (
          <Sequence
            key={index}
            from={startFrame}
            durationInFrames={120}
          >
            <SlideContent slide={slide} theme={theme} />
          </Sequence>
        );
      })}

      {/* Branding footer */}
      <div
        style={{
          position: "absolute",
          bottom: 40,
          right: 60,
          fontSize: 18,
          color: theme.primaryColor,
          opacity: 0.7,
        }}
      >
        SalarsNet • Dreamweaving
      </div>
    </AbsoluteFill>
  );
};

const SlideContent: React.FC<{
  slide: ChapterVideoProps["slides"][0];
  theme: ChapterVideoProps["theme"];
}> = ({ slide, theme }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 15, 105, 120], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        padding: 120,
        opacity,
      }}
    >
      {slide.type === "text" && (
        <div
          style={{
            fontSize: 48,
            fontWeight: 600,
            color: theme.textColor,
            textAlign: "center",
            maxWidth: 1200,
            lineHeight: 1.4,
          }}
        >
          {slide.content}
        </div>
      )}

      {slide.type === "diagram" && (
        <div
          style={{
            width: "80%",
            height: "60%",
            backgroundColor: "#fff",
            borderRadius: 16,
            boxShadow: "0 10px 40px rgba(0,0,0,0.1)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            fontSize: 24,
            color: theme.textColor,
          }}
        >
          {/* Diagram placeholder - would render actual diagram */}
          📊 {slide.content}
        </div>
      )}
    </AbsoluteFill>
  );
};
