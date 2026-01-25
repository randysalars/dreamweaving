import logging
import os
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load .env explicitly if not loaded
load_dotenv()

# Optional Import for Vertex AI
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel, GenerationConfig
    _VERTEX_AVAILABLE = True
except ImportError:
    _VERTEX_AVAILABLE = False
    logger.warning("⚠️ Vertex AI SDK not found. LLMClient will operate in MOCK MODE.")

class LLMClient:
    """
    Native Python client for Google Vertex AI (Antigravity/Ultra).
    Uses authenticated user session (ADC).
    """
    def __init__(self, mock_mode: bool = False):
        self.mock_mode = mock_mode
        if mock_mode or not _VERTEX_AVAILABLE:
            self.valid = True if _VERTEX_AVAILABLE else False # Theoretically valid but using mock
            self.mock_mode = True # Force mock
            logger.info("✨ LLMClient initialized in MOCK MODE.")
            return

        try:
            # Initialize Vertex AI with the user's project
            # Using the project ID found via 'gcloud config get-value project'
            project_id = "gen-lang-client-0470412956" 
            location = "us-central1"
            
            vertexai.init(project=project_id, location=location)
            
            # Use 'gemini-1.5-pro' for high quality
            self.model = GenerativeModel("gemini-1.5-pro-002")
            self.valid = True
            logger.info(f"✨ Connected to Google Vertex AI (Project: {project_id})")
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")
            self.valid = False

    def generate(self, prompt: str, max_tokens: int = 4000) -> str:
        """
        Generates text content using Vertex AI.
        """
        if self.mock_mode:
            return self._get_mock_response(prompt)

        if not self.valid:
             return self._get_mock_response(prompt) # Fallback to mock if API fails init

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.7
                )
            )
            
            if response.text:
                return response.text.strip()
            else:
                 return "# Error: Empty response from Vertex AI."
            
        except Exception as e:
            logger.error(f"Vertex AI Generation failed: {e}")
            # Fallback to mock for testing continuity
            return self._get_mock_response(prompt)

    def _get_mock_response(self, prompt: str) -> str:
        """Return a valid response for testing."""
        prompt_lower = prompt.lower()
        
        # 1. Visual/Chart request -> Force Error to trigger Template Engine Fallback
        if "matplotlib" in prompt_lower or "chart" in prompt_lower:
             return "# Error: Force Template Fallback"
             
        # 2. JSON Structure request (e.g. WritersRoom Architect)
        if "json" in prompt_lower and "sections" in prompt_lower:
            return """
```json
{
  "sections": [
    { "title": "Chapter Content", "north_star": "Comprehensive coverage of the topic." }
  ]
}
```
"""
        
        # 2.5 New Bonus Generator Prompts
        if "process flow" in prompt_lower and "step 1" in prompt_lower:
            return "Audit -> Plan -> Execute -> Review"
            
        if "extract 3 short" in prompt_lower and "takeaways" in prompt_lower:
            return """
- Stop spending on things you hate.
- Automate your savings first.
        # if "extract 3 short" in prompt_lower and "takeaways" in prompt_lower:
        #     return """
