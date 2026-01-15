import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";

export const metadata: Metadata = {
  title: "Sleep & Performance | Sleep & Dreams",
  description: "How sleep affects memory, learning, and cognition",
  openGraph: {
    title: "Sleep & Performance",
    description: "How sleep affects memory, learning, and cognition",
    type: "article",
  },
};

const questions = [
  { text: "How does sleep affect memory consolidation?", slug: "how-does-sleep-affect-memory-consolidation" },
  { text: "What is the relationship between sleep and learning?", slug: "what-is-the-relationship-between-sleep-and-learning" },
  { text: "Can you catch up on lost sleep?", slug: "can-you-catch-up-on-lost-sleep" },
  { text: "What are the effects of sleep deprivation?", slug: "what-are-the-effects-of-sleep-deprivation" },
  { text: "How does sleep affect creativity?", slug: "how-does-sleep-affect-creativity" },
  { text: "What is the relationship between sleep and decision-making?", slug: "what-is-the-relationship-between-sleep-and-decision-making" },
  { text: "How does sleep affect athletic performance?", slug: "how-does-sleep-affect-athletic-performance" },
  { text: "Can you learn while sleeping?", slug: "can-you-learn-while-sleeping" },
  { text: "What is the impact of sleep on emotional regulation?", slug: "what-is-the-impact-of-sleep-on-emotional-regulation" },
  { text: "How does sleep deprivation affect reaction time?", slug: "how-does-sleep-deprivation-affect-reaction-time" },
  { text: "What is sleep inertia (grogginess after waking)?", slug: "what-is-sleep-inertia-grogginess-after-waking" },
  { text: "How does sleep affect immune function?", slug: "how-does-sleep-affect-immune-function" },
];

export default function SleepPerformancePage() {
  return (
    <div className='min-h-screen bg-background'>
      <main className='container mx-auto px-4 py-12 max-w-4xl'>
        <Link
          href='/consciousness/sleep-dreams'
          className='text-primary hover:underline mb-6 inline-flex items-center gap-2'
        >
          <ArrowLeft className='h-4 w-4' />
          Back to Sleep & Dreams
        </Link>

        <h1 className='text-4xl md:text-5xl font-bold mb-4 text-foreground'>
          Sleep & Performance
        </h1>
        <p className='text-xl text-muted-foreground mb-12'>
          How sleep affects memory, learning, and cognition
        </p>

        <div className='space-y-4'>
          {questions.map((q) => (
            <Link
              key={q.slug}
              href={`/consciousness/sleep-dreams/sleep-performance/${q.slug}`}
              className='block group'
            >
              <div className='p-6 rounded-xl border border-border bg-card/40 hover:bg-card/60 transition-all hover:scale-[1.02] hover:shadow-md'>
                <div className='flex items-start gap-4'>
                  <div className='p-2 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors'>
                    <HelpCircle className='h-5 w-5 text-primary' />
                  </div>
                  <h2 className='text-lg font-semibold text-foreground group-hover:text-primary transition-colors flex-1'>
                    {q.text}
                  </h2>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}
