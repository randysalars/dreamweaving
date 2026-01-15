import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";

export const metadata: Metadata = {
  title: "Dream Work & Interpretation | Sleep & Dreams",
  description: "Working with dreams for insight and growth",
  openGraph: {
    title: "Dream Work & Interpretation",
    description: "Working with dreams for insight and growth",
    type: "article",
  },
};

const questions = [
  { text: "How do I interpret my dreams?", slug: "how-do-i-interpret-my-dreams" },
  { text: "What is dream journaling and how do I start?", slug: "what-is-dream-journaling-and-how-do-i-start" },
  { text: "Do recurring dreams mean something?", slug: "do-recurring-dreams-mean-something" },
  { text: "What are archetypes in dreams?", slug: "what-are-archetypes-in-dreams" },
  { text: "What is active imagination in dream work?", slug: "what-is-active-imagination-in-dream-work" },
  { text: "Can dreams provide creative insights?", slug: "can-dreams-provide-creative-insights" },
  { text: "What are common dream symbols and their meanings?", slug: "what-are-common-dream-symbols-and-their-meanings" },
  { text: "How do I work with nightmares therapeutically?", slug: "how-do-i-work-with-nightmares-therapeutically" },
  { text: "What is dream incubation?", slug: "what-is-dream-incubation" },
  { text: "How can dreams support personal growth?", slug: "how-can-dreams-support-personal-growth" },
];

export default function DreamWorkPage() {
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
          Dream Work & Interpretation
        </h1>
        <p className='text-xl text-muted-foreground mb-12'>
          Working with dreams for insight and growth
        </p>

        <div className='space-y-4'>
          {questions.map((q) => (
            <Link
              key={q.slug}
              href={`/consciousness/sleep-dreams/dream-work/${q.slug}`}
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