# - Stop spending on things you hate.
# - Automate your savings first.
# - Review your numbers weekly.
# """
        # 3. Text Content request (e.g. WritersRoom Writer)
        # Content Library for "Smart Mock"
        
        print(f"DEBUG: Checking prompt: {prompt[:30]}...")
        
        # --- SMART VISUALS ---
        if "matplotlib" in prompt_lower or "chart" in prompt_lower:
            if "budget" in prompt_lower:
                return """
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

labels = ['Needs (50%)', 'Wants (30%)', 'Savings (20%)']
sizes = [50, 30, 20]
colors = ['#1a202c', '#3182ce', '#38a169']

plt.figure(figsize=(10,6))
plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
plt.title('The Ideal Zero-Based Budget Split', fontsize=16)
plt.savefig("{output_path}", dpi=300, bbox_inches='tight')
"""
            if "invest" in prompt_lower or "recession" in prompt_lower:
                return """
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y1 = x * 1.5  # Compounding
y2 = x * 0.1  # Cash

plt.figure(figsize=(10,6))
plt.plot(x, y1, label='Invested at 10%', color='#38a169', linewidth=3)
plt.plot(x, y2, label='Cash Accounts', color='#e53e3e', linewidth=2, linestyle='--')
plt.title('The Cost of Waiting: Investing vs Saving', fontsize=16)
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig("{output_path}", dpi=300, bbox_inches='tight')
"""
            if "negotiat" in prompt_lower:
                return """
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(12, 6))
ax.set_xlim(0, 10)
ax.set_ylim(0, 5)
ax.axis('off')

# Nodes
def draw_box(x, y, text, color='#3182ce'):
    rect = patches.FancyBboxPatch((x, y), 2.5, 1, boxstyle="round,pad=0.1", fc=color, ec="none")
    ax.add_patch(rect)
    ax.text(x+1.25, y+0.5, text, ha='center', va='center', color='white', fontweight='bold')

draw_box(1, 3, "Research", "#718096")
draw_box(4, 3, "Ask High", "#3182ce")
draw_box(7, 3, "Silence", "#e53e3e")

# Arrows
ax.annotate("", xy=(4, 3.5), xytext=(3.5, 3.5), arrowprops=dict(arrowstyle="->", lw=2))
ax.annotate("", xy=(7, 3.5), xytext=(6.5, 3.5), arrowprops=dict(arrowstyle="->", lw=2))

plt.title('The Negotiation Flow', fontsize=16)
plt.savefig("{output_path}", dpi=300, bbox_inches='tight')
"""
            # Generic Fallback Code
            return "# Error: Force Template Fallback"

        # --- SMART TAKEAWAYS ---
        if "extract 3 short" in prompt_lower:
             if "budget" in prompt_lower:
                 return "- Give every dollar a job (Zero-Based).\n- Audit your last 90 days of spending.\n- Automate transfers to savings immediately."
             if "invest" in prompt_lower:
                 return "- Time in the market > Timing the market.\n- Buy VTI and hold forever.\n- Ignore the news cycle."
             if "negotiat" in prompt_lower:
                 return "- Never accept the first offer.\n- Use silence as a weapon.\n- Focus on total compensation, not just salary."
             return "- Stop spending on things you hate.\n- Automate everything.\n- Review weekly."


        # --- BUDGET BOOTCAMP (DEEP DIVE 10-CHAPTER) ---
        if "budget" in prompt_lower:
            print("   DEBUG: Hit BUDGET logic")
            # Check Chapter Title in prompt
            if "intro" in prompt_lower:
                print("      DEBUG: Hit INTRO")
                return """
## The Money Mindset Shift: From Scarcity to Architecture
Welcome to the bootcamp. This is not just about numbers; it is about completely rewriting your psychology around money.
Most people view budgeting as a "restriction"—a punitive diet for your wallet. They think, "I can't buy that latte because the spreadsheet says no." This mindset leads to failure 100% of the time because willpower is a depleting resource. You cannot "white-knuckle" your way to wealth.

**The Architectural Shift:**
Instead, we view budgeting as "Permission Spending."
When you budget $100 for dining out, you can spend that $100 with ZERO guilt. You are not restricting yourself; you are giving yourself *permission* to enjoy your money within boundaries you designed.
This shift changes everything. Instead of feeling poor when you say "no," you feel powerful because you are saying "yes" to your bigger goals.

**The Goal:**
We are not trying to save pennies on coffee. We are building a system.
A system that handles your rent, your debt, and your savings automatically.
By the end of these 30 days, you won't just have a spreadsheet. You will have a machine that builds wealth while you sleep.
You will know exactly how much it costs to be you. 
You will know exactly when you will be debt-free.
And you will sleep better than you have in years.
"""
            if "core concept" in prompt_lower:
                return """
## The Physics of Zero-Based Budgeting
The rule is absolute: **Income - Expense = Zero.**
If you earn $5,000 this month, and your bills tally to $4,000, you have $1,000 "floating" in your account.
In a normal financial life, that $1,000 evaporates. It becomes extra takeout, Amazon purchases, or "I don't know where it went" money. It is lost to entropy.

**The Zero-Based Solution:**
We assign that $1,000 a job BEFORE the month begins. Only by giving every dollar a name can we control it.
*   $500 goes to the Credit Card Principal (The "Debt Killer").
*   $250 goes to the Car Repair Sinking Fund (The "Sleep Well" Fund).
*   $250 goes to the "Fun Money" account (The "Sanity" Fund).

Now, the calculation is $5,000 - $5,000 = $0.
You are broke on paper, but rich in assets. This is the secret of the wealthy. They do not have "spare cash" sitting idle. Every dollar is deployed like a soldier on a battlefield.

**Why Zero Matters:**
If you leave $100 "unassigned" in your checking account, you will spend it. It is a law of nature.
By zeroing out, you force efficiency. You ensure that your priorities (Debt, Savings, Investing) get paid before your impulses (Uber Eats, Gadgets).
"""
            if "strategy part 1" in prompt_lower:
                return """
## Days 1-7: The Forensic Audit
You cannot fix what you cannot measure. Before we cut a single expense, we must see the truth about your life.
Most people estimate their spending based on their "ideal" self. "I spend about $400 on groceries," they say.
The audit usually reveals they spend $800. The gap between your *perception* and *reality* is where your wealth is leaking out.

**The Protocol:**
1.  **Download:** Get the CSV files for your Checking and Credit Cards for the last 90 days. Do not rely on your memory. Memory lies. Data tells the truth.
2.  **Categorize:** Use 3 highlighters or digital tags:
    *   **Green (Survival):** Rent, Utilities, Basic Groceries, Insurance. These are non-negotiable.
    *   **Yellow (Optional but Good):** Netflix, Gym, Quality Food, Hobbies. These add value but aren't strictly necessary for survival.
    *   **Red (Waste):** unused subscriptions, fees, impulsive shopping, convenience fees. These are the enemy.
3.  **The Burn Rate:**
    Add up all the Greens. That is your "Survival Number." If you lost your job today, that is what you need to survive. Knowing this number destroys anxiety.
    Now add up the Reds. This is your immediate "raise." Cutting these costs is tax-free income.
"""
            if "strategy part 2" in prompt_lower:
                return """
## Days 8-14: The Great Purge & Negotiate
Now that we have the Red pile (Waste), we attack.
But we do not just cancel; we negotiate. We treat our household like a business reducing overhead.

**The "Script" for Service Providers:**
Call your Internet/Cable/Phone provider. Do not be rude, be firm.
**You:** "Hi, I'm reviewing my monthly expenses. I see my bill is $80. I saw a promotion for new customers at $50. I'd like to match that or I'll need to cancel service today."
**Agent:** "I can't do that. That's for new customers only."
**You:** "I understand. Please route me to the retention department to process my cancellation."
*(This is the key step. Regular agents can't discount. Retention agents are paid to keep you.)*
**Retention Agent:** "Wait! We can offer you $55/month for 12 months if you stay."
**Result:** You just saved $300/year with a 5-minute phone call. That is a $3,600/hour hourly rate.

**The Cancellation Challenge:**
Cancel 3 subscriptions today. You can always sign up again later. But for 30 days, kill them.
Prove to yourself that you are in control.
"""
            if "strategy part 3" in prompt_lower:
                return """
## Days 15-21: The Automation Engine
Willpower fails. Systems scale.
If you rely on "remembering" to save money, you will fail.
We are going to build a "Waterfall" system for your money that operates without your intervention.

**The Stack:**
1.  **Income Account:** All paychecks hit here. This is the reservoir.
2.  **The Filter:** On the 1st of the month, an auto-transfer moves your "Fixed Cost" money (Rent, Bills) to a separate Billing Account. This money is now "spent" and untouchable.
3.  **The Pay Yourself First:** On the 2nd, an auto-transfer moves 10-20% to your High Yield Savings or Investment Account. This happens *before* you wake up.
4.  **The Spend:** Whatever remains is transferred to your Debit Card/Spending Account. This is for groceries, gas, and fun.

**Why this works:**
You physically cannot overspend on bills because the money isn't in your spending account.
You cannot forget to save because it happened automatically.
You handle your money *once* to set up the system, then the system handles your money forever.
"""
            if "advanced" in prompt_lower:
                return """
## Sinking Funds: The Secret Weapon
Christmas happens every December. It is not an emergency.
Car tires wear out every 30,000 miles. It is not a surprise.
Yet, these events destroy budgets because we treat them as "unexpected." We swipe the credit card and say "I had to."

**Solution: Sinking Funds**
Open a sub-savings account (many banks call them "Buckets" or "Vaults").
We smooth out these "lumpy" expenses into monthly payments.
*   **Car Repair:** $50/mo.
*   **Gifts:** $30/mo.
*   **Vet Bills:** $20/mo.
*   **Vacation:** $100/mo.

When your tire blows out, you don't panic. You don't feel stress. You check your "Car Repair" bucket, see $600, and pay for the tire.
You essentially "paid" for that tire 2 years ago, $50 at a time. This is how you bulletproof your finances against life's friction.
"""
            if "mistake" in prompt_lower:
                return """
## The "Yo-Yo" Effect (Budgeting Burnout)
The #1 mistake is being too aggressive.
If you normally spend $600 on dining out, and you budget $0 for next month, you will fail.
You will last 12 days. Then you will have a bad day at work, order $50 of Sushi, feel guilty, and abandon the entire budget.

**The Fix: The "Guilt-Free" Buffer**
Budget for waste. Literally.
Add a line item called "Stupidity" or "Fun" for $100/mo.
When you blow money on something dumb, categorize it there. You stayed ON BUDGET.
Psychologically, this keeps you in the game. Consistency > Perfection.
It is better to adhere to a loose budget for 10 years than a perfect budget for 10 days.
"""
            if "case stud" in prompt_lower:
                return """
## Case Study: Sarah (The "I Don't Make Enough" Spender)
Sarah earned $80k/year but lived paycheck to paycheck. She had $12k in credit card debt.
She believed she didn't earn enough to save. She felt like a victim of inflation.

**The Audit:**
Her audit revealed she spent $900/mo on "convenience" (Uber Eats, Amazon, 7-11).
She wasn't buying luxury items; she was buying laziness. She was paying a 30% premium on her life because she wasn't planning.

**The Intervention:**
1.  She deleted Amazon and Uber Eats apps from her phone. (Friction Strategy).
2.  She switched to cash envelopes for groceries ($400/mo limit).
3.  She automated a $500/mo payment to her credit card.

**The Result:**
In 6 months, she adjusted to the new lifestyle. The constraints forced creativity (meal prepping).
In 18 months, the debt was gone.
She didn't get a raise. She gave herself a raise by stopping the leaks.
"""
            if "tool" in prompt_lower:
                return """
## The Tech Stack
1.  **YNAB (You Need A Budget):** The Gold Standard. It forces you to only budget money you HAVE, not money you expect. Steep learning curve, but life-changing. It is digital envelopes.
2.  **Excel/Google Sheets:** For the control freak. Total customization. Use the "Aspire Budget" free template if you want power without cost.
3.  **Monarch Money:** The best modern dashboard for couples. Connects to everything, great UI.
4.  **EveryDollar:** Good for simple, Dave Ramsey-style zero-based budgeting.

**Recommendation:**
Start with Paper or Excel for Month 1 to feel the pain. Writing numbers by hand connects your brain to the money.
Then automate with YNAB once you understand the philosophy.
"""
            if "action plan" in prompt_lower:
                return """
## The 30-Day Calendar Summary
*   **Day 1:** Print Statements. Highlight Green/Yellow/Red. Do not judge, just observe.
*   **Day 2:** Calculate Survival Number. Realize you are safer than you think.
*   **Day 5:** Cancel 3 Subscriptions. Feel the momentum.
*   **Day 10:** Open High Yield Savings Account. Earn 4-5% on your cash.
*   **Day 15:** Set up Auto-Transfers (The Waterfall). The machine is live.
*   **Day 20:** First Sinking Fund Created (e.g. Christmas). Future-proofing.
*   **Day 30:** Full Monthly Review. Compare Actual vs Planned.

**Final Words:**
The fast path is the slow path. Do not try to get rich tomorrow.
Build the machine today. Trust the compounding.
"""
            # Fallback for generic budget prompts
            return """
## Understanding the Flow of Money
Money is energy. It flows where attention goes.
If you ignore it, it flows away.
If you direct it, it flows towards your goals.
This chapter builds the dam and the turbine.
"""

        # --- INVESTING GUIDE (Deep Content) ---
        if "invest" in prompt_lower or "recession" in prompt_lower:
            if "intro" in prompt_lower:
                return """
## The Market is a Machine: Understanding the Wealth Generator
The stock market is not a casino. It is not a place for gambling, guessing, or "playing the lottery."
It is a machine that transfers wealth from the impatient to the patient. It is the engine of human capitalism.
When the market drops 20%, it is not "broken." It is going on sale.
Most people run out of the store when prices drop. Investors run IN.

**The Rule of 72 (The Magic Number):**
Divide the number 72 by your expected interest rate to see how many years it takes for your money to double.
*   **Bank Savings (0.01%):** 72 / 0.01 = 7,200 years to double. (You will be dead).
*   **Inflation (3%):** Your purchasing power HALVES every 24 years.
*   **S&P 500 (10%):** 72 / 10 = 7.2 years to double.

At 10%, your money doubles every 7 years. Then it quadruples. Then it octuples.
$10k becomes $20k -> $40k -> $80k -> $160k.
You didn't work for that growth. The machine did.
"""
            if "concept" in prompt_lower:
                return """
## The Philosophy of "Enough": Winning the Game
Investing is not about becoming a billionaire. It is about buying your freedom.
Every dollar you invest is a little green soldier.
That soldier works 24 hours a day, 7 days a week, 365 days a year. It never sleeps, never complains, never strikes.
And best of all? It creates more little soldiers (Interest/Dividends).

**The Crossover Point:**
When you have enough soldiers (Capital), their output (Passive Income) exceeds your expenses.
At that exact moment, you are free. You never *have* to work again.
You might choose to work, but you don't have to.
This is the only goal of this guide. Anything else—beating the market, picking the next Tesla—is ego. And ego is expensive.
"""
            if "strategy" in prompt_lower:
                return """
## The "Sleep Well at Night" Portfolio (Boglehead Style)
We don't pick stocks. We pick economies.
Trying to pick the "winning stock" is like trying to find a needle in a haystack.
Instead, we buy the haystack.

**The 3-Fund Portfolio:**
1.  **60% Total US Stock Market Index (VTI):**
    You own a piece of Apple, Google, Microsoft, but also the local utility company and the steel mill. You own the entire American economic engine.
2.  **20% Total International Stock Index (VXUS):**
    Invest in Samsung (Korea), Nestle (Swiss), Toyota (Japan). This hedges you against the US dollar collapsing or the US economy stagnating.
3.  **20% Total Bond Market (BND):**
    The airbag. When stocks crash (and they will), bonds usually hold steady or rise as investors flee to safety. This keeps you sane so you don't panic sell.

**Rebalancing:**
Once a year, you look at your pie chart. If stocks grew to 70%, you sell some stocks and buy bonds to get back to 60/20/20.
That forces you to "Sell High, Buy Low" automatically.
"""
            if "common mistake" in prompt_lower or "mistake" in prompt_lower:
                return """
## Mistake: Panic Selling (The Wealth Killer)
"It's different this time."
No, it isn't. Every crash feels like the end of the world.
In 2008, the banks were collapsing. The world was ending.
In 2020, a pandemic shut down the globe. The world was ending.
In 1929, the Great Depression hit. The world was ending.

**The Math of Panic:**
If you sell at the bottom because you are scared, you turn a paper loss (temporary) into a real loss (permanent).
You cement the failure.
Then, you sit in cash ("Waiting for the dust to settle") while the market recovers 20% in a flash.
You buy back in at the top.
You just destroyed 10 years of compounding in 2 months.

**The Fix:**
1.  **Stop Watching the News:** CNBC exists to sell ads, not to make you rich. Fear sells ads.
2.  **Delete the App:** Make it hard to log in.
3.  **Automate:** If the money leaves your account automatically, you can't emotionally stop it.
"""
            if "action plan" in prompt_lower or "action" in prompt_lower:
                return """
## Step 1: Occam's Razor for Accounts
We need to put our investments in the right "buckets" to avoid taxes.

**The Order of Operations (The Waterfall):**
1.  **401k Match:** If your employer offers a match (e.g., 3%), TAKE IT. It is a guaranteed 100% return instantly. Free money.
2.  **Health Savings Account (HSA):** The Triple Tax Threat. Tax-free in, tax-free growth, tax-free out for medical. It's the best account in existence.
3.  **Roth IRA:** You pay taxes now, but tax-free FOREVER. When you retire with $2 Million, the government gets $0.
4.  **Traditional IRA / 401k:** Tax deduction now, pay taxes later. Good for high earners.
5.  **Taxable Brokerage:** For everything else.

**Execution:**
1.  Go to Vanguard/Fidelity.
2.  Open a **Roth IRA**.
3.  Link your bank.
4.  Transfer $500.
5.  **CRITICAL STEP:** search "VTI" and CLICK BUY. (Many people transfer money but leave it in cash!).
"""
            return "## The path to wealth is boring..."

        # --- NEGOTIATION BLACKBOOK (Deep Content) ---
        if "negotiat" in prompt_lower or "salary" in prompt_lower:
            if "intro" in prompt_lower:
                return """
## You Are a Business
You are not an employee. You are a business of one (Me, Inc.) selling services to a client (Your Employer).
A business does not "ask for a raise" (begging).
A business "re-negotiates a contract based on increased value delivery."
The moment you switch this mindset, the fear disappears. You are B2B sales.
Unlike a typical employee who fears rejection, a business understands that price negotiation is a standard part of every deal.
"""
            if "concept" in prompt_lower:
                return """
## The Leverage Equation
You only have leverage if:
1.  You have another offer.
2.  You are willing to walk away.
3.  You provide unique value they cannot easily replace.

If you have none of these, you are not negotiating; you are hoping.
This chapter builds your Leverage Stack before you send the email.
"""
            if "strategy" in prompt_lower:
                return """
## The "I'm Excited" Bridge
When they offer you $90k, but you want $110k, do not say "No." Do not say "That's too low."
Use the **Bridge Technique**. Validate their offer, then redirect to your number.

**The Script:**
*"I am really excited about the team and the mission here. I know I can drive results in [Project X]. However, looking at the market value for this role and my specific experience in [Skill Y], I was expecting to land closer to the $110k range. What flexibility do we have to get closer to that number?"*

**The Aftermath:**
Then... shut up.
Silence is your weapon. They will feel an urge to fill the silence. Let them fill it with a higher number.
"""
            if "common mistake" in prompt_lower or "mistake" in prompt_lower:
                return """
## Mistake: Negotiating from Need vs ROI
**Wrong:** "I need more money because my rent went up."
**Company response (Silent):** "That is not my problem."

**Right:** "Negotiating from ROI (Return on Investment)."
**Script:** "In the last 6 months, I automated the reporting system, saving the team 20 hours a week. That is 1,000 hours a year. At a consultant rate, that's $100k in value. I am asking for a $10k adjustment to reflect that created value."

This makes saying "No" illogical.
"""
            if "action plan" in prompt_lower or "action" in prompt_lower:
                return """
## The Counter-Offer Email Template
Subject: Re: Offer for [Role] - [Your Name]

Hi [Name],

Thank you so much for the offer. I am thrilled about the opportunity to join [Company] and tackle [Project A].

I’ve reviewed the details. Before we finalize, I’d like to discuss the base salary component. Based on my research and the specific responsibilities of this role, I’m looking for something in the [$X - $Y] range.

I am confident we can find a number that works, as I am very keen to get started. Can we hop on a brief call tomorrow at 10am to resolve this?

Best,
[You]
"""
            return "## Never Accept the First Offer\nThe first offer is a test. They expect you to counter. If you don't, you are leaving money on the table."

        # Fallback for misc
        return """
## Deep Dive Section
This section explores the nuance of the topic in depth.
It covers the foundational elements, the strategic application, and the common pitfalls.
By mastering this, you gain control over the outcome.
"""
