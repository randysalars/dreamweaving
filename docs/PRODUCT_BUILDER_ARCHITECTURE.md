# Epistemic Factory — Complete System Architecture

The Epistemic Factory is a **full-lifecycle AI product generation system** that creates premium digital products from topic to deployment, including marketing automation.

---

## 1. System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EPISTEMIC FACTORY PIPELINE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   PHASE 1   │───▶│   PHASE 2   │───▶│   PHASE 3   │───▶│   PHASE 4   │  │
│  │  EMISSION   │    │ GENERATION  │    │ COMPILATION │    │  PACKAGING  │  │
│  │Python CLI   │    │ Antigravity │    │ PDF/Audio   │    │ZIP + Deploy │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│                                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                      │
│  │   PHASE 5   │───▶│   PHASE 6   │───▶│   PHASE 7   │                      │
│  │  MARKETING  │    │   EMAIL     │    │   SOCIAL    │                      │
│  │Landing Page │    │  Sequences  │    │  Scheduling │                      │
│  └─────────────┘    └─────────────┘    └─────────────┘                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Complete Directory Map

```
dreamweaving/agents/product_builder/
├── cli.py                           # Main CLI entry point
├── CONVENTIONS.md                   # Quality guarantees
│
├── core/                            # Core infrastructure
│   ├── llm.py                      # LLMClient (Vertex AI)
│   ├── context.py                  # ProductContext state
│   ├── config.py                   # Settings
│   ├── blueprinter.py              # Initial planning
│   ├── intelligence.py             # DemandSignal processing
│   ├── library_manager.py          # Reference library
│   ├── quality_loop.py             # Quality iteration
│   └── visual_library_manager.py   # Visual assets
│
├── pipeline/                        # 17 Pipeline Agents
│   ├── studio_orchestrator.py      # MASTER CONDUCTOR
│   ├── market_cartographer.py      # Research
│   ├── transformation_designer.py  # Transformation design
│   ├── curriculum_architect.py     # Curriculum structure
│   ├── product_mind.py             # Product intelligence
│   ├── narrative_architect.py      # Story structure
│   ├── voice_stylist.py            # Voice guide
│   ├── writers_room.py             # Multi-agent writing
│   ├── master_editor.py            # Editing
│   ├── ai_detector.py              # AI detection/humanization
│   ├── compression_pass.py         # Content compression
│   ├── content_expander.py         # 100+ page guarantee
│   ├── qa_lab.py                   # Quality assurance
│   ├── reader_sim.py               # Focus group simulation
│   ├── delight_guard.py            # "Delight factor"
│   ├── rubric_guard.py             # Quality scoring
│   └── visual_director.py          # Visual design
│
├── packaging/                       # 20 Packaging Modules
│   ├── pdf_generator.py            # PDF creation (Puppeteer/ReportLab)
│   ├── product_assembler.py        # Final assembly
│   ├── bonus_architect.py          # Bonus design
│   ├── bonus_generator.py          # Bonus content creation
│   ├── image_generator.py          # AI images (DALL-E)
│   ├── tts_client.py               # TEXT-TO-SPEECH (Edge/Piper/Coqui)
│   ├── remotion_client.py          # VIDEO generation (Remotion)
│   ├── audio.py                    # Audio scripts
│   ├── video.py                    # Video orchestration
│   ├── salarsu_deployer.py         # DEPLOY to SalarsNet
│   ├── salarsu_email_client.py     # REGISTER email sequences
│   ├── publisher.py                # Product publishing
│   ├── landing_page.py             # Landing page content
│   ├── landing_page_html.py        # HTML generation
│   ├── transcript_generator.py     # Audio transcripts
│   ├── graphics.py                 # Simple graphics
│   └── code_visuals.py             # Code diagrams
│
├── marketing/                       # 7 Marketing Modules
│   ├── landing_page_generator.py   # LANDING PAGE content
│   ├── email_sequence_generator.py # EMAIL SEQUENCES (welcome/launch)
│   ├── social_promo_generator.py   # SOCIAL POSTS (Twitter/LinkedIn/IG)
│   ├── buffer_client.py            # SCHEDULE to Buffer
│   ├── upsell_recommender.py       # Upsell strategy
│   └── analytics_tracker.py        # Product metrics
│
├── schemas/                         # 15 Pydantic models
│   ├── blueprint.py
│   ├── curriculum_graph.py
│   ├── transformation_map.py
│   ├── voice_style_guide.py
│   ├── premium_scorecard.py
│   └── visual_style.py
│
├── templates/                       # 25+ Prompt templates
│   ├── chapter_complete.md
│   ├── curriculum_architect.md
│   ├── market_cartographer.md
│   └── bonus/                      # Bonus templates
│
└── remotion_project/               # React video project
    ├── package.json
    └── src/
```

---

## 3. The 7 Phases

### Phase 1: EMISSION (Python CLI)
**Purpose:** Generate prompt files for Antigravity

