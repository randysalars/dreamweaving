import { Composition } from "remotion";
import { ChapterVideo } from "./compositions/ChapterVideo";
import { AudioNarration } from "./compositions/AudioNarration";
import { CourseIntro } from "./compositions/CourseIntro";
import { ChapterCard } from "./compositions/ChapterCard";

/**
 * Root component that registers all video/audio compositions.
 * These compositions are rendered via the Remotion CLI.
 */
export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* Main chapter video with slides and narration */}
      <Composition
        id="ChapterVideo"
        component={ChapterVideo}
        durationInFrames={900}  // 30 seconds at 30fps
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          title: "Chapter Title",
          content: "Chapter content goes here",
          slides: [],
          style: {},
          theme: {
            primaryColor: "#9F7AEA",
            backgroundColor: "#FAF5FF",
            textColor: "#2D3748",
            fontFamily: "Inter, system-ui, sans-serif",
          },
        }}
      />

      {/* Audio-only narration */}
      <Composition
        id="AudioNarration"
        component={AudioNarration}
        durationInFrames={1800}  // 60 seconds
        fps={30}
        width={1}
        height={1}
        defaultProps={{
          title: "Audio Title",
          audioScript: "Narration script goes here",
          voiceId: "default",
        }}
      />

      {/* Course intro animation */}
      <Composition
        id="CourseIntro"
        component={CourseIntro}
        durationInFrames={300}  // 10 seconds
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          courseTitle: "Course Title",
          subtitle: "Transform your understanding",
          authorName: "SalarsNet",
        }}
      />

      {/* Chapter card for social sharing */}
      <Composition
        id="ChapterCard"
        component={ChapterCard}
        durationInFrames={150}  // 5 seconds
        fps={30}
        width={1200}
        height={630}
        defaultProps={{
          chapterNumber: 1,
          chapterTitle: "Getting Started",
          keyTakeaway: "The most important insight...",
        }}
      />
    </>
  );
};
