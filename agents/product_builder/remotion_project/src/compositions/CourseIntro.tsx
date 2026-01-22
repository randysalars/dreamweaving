import React from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  spring,
  useVideoConfig,
} from "remotion";

interface CourseIntroProps {
  courseTitle: string;
  subtitle: string;
  authorName: string;
}

/**
 * Course intro animation.
 * 10-second branded opener for course videos.
 */
export const CourseIntro: React.FC<CourseIntroProps> = ({
  courseTitle,
  subtitle,
  authorName,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Background gradient animation
  const gradientRotation = interpolate(frame, [0, 300], [0, 360]);

  // Title animations
  const titleSpring = spring({
    frame: frame - 30,
    fps,
    config: { damping: 15, stiffness: 60 },
  });

  const subtitleSpring = spring({
    frame: frame - 60,
    fps,
    config: { damping: 15, stiffness: 60 },
  });

  const authorSpring = spring({
    frame: frame - 90,
    fps,
    config: { damping: 15, stiffness: 60 },
  });

  // Fade out at end
  const fadeOut = interpolate(frame, [240, 300], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(${gradientRotation}deg, #1a1a2e, #16213e, #0f3460)`,
        opacity: fadeOut,
      }}
    >
      {/* Animated background orbs */}
      <div
        style={{
          position: "absolute",
          width: 600,
          height: 600,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(159,122,234,0.3) 0%, transparent 70%)",
          top: -200,
          right: -100,
          transform: `scale(${1 + Math.sin(frame / 30) * 0.1})`,
        }}
      />
      <div
        style={{
          position: "absolute",
          width: 400,
          height: 400,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(72,187,120,0.2) 0%, transparent 70%)",
          bottom: -100,
          left: -50,
          transform: `scale(${1 + Math.cos(frame / 25) * 0.1})`,
        }}
      />

      {/* Content */}
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
          padding: 80,
        }}
      >
        {/* Course Title */}
        <h1
          style={{
            fontSize: 84,
            fontWeight: 800,
            color: "#ffffff",
            textAlign: "center",
            opacity: titleSpring,
            transform: `translateY(${interpolate(titleSpring, [0, 1], [60, 0])}px)`,
            textShadow: "0 4px 20px rgba(0,0,0,0.3)",
            maxWidth: 1200,
          }}
        >
          {courseTitle}
        </h1>

        {/* Subtitle */}
        <p
          style={{
            fontSize: 36,
            color: "rgba(255,255,255,0.8)",
            marginTop: 30,
            textAlign: "center",
            opacity: subtitleSpring,
            transform: `translateY(${interpolate(subtitleSpring, [0, 1], [40, 0])}px)`,
            fontWeight: 300,
          }}
        >
          {subtitle}
        </p>

        {/* Author */}
        <p
          style={{
            fontSize: 24,
            color: "#9F7AEA",
            marginTop: 60,
            opacity: authorSpring,
            transform: `translateY(${interpolate(authorSpring, [0, 1], [30, 0])}px)`,
            fontWeight: 500,
          }}
        >
          by {authorName}
        </p>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