```bash
python3 -m agents.product_builder.cli create \
  --topic "meditation for beginners" \
  --title "The Mindfulness Manual" \
  --output ./products/mindfulness-manual \
  --generate-prompts-only --landing-page --audio
```

**Output:** `prompts/*.prompt.md` files

---

### Phase 2: GENERATION (Antigravity/Claude)
**Purpose:** YOU respond to each prompt

When you see a `.prompt.md` file, read it and create a `.response.md` file with the content.

---

### Phase 3: COMPILATION
**Purpose:** Assemble all responses into final product

```bash
python3 -m agents.product_builder.cli compile \
  --product-dir ./products/mindfulness-manual \
  --title "The Mindfulness Manual"
```

**Creates:**
- Main PDF (100+ pages)
- Bonus PDFs
- Audio files (if `--audio` flag)
- manifest.json

---

### Phase 4: PACKAGING
**Purpose:** Create deployable ZIP and store entry

```bash
python3 -m agents.product_builder.cli deploy \
  --product-dir ./products/mindfulness-manual \
  --name "The Mindfulness Manual" \
  --slug "mindfulness-manual" \
  --price 29.99 \
  --salarsu-root /home/rsalars/Projects/salarsu \
  --commit --push
```

**The `SalarsuDeployer` does:**
1. Copies ZIP to `public/downloads/products/`
2. Generates cover image via DALL-E
3. Creates SQL for BOTH `products` AND `dreamweavings` tables
4. Commits and pushes to git

---

### Phase 5: LANDING PAGE
**Agent:** `LandingPageGenerator`

```python
from marketing import LandingPageGenerator

generator = LandingPageGenerator()
content = generator.generate(
    title="The Mindfulness Manual",
    positioning=positioning_brief,
    chapters=chapters,
    bonuses=bonus_plan
)
# Output: JSON with headline, features, FAQ, testimonials
```

**Saved to:** `landing_page_content.json` (stored in database)

---

### Phase 6: EMAIL SEQUENCES
**Agent:** `EmailSequenceGenerator`

Generates **two sequences**:

**Welcome Sequence (5 emails):**
| Day | Type | Purpose |
|-----|------|---------|
| 0 | Welcome | Immediate value + quick win |
| 1 | Story | Share your journey |
| 3 | Value | Core teaching from product |
| 5 | Objection | Address main concern |
| 7 | Soft Pitch | Gentle product intro |

**Launch Sequence (7 emails):**
| Day | Type | Purpose |
|-----|------|---------|
| -1 | Pre-launch | Anticipation building |
| 0 | Doors Open | Launch announcement |
| 1 | Deep Value | Free insight from product |
| 3 | Social Proof | Testimonials |
| 5 | Urgency | Limited time |
| 7 | Last Chance | Final reminder |

```python
from marketing import EmailSequenceGenerator

generator = EmailSequenceGenerator()
welcome = generator.generate_welcome_sequence(title, positioning)
launch = generator.generate_launch_sequence(title, positioning)

# Export to markdown
generator.export_to_file(welcome, Path("emails_welcome.md"))
generator.export_to_file(launch, Path("emails_launch.md"))
```

**Registration with SalarsNet:**
```python
from packaging import SalarsuEmailClient

client = SalarsuEmailClient()
result = client.register_from_file(
    product_slug="mindfulness-manual",
    product_title="The Mindfulness Manual",
    email_file=Path("emails_welcome.md")
)
```

---

### Phase 7: SOCIAL MEDIA
**Agents:** `SocialPromoGenerator`, `BufferClient`

**Generates posts for:**
| Platform | Format | Character Limit |
|----------|--------|-----------------|
| Twitter/X | Threads, hooks | 280 chars |
| LinkedIn | Professional, value-first | 3000 chars |
| Instagram | Captions + media suggestions | 2200 chars |
| YouTube | Descriptions, titles | 5000 chars |
| TikTok | Hooks + captions | 150 chars |

**Post Types Generated:**
- Launch announcement
- Problem-focused
- Transformation story
- Threads (Twitter)
- FAQ posts
- Engagement prompts
- Testimonial templates

```python
from marketing import SocialPromoGenerator

generator = SocialPromoGenerator()
package = generator.generate_promo_package(
    title="The Mindfulness Manual",
    positioning=positioning_brief,
    chapters=chapters
)

# Export to markdown
generator.export_to_file(package, Path("social_promo.md"))
```

**Schedule to Buffer:**
```python
from marketing.buffer_client import schedule_to_buffer
from datetime import datetime

result = schedule_to_buffer(
    social_package=package,
    launch_date=datetime(2026, 2, 1),
    access_token="YOUR_BUFFER_TOKEN",
    dry_run=True  # Set False to actually schedule
)
```

---

## 4. Audio & Video Generation

### Audio (TTS)
**Agent:** `TTSClient`

**Supported Engines:**
| Engine | Quality | Speed | Setup |
|--------|---------|-------|-------|
| Edge TTS | Good | Fast | None (free Microsoft API) |
| Piper | Good | Very Fast | `pip install piper-tts` |
| Coqui/XTTS | Best | Slow | `pip install TTS` |

