import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";

export const metadata: Metadata = {
  title: "Modern Memory Approaches | Memory Systems",
  description: "Spaced repetition, digital tools, and scientific methods",
  openGraph: {
    title: "Modern Memory Approaches",
    description: "Spaced repetition, digital tools, and scientific methods",
    type: "article",
  },
};

const questions = [
  { text: "What is spaced repetition and why does it work?", slug: "what-is-spaced-repetition-and-why-does-it-work" },
  { text: "How does the Leitner system improve memorization?", slug: "how-does-the-leitner-system-improve-memorization" },
  { text: "What is active recall and how is it different from re-reading?", slug: "what-is-active-recall-and-how-is-it-different-from-re-reading" },
  { text: "Which memory apps are most effective (Anki, Quizlet, etc.)?", slug: "which-memory-apps-are-most-effective-anki-quizlet-etc" },
  { text: "What is the testing effect in memory science?", slug: "what-is-the-testing-effect-in-memory-science" },
  { text: "How does interleaving improve long-term retention?", slug: "how-does-interleaving-improve-long-term-retention" },
  { text: "What is elaborative interrogation for memory?", slug: "what-is-elaborative-interrogation-for-memory" },
  { text: "How do digital flashcards compare to physical ones?", slug: "how-do-digital-flashcards-compare-to-physical-ones" },
  { text: "What is the Feynman Technique for learning and memory?", slug: "what-is-the-feynman-technique-for-learning-and-memory" },
  { text: "How does mind mapping enhance memory?", slug: "how-does-mind-mapping-enhance-memory" },
];

export default function ModernApproachesPage() {
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
          Modern Memory Approaches
        </h1>
        <p className='text-xl text-muted-foreground mb-12'>
          Spaced repetition, digital tools, and scientific methods
        </p>

        <div className='space-y-4'>
          {questions.map((q) => (
            <Link
              key={q.slug}
              href={`/consciousness/memory-systems/modern-approaches/${q.slug}`}
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
