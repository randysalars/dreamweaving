import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";

export const metadata: Metadata = {
  title: "Deepening Your Practice | Meditation",
  description: "Progressing beyond basics and building a sustainable practice",
  openGraph: {
    title: "Deepening Your Practice",
    description: "Progressing beyond basics and building a sustainable practice",
    type: "article",
  },
};

const questions = [
  { text: "How do I progress from beginner to intermediate meditation?", slug: "how-do-i-progress-from-beginner-to-intermediate-meditation" },
  { text: "What are different meditation states (concentration vs insight)?", slug: "what-are-different-meditation-states-concentration-vs-insight" },
  { text: "How do I build consistency in my meditation practice?", slug: "how-do-i-build-consistency-in-my-meditation-practice" },
  { text: "When should I seek a meditation teacher or join a group?", slug: "when-should-i-seek-a-meditation-teacher-or-join-a-group" },
  { text: "How do I integrate meditation into daily life?", slug: "how-do-i-integrate-meditation-into-daily-life" },
  { text: "What is the difference between formal meditation and mindfulness?", slug: "what-is-the-difference-between-formal-meditation-and-mindfulness" },
  { text: "How do I deepen my meditation practice beyond technique?", slug: "how-do-i-deepen-my-meditation-practice-beyond-technique" },
  { text: "What are advanced meditation practices?", slug: "what-are-advanced-meditation-practices" },
];

export default function DeepeningPracticePage() {
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
          Deepening Your Practice
        </h1>
        <p className='text-xl text-muted-foreground mb-12'>
          Progressing beyond basics and building a sustainable practice
        </p>

        <div className='space-y-4'>
          {questions.map((q) => (
            <Link
              key={q.slug}
              href={`/consciousness/meditation/deepening-practice/${q.slug}`}
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
