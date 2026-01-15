import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";

export const metadata: Metadata = {
  title: "Getting Started with Meditation | Meditation",
  description: "Essential guidance for beginners starting a meditation practice",
  openGraph: {
    title: "Getting Started with Meditation",
    description: "Essential guidance for beginners starting a meditation practice",
    type: "article",
  },
};

const questions = [
  { text: "What is meditation and how does it work?", slug: "what-is-meditation-and-how-does-it-work" },
  { text: "How do I start a meditation practice as a complete beginner?", slug: "how-do-i-start-a-meditation-practice-as-a-complete-beginner" },
  { text: "How long should I meditate each day when starting out?", slug: "how-long-should-i-meditate-each-day-when-starting-out" },
  { text: "Do I need special equipment or training to meditate?", slug: "do-i-need-special-equipment-or-training-to-meditate" },
  { text: "What is the best time of day to meditate?", slug: "what-is-the-best-time-of-day-to-meditate" },
  { text: "Should I meditate sitting, lying down, or walking?", slug: "should-i-meditate-sitting-lying-down-or-walking" },
  { text: "What are the most common beginner mistakes in meditation?", slug: "what-are-the-most-common-beginner-mistakes-in-meditation" },
  { text: "How do I know if I am meditating correctly?", slug: "how-do-i-know-if-i-am-meditating-correctly" },
];

export default function GettingStartedPage() {
  return (
    <div className='min-h-screen bg-background'>
      <main className='container mx-auto px-4 py-12 max-w-4xl'>
        <Link
          href='/consciousness/meditation'
          className='text-primary hover:underline mb-6 inline-flex items-center gap-2'
        >
          <ArrowLeft className='h-4 w-4' />
          Back to Meditation
        </Link>

        <h1 className='text-4xl md:text-5xl font-bold mb-4 text-foreground'>
          Getting Started with Meditation
        </h1>
        <p className='text-xl text-muted-foreground mb-12'>
          Essential guidance for beginners starting a meditation practice
        </p>

        <div className='space-y-4'>
          {questions.map((q) => (
            <Link
              key={q.slug}
              href={`/consciousness/meditation/getting-started/${q.slug}`}
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
