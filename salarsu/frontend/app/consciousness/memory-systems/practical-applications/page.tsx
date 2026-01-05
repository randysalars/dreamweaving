import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";

export const metadata: Metadata = {
  title: "Practical Applications | Memory Systems",
  description: "Using memory systems for studying, work, and daily life",
  openGraph: {
    title: "Practical Applications",
    description: "Using memory systems for studying, work, and daily life",
    type: "article",
  },
};

const questions = [
  { text: "How do I memorize for exams effectively?", slug: "how-do-i-memorize-for-exams-effectively" },
  { text: "How can memory systems help with learning languages?", slug: "how-can-memory-systems-help-with-learning-languages" },
  { text: "How do I remember names and faces?", slug: "how-do-i-remember-names-and-faces" },
  { text: "What is the best way to remember presentations without notes?", slug: "what-is-the-best-way-to-remember-presentations-without-notes" },
  { text: "How do I memorize numbers and dates?", slug: "how-do-i-memorize-numbers-and-dates" },
  { text: "How can I use memory systems in professional work?", slug: "how-can-i-use-memory-systems-in-professional-work" },
  { text: "What memory techniques work best for studying technical material?", slug: "what-memory-techniques-work-best-for-studying-technical-material" },
  { text: "How do I remember vocabulary and definitions?", slug: "how-do-i-remember-vocabulary-and-definitions" },
  { text: "Can memory systems help with daily tasks and routines?", slug: "can-memory-systems-help-with-daily-tasks-and-routines" },
  { text: "How do I memorize speeches and scripts?", slug: "how-do-i-memorize-speeches-and-scripts" },
  { text: "What is the best way to remember reading material?", slug: "what-is-the-best-way-to-remember-reading-material" },
  { text: "How can memory systems improve productivity?", slug: "how-can-memory-systems-improve-productivity" },
];

export default function PracticalApplicationsPage() {
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
          Practical Applications
        </h1>
        <p className='text-xl text-muted-foreground mb-12'>
          Using memory systems for studying, work, and daily life
        </p>

        <div className='space-y-4'>
          {questions.map((q) => (
            <Link
              key={q.slug}
              href={`/consciousness/memory-systems/practical-applications/${q.slug}`}
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
