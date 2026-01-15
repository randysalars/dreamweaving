import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";

export const metadata: Metadata = {
  title: "Meditation Techniques | Meditation",
  description: "Different meditation methods and how to practice them",
  openGraph: {
    title: "Meditation Techniques",
    description: "Different meditation methods and how to practice them",
    type: "article",
  },
};

const questions = [
  { text: "What is breath awareness meditation and how do I practice it?", slug: "what-is-breath-awareness-meditation-and-how-do-i-practice-it" },
  { text: "What is mindfulness meditation?", slug: "what-is-mindfulness-meditation" },
  { text: "What is loving-kindness meditation (Metta)?", slug: "what-is-loving-kindness-meditation-metta" },
  { text: "What is body scan meditation and how does it work?", slug: "what-is-body-scan-meditation-and-how-does-it-work" },
  { text: "What is mantra meditation?", slug: "what-is-mantra-meditation" },
  { text: "What is walking meditation and how is it different from sitting meditation?", slug: "what-is-walking-meditation-and-how-is-it-different-from-sitting-meditation" },
  { text: "What is guided visualization meditation?", slug: "what-is-guided-visualization-meditation" },
  { text: "Which meditation technique is best for beginners?", slug: "which-meditation-technique-is-best-for-beginners" },
  { text: "How do I choose the right meditation technique for me?", slug: "how-do-i-choose-the-right-meditation-technique-for-me" },
  { text: "Can I combine different meditation techniques?", slug: "can-i-combine-different-meditation-techniques" },
];

export default function TechniquesPage() {
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
          Meditation Techniques
        </h1>
        <p className='text-xl text-muted-foreground mb-12'>
          Different meditation methods and how to practice them
        </p>

        <div className='space-y-4'>
          {questions.map((q) => (
            <Link
              key={q.slug}
              href={`/consciousness/meditation/techniques/${q.slug}`}
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
