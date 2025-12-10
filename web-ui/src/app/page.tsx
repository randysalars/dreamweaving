import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ArrowRight,
  BookOpen,
  Compass,
  MoonStar,
  Search,
  Shield,
  Sparkles,
} from "lucide-react";
import { NewsletterForm } from "@/components/NewsletterForm";

const traditions = [
  {
    name: "Christianity",
    summary: "Prophetic dreams, angelic encounters, psalm-based protection, saints and visions.",
    queries: ["What does an angelic dream mean?", "How to pray before incubating a dream?"],
  },
  {
    name: "Norse",
    summary: "Seidr trance work, rune dreams, Valkyrie protection, Yggdrasil world-bridge journeys.",
    queries: ["Are rune dreams omens?", "How to invite guidance from the Norns?"],
  },
  {
    name: "Egyptian",
    summary: "Temple incubations, solar barque rebirth, Anubis psychopomp guidance, judgment halls.",
    queries: ["How to perform an incubation ritual?", "Who appears as a guide in Duat dreams?"],
  },
  {
    name: "Tibetan / Buddhist",
    summary: "Milam dream yoga stages, bardo rehearsal, clear light awareness, mantra-infused sleep.",
    queries: ["Steps for beginner dream yoga?", "How to stabilize clear light dreams?"],
  },
  {
    name: "Indigenous & Earthline",
    summary: "Vision quests, animal totems, ancestor councils, plant-spirit teaching dreams.",
    queries: ["How to work with an animal guide?", "What is a safe vision-quest protocol?"],
  },
  {
    name: "Modern & Depth Psychology",
    summary: "Lucid methods, active imagination, archetypal dialogue, sleep science and binaural tech.",
    queries: ["Lucid induction tonight?", "How to decode recurring archetypes?"],
  },
];

const journeys = [
  {
    title: "Psalmic Night Watch",
    tradition: "Christianity",
    intent: "Protection",
    length: "22 min",
    summary: "Shielding prayer, angelic guardianship, and journaling prompts to interpret symbols.",
  },
  {
    title: "Rune Incubation",
    tradition: "Norse",
    intent: "Guidance",
    length: "18 min",
    summary: "Seidr breath, raidho rune casting, and a Valkyrie ally for travel between realms.",
  },
  {
    title: "Temple of Dreams",
    tradition: "Egyptian",
    intent: "Healing",
    length: "26 min",
    summary: "Pre-sleep purification, solar rebirth imagery, and Anubis-led interpretation steps.",
  },
  {
    title: "Milam Entry",
    tradition: "Tibetan",
    intent: "Lucidity",
    length: "24 min",
    summary: "Four-stage dream yoga ladder with seed syllables and soft wake-back-to-bed timing.",
  },
];

const archetypeAnswers = [
  {
    title: "Valkyrie / Protector",
    meaning: "Signals protection and passage through trials; respond with courage + grounding ritual.",
  },
  {
    title: "Angelic Messenger",
    meaning: "Often arrives with instruction or warning; record verbatim phrases and pair with prayer.",
  },
  {
    title: "Psychopomp (Anubis, Hermes)",
    meaning: "Guides transitions; use offerings/thanks and journal any thresholds or gates you crossed.",
  },
  {
    title: "Ancestral Guide",
    meaning: "Appears to reconcile lineage patterns; follow with a gratitude rite and integration walk.",
  },
];

const faqs = [
  {
    question: "How do I incubate a dream for guidance?",
    answer:
      "Set a single clear question, create a short pre-sleep ritual (prayer, rune, or mantra), keep a notebook ready, and record symbols immediately on waking.",
  },
  {
    question: "What makes a dream ‘prophetic’ versus ‘processing’?",
    answer:
      "Prophetic dreams tend to be vivid, coherent, emotionally weighty, and sometimes include direct instruction; processing dreams remix recent events with loose, shifting narratives.",
  },
  {
    question: "How can I get lucid tonight?",
    answer:
      "Do 8–10 reality checks today, sleep 6 hours then wake-back-to-bed, use a 10–15 minute induction audio, and set a single intent like ‘When I see hands, I become lucid.’",
  },
];

