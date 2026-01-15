import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, Layers, HelpCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/memory-systems`;

export const metadata: Metadata = {
  title: "Memory Systems | Salars Consciousness",
  description: "Ancient and modern techniques for enhancing memory through association, visualization, and spatial organization. Explore 55+ questions about memory improvement, mnemonic devices, and advanced memory techniques.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Memory Systems | Salars Consciousness",
    description: "Ancient and modern techniques for enhancing memory through association, visualization, and spatial organization. Explore 55+ questions about memory improvement.",
    url: pageUrl,
    type: "article",
  },
  keywords: [
    "memory systems",
    "memory palace",
    "mnemonic devices",
    "spaced repetition",
    "memory improvement",
    "memory techniques",
    "method of loci",
    "chunking",
    "active recall",
    "memory training",
  ],
};

const categories = [
  {
    slug: "fundamentals",
    name: "Memory Fundamentals",
    description: "How memory works and core principles",
    count: 10,
  },
  {
    slug: "classic-techniques",
    name: "Classic Memory Techniques",
    description: "Time-tested methods like Memory Palace and mnemonics",
    count: 12,
  },
  {
    slug: "modern-approaches",
    name: "Modern Memory Approaches",
    description: "Spaced repetition, digital tools, and scientific methods",
    count: 10,
  },
  {
    slug: "practical-applications",
    name: "Practical Applications",
    description: "Using memory systems for studying, work, and daily life",
    count: 12,
  },
  {
    slug: "advanced-practice",
    name: "Advanced Practice",
    description: "Competition techniques, mastery, and optimization",
    count: 11,
  },
];

export default function MemorySystemsPage() {
  const totalQuestions = categories.reduce((sum, cat) => sum + cat.count, 0);

  return (
    <div className='min-h-screen bg-background'>
      <div className='container mx-auto px-4 py-8'>
        <Link
          href='/consciousness'
          className='text-primary hover:underline mb-4 inline-block'
        >
          <ArrowLeft className='h-4 w-4 inline mr-2' />
          Back to Consciousness
        </Link>

        <h1 className='text-4xl md:text-5xl font-bold mb-4 text-foreground'>
          Memory Systems
        </h1>
        <p className='text-lg italic mb-6 text-muted-foreground'>
          Ancient and modern techniques for enhancing information encoding and
          retrieval through association, visualization, and spatial organization.
          Memory systems help you learn faster, remember more, and unlock your
          brain's creative potential.
        </p>

        <div className='mb-12 bg-card/70 text-card-foreground border p-8 rounded-lg'>
          <h2 className='text-3xl font-bold mb-6 text-foreground'>
            Why Use Memory Systems?
          </h2>
          <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3'>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                Boost recall for study, work, and daily life
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                Organize complex information for easier access
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                Sharpen creativity and imagination
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-lg text-foreground'>
                Develop mental agility and focus
              </span>
            </div>
          </div>

          <h2 className='text-3xl font-bold mb-6 mt-8 text-foreground'>
            Classic Memory Techniques
          </h2>
          <div className='grid gap-4 md:grid-cols-2'>
            <div className='flex items-start space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full mt-2'></div>
              <span className='text-foreground'>
                <strong>Method of Loci (Memory Palace):</strong> Visualize
                information placed along a familiar route or within an imagined
                building to aid recall. This ancient technique was used by Greek and
                Roman orators.
              </span>
            </div>
            <div className='flex items-start space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full mt-2'></div>
              <span className='text-foreground'>
                <strong>Mnemonic Devices:</strong> Use acronyms, rhymes, or phrases
                to encode complex information in memorable ways (e.g., "Every Good
                Boy Does Fine" for musical notes).
              </span>
            </div>
            <div className='flex items-start space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full mt-2'></div>
              <span className='text-foreground'>
                <strong>Chunking:</strong> Group related items together to reduce
                cognitive load and improve retention (e.g., phone numbers, dates).
              </span>
            </div>
            <div className='flex items-start space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full mt-2'></div>
              <span className='text-foreground'>
                <strong>Storytelling:</strong> Turn facts or lists into a vivid story
                to create strong associations.
              </span>
            </div>
          </div>

          <h2 className='text-3xl font-bold mb-6 mt-8 text-foreground'>
            Visualization & Association
          </h2>
          <div className='grid gap-4 md:grid-cols-2'>
            <div className='flex items-start space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full mt-2'></div>
              <span className='text-foreground'>
                <strong>Vivid Imagery:</strong> Turn abstract concepts into striking
                mental images to make them more memorable. The more unusual or
                emotional, the better.
              </span>
            </div>
            <div className='flex items-start space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full mt-2'></div>
              <span className='text-foreground'>
                <strong>Linking:</strong> Create stories or chains that connect
                pieces of information together, so recalling one item triggers the
                next.
              </span>
            </div>
            <div className='flex items-start space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full mt-2'></div>
              <span className='text-foreground'>
                <strong>Substitution:</strong> Replace unfamiliar words or ideas with
                familiar images or sounds.
              </span>
            </div>
          </div>

          <h2 className='text-3xl font-bold mb-6 mt-8 text-foreground'>
            Spatial Organization
          </h2>
          <div className='grid gap-4 md:grid-cols-2'>
            <div className='flex items-start space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full mt-2'></div>
              <span className='text-foreground'>
                <strong>Mind Mapping:</strong> Organize ideas visually using diagrams
                that show relationships and hierarchies. Great for brainstorming and
                review.
              </span>
            </div>
            <div className='flex items-start space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full mt-2'></div>
              <span className='text-foreground'>
                <strong>Peg Systems:</strong> Associate information with a
                pre-memorized list of "pegs" (numbers, shapes, or objects) for easy
                retrieval (e.g., 1-bun, 2-shoe, 3-tree).
              </span>
            </div>
            <div className='flex items-start space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full mt-2'></div>
              <span className='text-foreground'>
                <strong>Major System:</strong> Convert numbers into consonant sounds
                and then into words or images for memorizing long numbers.
              </span>
            </div>
          </div>

          <h2 className='text-3xl font-bold mb-6 mt-8 text-foreground'>
            Modern Approaches
          </h2>
          <div className='grid gap-4 md:grid-cols-2'>
            <div className='flex items-start space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full mt-2'></div>
              <span className='text-foreground'>
                <strong>Spaced Repetition:</strong> Review material at increasing
                intervals to strengthen long-term memory. Used in language learning
                and exam prep.
              </span>
            </div>
            <div className='flex items-start space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full mt-2'></div>
              <span className='text-foreground'>
                <strong>Digital Tools:</strong> Use apps and software to create
                flashcards, mind maps, and spaced repetition schedules (e.g., Anki,
                Quizlet, Obsidian).
              </span>
            </div>
            <div className='flex items-start space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full mt-2'></div>
              <span className='text-foreground'>
                <strong>Active Recall:</strong> Test yourself frequently rather than
                just rereading notes—retrieval practice strengthens memory.
              </span>
            </div>
          </div>

          <h2 className='text-3xl font-bold mb-6 mt-8 text-foreground'>
            Tips for Practice
          </h2>
          <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3'>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-foreground'>
                Practice regularly and experiment with different techniques.
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-foreground'>
                Combine multiple methods for best results.
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-foreground'>
                Personalize your imagery and associations for greater effectiveness.
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-foreground'>
                Teach others what you've learned—explaining concepts helps you
                remember them.
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-foreground'>
                Review and update your memory systems as your needs change.
              </span>
            </div>
          </div>

          <h2 className='text-3xl font-bold mb-6 mt-8 text-foreground'>
            Applications of Memory Systems
          </h2>
          <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3'>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-foreground'>
                Learning languages, vocabulary, and grammar
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-foreground'>Remembering names and faces</span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-foreground'>
                Studying for exams or certifications
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-foreground'>
                Giving speeches or presentations without notes
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-foreground'>
                Memorizing poetry, scripture, or important texts
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-foreground'>
                Organizing creative ideas and projects
              </span>
            </div>
          </div>

          <h2 className='text-3xl font-bold mb-6 mt-8 text-foreground'>
            Recommended Resources
          </h2>
          <div className='grid gap-4 md:grid-cols-2'>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-foreground'>
                <a
                  href='https://www.mindtools.com/a4wo118/memory-improvement-techniques'
                  target='_blank'
                  rel='noopener noreferrer'
                  className='text-primary hover:underline'
                >
                  MindTools – Memory Improvement Techniques
                </a>
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-foreground'>
                <a
                  href='https://www.ankiweb.net/about'
                  target='_blank'
                  rel='noopener noreferrer'
                  className='text-primary hover:underline'
                >
                  Anki – Spaced Repetition Flashcards
                </a>
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-foreground'>
                <a
                  href='https://www.memorypalace.com/'
                  target='_blank'
                  rel='noopener noreferrer'
                  className='text-primary hover:underline'
                >
                  Memory Palace – How to Build a Memory Palace
                </a>
              </span>
            </div>
            <div className='flex items-center space-x-3'>
              <div className='w-2 h-2 bg-primary rounded-full'></div>
              <span className='text-foreground'>
                <a
                  href='https://www.scientificamerican.com/article/how-to-build-a-better-memory/'
                  target='_blank'
                  rel='noopener noreferrer'
                  className='text-primary hover:underline'
                >
                  Scientific American – How to Build a Better Memory
                </a>
              </span>
            </div>
          </div>

          <h2 className='text-3xl font-bold mb-6 mt-8 text-foreground'>
            Quotes on Memory
          </h2>
          <blockquote className='border-l-4 border-primary pl-4 my-4 italic text-lg text-muted-foreground'>
            "Memory is the diary that we all carry about with us." — Oscar Wilde
          </blockquote>
          <blockquote className='border-l-4 border-primary pl-4 my-4 italic text-lg text-muted-foreground'>
            "The true art of memory is the art of attention." — Samuel Johnson
          </blockquote>
          <blockquote className='border-l-4 border-primary pl-4 my-4 italic text-lg text-muted-foreground'>
            "What we learn with pleasure we never forget." — Alfred Mercier
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
              Explore Common Questions About Memory
            </h2>
            <p className='text-xl text-muted-foreground max-w-3xl mx-auto'>
              {totalQuestions} answers to help enhance your memory skills and
              understanding
            </p>
          </div>

          <div className='grid gap-6 md:grid-cols-2 lg:grid-cols-3 max-w-6xl mx-auto'>
            {categories.map((category) => (
              <Link
                key={category.slug}
                href={`/consciousness/memory-systems/${category.slug}`}
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
