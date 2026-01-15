import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, Layers, HelpCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/meditation`;

export const metadata: Metadata = {
  title: "Meditation | Salars Consciousness",
  description: "Explore meditation practices, techniques, benefits, and 40+ common questions. Meditation is a foundational practice for expanding awareness, cultivating focus, and fostering emotional balance.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Meditation | Salars Consciousness",
    description: "Explore meditation practices, techniques, benefits, and 40+ common questions. Meditation is a foundational practice for expanding awareness, cultivating focus, and fostering emotional balance.",
    url: pageUrl,
    type: "article",
  },
  keywords: ["meditation", "mindfulness", "breath awareness", "meditation techniques", "meditation benefits", "how to meditate", "meditation for beginners", "meditation science"],
};

const categories = [
  {
    slug: "getting-started",
    name: "Getting Started with Meditation",
    description: "Essential guidance for beginners starting a meditation practice",
    count: 8,
  },
  {
    slug: "techniques",
    name: "Meditation Techniques",
    description: "Different meditation methods and how to practice them",
    count: 10,
  },
  {
    slug: "benefits-science",
    name: "Benefits & Science of Meditation",
    description: "Research-backed benefits and neuroscience of meditation",
    count: 8,
  },
  {
    slug: "challenges",
    name: "Common Challenges",
    description: "Overcoming obstacles and difficulties in meditation practice",
    count: 8,
  },
  {
    slug: "deepening-practice",
    name: "Deepening Your Practice",
    description: "Progressing beyond basics and building a sustainable practice",
    count: 8,
  },
];

export default function MeditationPage() {
  const totalQuestions = categories.reduce((sum, cat) => sum + cat.count, 0);

  return (
    <div className='min-h-screen bg-background'>
      <div className='container mx-auto px-4 py-8'>
        <Link
          href='/consciousness'
          className='text-primary hover:underline mb-4 inline-block'
        >
          &larr; Back to Consciousness
        </Link>
        <h1 className='text-4xl md:text-5xl font-bold mb-6 text-foreground'>
          Meditation
        </h1>
        <p className='text-lg text-foreground mb-4'>
          Meditation is a foundational practice for expanding awareness,
          cultivating focus, and fostering emotional balance. It involves training
          the mind to observe thoughts, sensations, and emotions with clarity and
          equanimity. Meditation is both ancient and modern, practiced in many
          forms across cultures for well-being, insight, and spiritual growth.
        </p>
        <div className='mb-12 bg-card/70 text-card-foreground border p-8 rounded-lg'>
          <h2 className='text-3xl font-bold mb-6 text-foreground'>
            What Is Meditation?
          </h2>
          <p className='text-lg text-foreground mb-4'>
            Meditation is the art of paying attention—intentionally focusing your
            awareness, often on the breath, a mantra, or the present moment. It
            can be practiced sitting, walking, lying down, or even during daily
            activities. The goal is not to stop thoughts, but to relate to them
            with greater calm, curiosity, and compassion.
          </p>
          <h2 className='text-3xl font-bold mb-6 text-foreground'>
            Benefits of Meditation
          </h2>
          <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3'>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                Improves attention and concentration
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                Reduces stress and anxiety
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                Enhances emotional regulation and resilience
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                Supports cognitive flexibility and creativity
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                Promotes better sleep and physical health
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                Deepens self-awareness and spiritual connection
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                Fosters compassion and empathy for self and others
              </span>
            </div>
          </div>
          <h2 className='text-3xl font-bold mb-6 text-foreground mt-8'>
            Popular Meditation Techniques
          </h2>
          <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3'>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                <strong>Breath Awareness:</strong> Focus on the natural rhythm of
                your breath, returning gently whenever the mind wanders.
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                <strong>Mindfulness Meditation:</strong> Observe thoughts,
                sensations, and emotions as they arise, without judgment or
                attachment.
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                <strong>Loving-Kindness (Metta):</strong> Cultivate goodwill and
                compassion for yourself and others through silent phrases or
                visualization.
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                <strong>Body Scan:</strong> Bring awareness to each part of the
                body, noticing sensations and releasing tension.
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                <strong>Guided Visualization:</strong> Use imagery and suggestion
                to explore inner landscapes or promote relaxation.
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                <strong>Mantra Meditation:</strong> Repeat a word, phrase, or
                sound to anchor attention and quiet the mind.
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                <strong>Walking Meditation:</strong> Practice mindful movement,
                focusing on each step and the sensations of walking.
              </span>
            </div>
          </div>
          <h2 className='text-3xl font-bold mb-6 text-foreground mt-8'>
            Getting Started
          </h2>
          <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3'>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                Begin with simple breath awareness or guided meditations.
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                Start with short sessions (5–10 minutes) and gradually increase
                the duration.
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                Find a quiet, comfortable space where you won't be disturbed.
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                Use a timer or meditation app to help you stay on track.
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                Be patient and gentle with yourself—wandering thoughts are normal.
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                Consistency is more important than duration—just a few minutes a
                day can yield noticeable benefits.
              </span>
            </div>
          </div>
          <h2 className='text-3xl font-bold mb-6 text-foreground mt-8'>
            Tips for a Sustainable Practice
          </h2>
          <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3'>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                Try different techniques to discover what resonates with you.
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                Pair meditation with another habit (like morning coffee or
                bedtime) to make it routine.
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                Keep a journal to track your experiences, insights, and progress.
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                Join a meditation group or class for support and accountability.
              </span>
            </div>
          </div>
          <h2 className='text-3xl font-bold mb-6 text-foreground mt-8'>
            Common Challenges and How to Overcome Them
          </h2>
          <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3'>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                <strong>Restlessness:</strong> If you feel fidgety, try walking
                meditation or focus on body sensations.
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                <strong>Sleepiness:</strong> Meditate sitting up with an alert
                posture, or try shorter sessions.
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                <strong>Busy Mind:</strong> Remember, the goal is not to empty the
                mind, but to notice thoughts and return to your anchor.
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                <strong>Lack of Time:</strong> Even one mindful breath or a minute
                of stillness can make a difference.
              </span>
            </div>
          </div>
          <h2 className='text-3xl font-bold mb-6 text-foreground mt-8'>
            Further Exploration
          </h2>
          <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3'>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                <a
                  href='https://www.mindful.org/meditation/mindfulness-getting-started/'
                  target='_blank'
                  rel='noopener noreferrer'
                  className='text-primary hover:underline'
                >
                  Mindful.org – Meditation for Beginners
                </a>
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                <a
                  href='https://www.headspace.com/meditation/meditation-for-beginners'
                  target='_blank'
                  rel='noopener noreferrer'
                  className='text-primary hover:underline'
                >
                  Headspace – Meditation for Beginners
                </a>
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                <a
                  href='https://www.tarabrach.com/guided-meditations/'
                  target='_blank'
                  rel='noopener noreferrer'
                  className='text-primary hover:underline'
                >
                  Tara Brach – Guided Meditations
                </a>
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                <a
                  href='https://insighttimer.com/'
                  target='_blank'
                  rel='noopener noreferrer'
                  className='text-primary hover:underline'
                >
                  Insight Timer – Free Meditation App
                </a>
              </span>
            </div>
          </div>
          <h2 className='text-3xl font-bold mb-6 text-foreground mt-8'>
            Quotes on Meditation
          </h2>
          <blockquote className='border-l-4 border-primary pl-4 my-4 italic text-lg text-foreground'>
            "Meditation is not evasion; it is a serene encounter with reality." —
            Thich Nhat Hanh
          </blockquote>
          <blockquote className='border-l-4 border-primary pl-4 my-4 italic text-lg text-foreground'>
            "You should sit in meditation for twenty minutes every day—unless
            you're too busy; then you should sit for an hour." — Zen proverb
          </blockquote>
          <blockquote className='border-l-4 border-primary pl-4 my-4 italic text-lg text-foreground'>
            "The thing about meditation is: You become more and more you." — David
            Lynch
          </blockquote>
        </div>

        <Separator className='my-16' />

        {/* Question Hub Section */}
        <section className='py-8'>
          <div className='text-center mb-12'>
            <Badge variant='outline' className='mb-4'>
              Question Hub
            </Badge>
            <h2 className='text-4xl md:text-5xl font-bold text-foreground mb-6'>
              Explore Common Questions About Meditation
            </h2>
            <p className='text-xl text-muted-foreground max-w-3xl mx-auto'>
              {totalQuestions} answers to help deepen your understanding and practice
            </p>
          </div>

          <div className='grid gap-6 md:grid-cols-2 lg:grid-cols-3 max-w-6xl mx-auto'>
            {categories.map((category) => (
              <Link
                key={category.slug}
                href={`/consciousness/meditation/${category.slug}`}
                className='group'
              >
                <div className='h-full p-6 rounded-2xl border border-border bg-card/40 hover:bg-card/60 transition-all hover:scale-105 hover:shadow-lg'>
                  <div className='flex items-center gap-3 mb-3'>
                    <div className='p-2 rounded-lg bg-primary/10'>
                      <Layers className='h-5 w-5 text-primary' />
                    </div>
                    <h3 className='text-xl font-semibold text-foreground group-hover:text-primary transition-colors'>
                      {category.name}
                    </h3>
                  </div>
                  <p className='text-sm text-muted-foreground mb-4'>
                    {category.description}
                  </p>
                  <div className='flex items-center gap-2 text-sm text-primary'>
                    <HelpCircle className='h-4 w-4' />
                    <span>{category.count} questions</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
