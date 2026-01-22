import { Composition } from "remotion";
import { ChapterVideo } from "./compositions/ChapterVideo";
import { AudioNarration } from "./compositions/AudioNarration";
import { CourseIntro } from "./compositions/CourseIntro";
import { ChapterCard } from "./compositions/ChapterCard";
import { KeyInsight } from "./compositions/KeyInsight";
import { Checklist } from "./compositions/Checklist";
import { QuoteCard } from "./compositions/QuoteCard";
import { ProgressMilestone } from "./compositions/ProgressMilestone";

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
        durationInFrames={900}
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
        durationInFrames={1800}
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
        durationInFrames={300}
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
        durationInFrames={150}
        fps={30}
        width={1200}
        height={630}
        defaultProps={{
          chapterNumber: 1,
          chapterTitle: "Getting Started",
          keyTakeaway: "The most important insight...",
        }}
      />

      {/* Key Insight highlight */}
      <Composition
        id="KeyInsight"
        component={KeyInsight}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          insightText: "The key insight goes here",
          context: "Context name",
          chapterNumber: 1,
        }}
      />

      {/* Animated Checklist */}
      <Composition
        id="Checklist"
        component={Checklist}
        durationInFrames={300}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          title: "Action Steps",
          items: ["Step one", "Step two", "Step three"],
        }}
      />

      {/* Quote Card */}
      <Composition
        id="QuoteCard"
        component={QuoteCard}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          quote: "The quote goes here",
          author: "Author Name",
          context: "Book Title",
        }}
      />

      {/* Progress Milestone */}
      <Composition
        id="ProgressMilestone"
        component={ProgressMilestone}
        durationInFrames={360}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          milestones: [
            { name: "Foundation", description: "Core concepts", completed: true },
            { name: "Application", description: "First practice", completed: true },
            { name: "Mastery", description: "Full implementation", completed: false },
          ],
          currentMilestone: 2,
        }}
      />
    </>
  );
};