const structuredData = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  name: "Sacred Digital Dreamweaver",
  url: "https://dreamweaving.example",
  potentialAction: {
    "@type": "SearchAction",
    target: "https://dreamweaving.example/search?q={search_term_string}",
    "query-input": "required name=search_term_string",
  },
  mainEntity: [
    {
      "@type": "ItemList",
      name: "Dreamweaving Traditions",
      itemListOrder: "ItemListOrderAscending",
      numberOfItems: traditions.length,
      itemListElement: traditions.map((tradition, index) => ({
        "@type": "ListItem",
        position: index + 1,
        name: tradition.name,
        description: tradition.summary,
      })),
    },
    {
      "@type": "FAQPage",
      mainEntity: faqs.map((faq) => ({
        "@type": "Question",
        name: faq.question,
        acceptedAnswer: {
          "@type": "Answer",
          text: faq.answer,
        },
      })),
    },
  ],
};

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-amber-50 text-slate-900">
      <main className="mx-auto flex max-w-6xl flex-col gap-16 px-6 py-12 sm:py-16 lg:px-8">
        <section className="grid gap-10 lg:grid-cols-[1.3fr_1fr] lg:items-center">
          <div className="space-y-6">
            <div className="inline-flex items-center gap-2 rounded-full bg-white/70 px-3 py-1 text-sm font-medium shadow-sm ring-1 ring-slate-200">
              <Sparkles className="h-4 w-4 text-amber-600" />
              Dreamweaving studio across traditions
            </div>
            <div className="space-y-3">
              <h1 className="text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
                Explore dreamweaving across Christian visions, Norse seidr,
                temple incubations, and modern lucid practice.
              </h1>
              <p className="text-lg text-slate-700">
                Answer your dream questions with tradition-specific guides,
                archetype explainers, and guided audio journeys engineered for
                insight, healing, and lucidity.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Button className="gap-2">
                Browse Traditions
                <Compass className="h-4 w-4" />
              </Button>
              <Button variant="outline" className="gap-2">
                Start a Guided Journey
                <ArrowRight className="h-4 w-4" />
              </Button>
              <Button variant="ghost" className="gap-2">
                Find Answers
                <BookOpen className="h-4 w-4" />
              </Button>
            </div>
            <div className="grid gap-4 rounded-2xl bg-white/80 p-4 shadow-sm ring-1 ring-slate-200 sm:grid-cols-[1.3fr_1fr] sm:items-center">
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-amber-100 text-amber-700">
                  <Search className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-800">
                    Quick finder
                  </p>
                  <p className="text-sm text-slate-600">
                    Search by tradition, intent, method, or archetype.
                  </p>
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                {["Tradition", "Intent", "Method", "Archetype", "Duration"].map(
                  (pill) => (
                    <Badge key={pill} variant="secondary" className="px-3 py-1">
                      {pill}
                    </Badge>
                  )
                )}
              </div>
            </div>
            <dl className="grid gap-4 text-sm text-slate-700 sm:grid-cols-3">
              <div>
                <dt className="font-semibold text-slate-900">Traditions</dt>
                <dd>Christian, Norse, Egyptian, Tibetan, Indigenous, more</dd>
              </div>
              <div>
                <dt className="font-semibold text-slate-900">Methods</dt>
                <dd>Lucid induction, incubation, ritual, active imagination</dd>
              </div>
              <div>
                <dt className="font-semibold text-slate-900">Outcomes</dt>
                <dd>Protection, healing, creativity, prophecy, integration</dd>
              </div>
            </dl>
          </div>
          <Card className="bg-white/80 ring-1 ring-slate-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Shield className="h-5 w-5 text-amber-600" />
                Safety + integrity
              </CardTitle>
              <CardDescription>
                Tradition-respectful language, neuroscience-informed pacing, and
                built-in post-dream integration prompts.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <p className="text-sm font-semibold text-slate-900">
                  Ritual & practice layers
                </p>
                <p className="text-sm text-slate-700">
                  Sleep hygiene, grounding, protection rites, and journaling
                  checklists adapted per culture.
                </p>
              </div>
              <div className="space-y-2">
                <p className="text-sm font-semibold text-slate-900">
                  Archetype clarity
                </p>
                <p className="text-sm text-slate-700">
                  Cross-compare Valkyries, angels, psychopomps, and ancestor
                  guides with direct “what to do next” steps.
                </p>
              </div>
            </CardContent>
            <CardFooter className="justify-end">
              <Button variant="ghost" className="gap-2 text-amber-700">
                View safety guide
                <ArrowRight className="h-4 w-4" />
              </Button>
            </CardFooter>
          </Card>
        </section>

        <section className="space-y-6">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-sm font-semibold uppercase tracking-wide text-amber-700">
                Traditions
              </p>
              <h2 className="text-2xl font-semibold">Browse by lineage</h2>
              <p className="text-sm text-slate-700">
                Keep every existing category; layer new navigation that clarifies
                culture, era, practice, and intent.
              </p>
            </div>
            <Button variant="outline" className="gap-2">
              See all traditions
              <ArrowRight className="h-4 w-4" />
            </Button>
          </div>
          <div className="grid gap-5 md:grid-cols-2">
            {traditions.map((tradition) => (
              <Card key={tradition.name} className="border-slate-200">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>{tradition.name}</span>
                    <Badge variant="secondary">Guides</Badge>
                  </CardTitle>
                  <CardDescription>{tradition.summary}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-sm font-semibold text-slate-900">
                    Common questions
                  </p>
                  <ul className="space-y-2 text-sm text-slate-700">
                    {tradition.queries.map((q) => (
                      <li key={q} className="flex items-start gap-2">
                        <span className="mt-1 h-1.5 w-1.5 rounded-full bg-amber-600" />
                        <span>{q}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
                <CardFooter className="justify-end">
                  <Button variant="ghost" className="gap-2">
                    Open {tradition.name}
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        </section>

        <section className="space-y-6">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-sm font-semibold uppercase tracking-wide text-amber-700">
                Guided audio
              </p>
              <h2 className="text-2xl font-semibold">Featured journeys</h2>
              <p className="text-sm text-slate-700">
                All existing journeys remain; these spotlights route users to
                intent-aligned starting points.
              </p>
            </div>
            <Button variant="outline" className="gap-2">
              View library
              <ArrowRight className="h-4 w-4" />
            </Button>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            {journeys.map((journey) => (
              <Card key={journey.title} className="bg-white/90 border-slate-200">
                <CardHeader>
                  <CardTitle className="text-lg">{journey.title}</CardTitle>
                  <CardDescription>{journey.summary}</CardDescription>
                </CardHeader>
                <CardContent className="flex flex-wrap gap-2 text-sm text-slate-700">
                  <Badge variant="secondary">{journey.tradition}</Badge>
                  <Badge variant="secondary">{journey.intent}</Badge>
                  <Badge variant="outline">{journey.length}</Badge>
                </CardContent>
                <CardFooter className="justify-end">
                  <Button variant="ghost" className="gap-2">
                    Start journey
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-[1.3fr_1fr]">
          <div className="space-y-4 rounded-2xl bg-white/85 p-6 shadow-sm ring-1 ring-slate-200">
            <div className="flex items-center gap-2">
              <MoonStar className="h-5 w-5 text-amber-600" />
              <p className="text-sm font-semibold uppercase tracking-wide text-amber-700">
                Archetype answers
              </p>
            </div>
            <h3 className="text-xl font-semibold">
              Decode who shows up in your dreams—and what to do next.
            </h3>
            <div className="grid gap-4 md:grid-cols-2">
              {archetypeAnswers.map((item) => (
                <Card key={item.title} className="border-slate-200">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base">{item.title}</CardTitle>
                  </CardHeader>
                  <CardContent className="text-sm text-slate-700">
                    {item.meaning}
                  </CardContent>
                  <CardFooter className="justify-start">
                    <Button variant="ghost" className="gap-2">
                      Read guide
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  </CardFooter>
                </Card>
              ))}
            </div>
          </div>
          <Card className="bg-slate-900 text-white ring-1 ring-slate-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <Sparkles className="h-5 w-5 text-amber-400" />
                Practices & methods
              </CardTitle>
              <CardDescription className="text-slate-200">
                Lucid induction, incubation, active imagination, divination,
                healing/protection, sleep optimization, and journaling stacks.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-slate-100">
              <p className="font-semibold text-white">Tonight’s fast path</p>
              <ul className="space-y-2">
                <li className="flex items-start gap-2">
                  <span className="mt-1 h-1.5 w-1.5 rounded-full bg-amber-400" />
                  Wake-back-to-bed + 10 minute induction audio + single intent.
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-1 h-1.5 w-1.5 rounded-full bg-amber-400" />
                  Incubation card: write the question, repeat three times, place
                  under pillow, journal immediately.
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-1 h-1.5 w-1.5 rounded-full bg-amber-400" />
                  Safety: brief grounding + protection phrase matched to your
                  tradition.
                </li>
              </ul>
            </CardContent>
            <CardFooter className="justify-end">
              <Button variant="secondary" className="gap-2 bg-white text-slate-900">
                Open practice hub
                <ArrowRight className="h-4 w-4" />
              </Button>
            </CardFooter>
          </Card>
        </section>

        <section className="grid gap-6 rounded-2xl bg-white/85 p-6 shadow-sm ring-1 ring-slate-200 lg:grid-cols-[1.2fr_1fr]">
          <div className="space-y-4">
            <p className="text-sm font-semibold uppercase tracking-wide text-amber-700">
              Answer engine
            </p>
            <h3 className="text-xl font-semibold">
              Quick answers for search and voice
            </h3>
            <div className="space-y-4">
              {faqs.map((faq) => (
                <div key={faq.question} className="space-y-1">
                  <p className="text-sm font-semibold text-slate-900">
                    {faq.question}
                  </p>
                  <p className="text-sm text-slate-700">{faq.answer}</p>
                </div>
              ))}
            </div>
          </div>
          <div className="space-y-4 rounded-xl bg-slate-900 p-6 text-white">
            <p className="text-sm font-semibold uppercase tracking-wide text-amber-400">
              Stay attuned
            </p>
            <h4 className="text-lg font-semibold">
              Weekly dream notes newsletter
            </h4>
            <p className="text-sm text-slate-200">
              One tradition, one practice, one script snippet. No spam, just
              field-tested prompts and rituals.
            </p>
            <NewsletterForm variant="dark" source="homepage" />
            <p className="text-xs text-slate-300">
              Opt out anytime. Includes integration and safety checklists.
            </p>
          </div>
        </section>
      </main>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
      />
    </div>
  );
}