```python
from packaging.tts_client import text_to_speech

result = text_to_speech(
    text="Welcome to The Mindfulness Manual...",
    output_path="./chapter_01.wav",
    voice="en-US-GuyNeural"
)
```

### Video (Remotion)
**Agent:** `RemotionClient`, `MediaProducer`

Uses [Remotion](https://www.remotion.dev/) for programmatic video creation.

```python
from packaging.remotion_client import MediaProducer

producer = MediaProducer()

# Decide if video/audio appropriate
should_video = producer.should_create_video(chapter_context)
should_audio = producer.should_create_audio(chapter_context)

# Produce media
result = producer.produce_media_for_chapter(
    chapter_id="ch01",
    chapter_context={"type": "guided_practice"},
    content="...",
    audio_script="..."
)
```

---

## 5. CLI Commands Reference

```bash
# Create product with prompts for Antigravity
python3 -m agents.product_builder.cli create \
  --topic "TOPIC" --title "TITLE" \
  --output ./products/SLUG \
  --generate-prompts-only --landing-page --audio

# Compile after Antigravity responses
python3 -m agents.product_builder.cli compile \
  --product-dir ./products/SLUG --title "TITLE"

# Generate bonuses
python3 -m agents.product_builder.cli bonuses \
  --product-dir ./products/SLUG

# Deploy to SalarsNet
python3 -m agents.product_builder.cli deploy \
  --product-dir ./products/SLUG \
  --name "TITLE" --slug "SLUG" --price 29.99 \
  --salarsu-root /path/to/salarsu --commit --push

# List templates
python3 -m agents.product_builder.cli templates
```

---

## 6. End-to-End Example

```bash
# 1. EMISSION: Generate prompts
cd /home/rsalars/Projects/dreamweaving && source venv/bin/activate
python3 -m agents.product_builder.cli create \
  --topic "financial independence for millennials" \
  --title "Financial Freedom Blueprints" \
  --output ./products/financial-freedom-blueprints \
  --generate-prompts-only --landing-page --audio

# 2. GENERATION: Antigravity answers prompts
# (You read .prompt.md files and create .response.md files)

# 3. COMPILATION: Build PDF + audio
python3 -m agents.product_builder.cli compile \
  --product-dir ./products/financial-freedom-blueprints \
  --title "Financial Freedom Blueprints"

# 4. PACKAGING + DEPLOY: Create ZIP, deploy to store
python3 -m agents.product_builder.cli deploy \
  --product-dir ./products/financial-freedom-blueprints \
  --name "Financial Freedom Blueprints" \
  --slug "financial-freedom-blueprints" \
  --price 47.00 --sale-price 29.99 \
  --salarsu-root /home/rsalars/Projects/salarsu \
  --commit --push

# 5. MARKETING: Generate email sequences + social posts (in Python)
from marketing import EmailSequenceGenerator, SocialPromoGenerator
from packaging import SalarsuEmailClient

# Generate email sequences
email_gen = EmailSequenceGenerator()
welcome = email_gen.generate_welcome_sequence("Financial Freedom Blueprints", positioning)
email_gen.export_to_file(welcome, Path("./products/financial-freedom-blueprints/emails_welcome.md"))

# Register with SalarsNet
email_client = SalarsuEmailClient()
email_client.register_from_file("financial-freedom-blueprints", "Financial Freedom Blueprints", Path("emails_welcome.md"))

# Generate social posts
social_gen = SocialPromoGenerator()
package = social_gen.generate_promo_package("Financial Freedom Blueprints", positioning)
social_gen.export_to_file(package, Path("./products/financial-freedom-blueprints/social_promo.md"))

# Schedule to Buffer
from marketing.buffer_client import schedule_to_buffer
from datetime import datetime
schedule_to_buffer(package, datetime(2026, 2, 1), dry_run=False)
```

---

## 7. The Trinity ZIP Bundle

Every product ZIP contains:

```
Product_Name.zip/
├── Main_Product.pdf           # 100+ page main content
├── Bonus_1_Quickstart.pdf     # Quick-start guide
├── Bonus_2_Checklist.pdf      # Practical checklist
├── Bonus_3_Templates.pdf      # Templates/worksheets
├── audio/                     # (if audio product)
│   ├── chapter_01.mp3
│   ├── chapter_02.mp3
│   └── ...
└── README.md                  # Contents overview
```

---

## 8. Database Tables

The system updates **TWO tables** for downloads:

| Table | Column | Purpose |
|-------|--------|---------|
| `products` | `digital_file_url` | Store catalog |
| `dreamweavings` | `audio_url` | Love Offering downloads |

**Both must have the same URL!**

---

## 9. Key API Endpoints (SalarsNet)

| Endpoint | Purpose |
|----------|---------|
| `/api/admin/seed-digital` | Seed digital products |
| `/api/admin/email-sequences` | Register email sequences |
| `/api/offerings/create` | Create download token |
| `/product-download/[token]` | Customer download page |

---

*Last Updated: Jan 28, 2026*
