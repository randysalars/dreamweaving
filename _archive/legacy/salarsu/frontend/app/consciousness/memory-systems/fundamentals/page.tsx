import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";

export const metadata: Metadata = {
  title: "Memory Fundamentals | Memory Systems",
  description: "How memory works and core principles",
  openGraph: {
    title: "Memory Fundamentals",
    description: "How memory works and core principles",
    type: "article",
  },
};

const questions = [
  { text: "What are the different types of memory (short-term, long-term, working)?", slug: "what-are-the-different-types-of-memory-short-term-long-term-working" },
  { text: "How does the brain encode and retrieve memories?", slug: "how-does-the-brain-encode-and-retrieve-memories" },
  { text: "What is the role of repetition in memory formation?", slug: "what-is-the-role-of-repetition-in-memory-formation" },
  { text: "Can memory be improved with practice?", slug: "can-memory-be-improved-with-practice" },
  { text: "What is working memory and why is it important?", slug: "what-is-working-memory-and-why-is-it-important" },
  { text: "How does attention affect memory formation?", slug: "how-does-attention-affect-memory-formation" },
  { text: "What is the difference between recognition and recall?", slug: "what-is-the-difference-between-recognition-and-recall" },
  { text: "How do emotions influence memory?", slug: "how-do-emotions-influence-memory" },
  { text: "What causes forgetting and how can it be prevented?", slug: "what-causes-forgetting-and-how-can-it-be-prevented" },
  { text: "How does sleep affect memory consolidation?", slug: "how-does-sleep-affect-memory-consolidation" },
];

export default function FundamentalsPage() {
  return (
    <div className='min-h-screen bg-background'>
      <main className='container mx-auto px-4 py-12 max-w-4xl'>
        <Link
          href='/consciousness/memory-systems'
          className='text-primary hover:underline mb-6 inline-flex items-center gap-2'
        >
          <ArrowLeft className='h-4 w-4' />
          Back to Memory Systems
        </Link>

        <h1 className='text-4xl md:text-5xl font-bold mb-4 text-foreground'>
          Memory Fundamentals
        </h1>
        <p className='text-xl text-muted-foreground mb-12'>
          How memory works and core principles
        </p>

        <div className='space-y-4'>
          {questions.map((q) => (
            <Link
              key={q.slug}
              href={`/consciousness/memory-systems/fundamentals/${q.slug}`}
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
