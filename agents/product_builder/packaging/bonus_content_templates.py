"""
Bonus Content Templates
Pre-defined unique content for each common bonus type.
This ensures bonuses have distinct content even in Mock Mode or when LLM fails.
"""

from typing import Dict, List
from pathlib import Path


# Define pre-built bonus content for common financial product bonuses
FINANCIAL_BONUS_TEMPLATES: Dict[str, Dict] = {
    "recession": {
        "title": "The Recession-Proof Investing Guide",
        "chapters": [
            {"title": "The Psychology of Market Crashes", "content": """
When the market drops 30%, most investors panic. They sell at the bottom, locking in losses, and miss the recovery. This is the single most expensive mistake in investing.

But for those who understand market cycles, crashes are the best buying opportunities of a lifetime.

"Be fearful when others are greedy, and greedy when others are fearful." — Warren Buffett

This guide gives you the playbook for staying calm—and profiting—when everyone else is running for the exits.
"""},
            {"title": "Understanding Bear Markets", "content": """
A bear market is defined as a decline of 20% or more from recent highs. They're a normal part of investing:

Historical Bear Markets:
- 2000-2002 Dot-com Crash: -49%, Recovery: 7 years
- 2007-2009 Financial Crisis: -57%, Recovery: 5.5 years
- 2020 COVID Crash: -34%, Recovery: 5 months
- 2022 Inflation Correction: -25%, Recovery: 10 months

Key insight: Every single crash has recovered. Every one. The question isn't whether the market will recover—it's whether you'll still be invested when it does.
"""},
            {"title": "The Bear Market Playbook", "content": """
Rule 1: Do Not Sell
The most important rule in a crash is also the simplest: don't sell. Time in the market beats timing the market. Missing just the 10 best days over 20 years cuts your returns in half.

Rule 2: Keep Buying
If you're still in the accumulation phase, a crash is a gift. You're buying assets at a discount. Dollar-cost averaging during a crash means you accumulate more shares at lower prices.

Rule 3: Rebalance Into Fear
If your target allocation is 80% stocks / 20% bonds, a crash might leave you at 65% stocks / 35% bonds. Rebalance by selling bonds and buying stocks at a discount.

Rule 4: Tax-Loss Harvest
A crash offers tax benefits. Sell losing positions to realize losses, immediately buy similar (but not identical) funds, and use the loss to offset gains or up to $3,000 of ordinary income.
"""},
            {"title": "Crash-Specific Strategies by Age", "content": """
If You're 10+ Years From Retirement:
This is the best possible time for a crash. Continue all automatic investments, consider increasing contributions, and resist checking your portfolio daily.

If You're 5-10 Years From Retirement:
Maintain automatic investments, don't panic, and review your allocation. If you're anxious, you may be too aggressive.

If You're Near or In Retirement:
Ensure 2-3 years of expenses are in cash or short-term bonds. Draw from bonds/cash during the crash while letting stocks recover.
"""},
            {"title": "Building Your Crash-Proof Portfolio", "content": """
The All-Weather Allocation (Ray Dalio):
- Long-term US Bonds: 40%
- Stocks (Total US Market): 30%
- Intermediate Bonds: 15%
- Gold: 7.5%
- Commodities: 7.5%

The Bucket Strategy for Retirees:
- Bucket 1 (Now): 2-3 years of expenses in cash/short-term bonds
- Bucket 2 (Soon): 5-7 years of expenses in bonds
- Bucket 3 (Later): Remaining assets in stocks

This structure ensures you never have to sell stocks at the worst time.
"""},
            {"title": "The Mental Game", "content": """
Techniques for Staying Calm:

1. Limit exposure to financial news - News profits from panic
2. Focus on dividends, not prices - Your dividend income is essentially unchanged during crashes
3. Zoom out - Look at a 30-year chart instead of a 30-day chart
4. Remember your why - You're investing for a future goal that hasn't changed

Every bear market has felt like the end of the world while it was happening. Every single time, the market recovered and went on to new highs.
"""},
            {"title": "Crash Response Checklist", "content": """
When the market crashes, follow this checklist:

☐ Do not sell anything
☐ Turn off the news (or limit to 10 minutes/day)
☐ Continue automatic investments as scheduled
☐ Rebalance if you're more than 5% off target allocation
☐ Consider tax-loss harvesting in taxable accounts
☐ Review your statement quarterly, not daily
☐ Remind yourself this is temporary—all crashes end

A crash is not a crisis. It's a sale. Act accordingly.
"""}
        ]
    },
    
    "salary_negotiation": {
        "title": "Salary Negotiation Scripts",
        "chapters": [
            {"title": "The Psychology of Negotiation", "content": """
Most people never negotiate their salary because they fear rejection. But here's what the research shows:

- 84% of employers expect candidates to negotiate
- People who negotiate earn $1-1.5 million more over their careers
- The worst they can say is "no"—and they rarely do

This guide gives you word-for-word scripts so you never have to improvise in the moment.
"""},
            {"title": "Script: The Initial Response to an Offer", "content": """
When you receive an offer, never accept immediately. Use this script:

Recruiter: "We'd like to offer you the position at $85,000."

You: "Thank you so much—I'm really excited about this opportunity. Before I give you an answer, I'd like to take a day to review the full offer details. When is a good time to reconnect tomorrow?"

Why this works: You haven't said no, but you've created space to prepare. Never negotiate in real-time.
"""},
            {"title": "Script: The Counter-Offer", "content": """
Phone Version:

You: "Thanks for giving me time to review. I'm very excited about joining [Company]. Based on my research into market rates for this role, and considering my [specific experience/skills], I was hoping we could discuss the base salary. I was thinking something in the range of $95,000 would be more aligned with my experience. Is that something we can explore?"

If they push back: "I understand there may be constraints. What flexibility do you have with this number?"

Key elements:
1. Express enthusiasm (they need to know you want the job)
2. Cite "research" (signals you've done homework)
3. Give a specific number above your target (leaves room to negotiate down)
4. Ask an open-ended question (invites dialogue)
"""},
            {"title": "Script: Negotiating Beyond Salary", "content": """
If they say salary is fixed, pivot to other elements:

Recruiter: "Unfortunately, $85,000 is the top of the band for this role."

You: "I understand. I'd still love to make this work. Are there other elements we could discuss? Specifically, I'm interested in:
- A signing bonus to bridge the gap
- An accelerated review timeline (6 months instead of 12)
- Additional vacation days
- Remote work flexibility
- Professional development budget"

Negotiable items (in order of typical flexibility):
1. Signing bonus (one-time cost, often easier to approve)
2. Start date
3. Vacation days
4. Work from home schedule
5. Professional development funds
"""},
            {"title": "Script: Requesting a Raise at Your Current Job", "content": """
Email to request the meeting:

Subject: Time to Discuss My Compensation

Hi [Manager Name],

I'd like to schedule some time to discuss my compensation. Over the past [time period], I've [brief accomplishment mention], and I believe it's a good time for us to revisit my salary.

Would you have 30 minutes next week? I'm flexible on timing.

Thanks,
[Your Name]

Never ambush your manager with a raise request. Give them time to prepare.
"""},
            {"title": "Script: The Raise Conversation", "content": """
You: "Thanks for making time. I wanted to discuss my compensation because I believe my contributions have grown significantly since my last adjustment.

Over the past [12 months], I've:
- [Specific accomplishment with numbers]
- [Specific accomplishment with numbers]
- [Specific accomplishment with numbers]

Based on my research, similar roles at other companies are compensated between $[X] and $[Y]. I'd like to discuss bringing my salary to $[Specific Number].

What are your thoughts?"

Then: Stop talking. Let them respond. Silence is powerful.
"""},
            {"title": "Handling Objections", "content": """
Objection 1: "It's not in the budget"
Response: "I understand budget constraints are real. Could we discuss a timeline for this adjustment? Perhaps we can plan for this in next quarter's budget."

Objection 2: "You recently got a raise"
Response: "I appreciate that adjustment. Since then, my responsibilities have expanded significantly to include [X]. I'd like to discuss compensation that reflects the current scope of my role."

Objection 3: "Let's revisit this at your review"
Response: "I'm happy to continue the conversation then. To make that discussion productive, could you clarify what you'd need to see from me between now and then to justify the adjustment I'm proposing?"

Objection 4: "I'll need to check with HR/my boss"
Response: "Absolutely, take the time you need. Could we schedule a follow-up in two weeks to continue the conversation?"
"""},
            {"title": "Email Templates", "content": """
Follow-Up After Raise Meeting:

Subject: Following Up on Compensation Discussion

Hi [Manager Name],

Thanks again for discussing my compensation. To summarize our conversation:
- I proposed a salary adjustment to $[X]
- You mentioned [their response/next steps]
- We agreed to revisit this on [date]

In the meantime, I'll continue focusing on [priority project]. Please let me know if you need anything from me.

Best,
[Your Name]

Why this works: Creates a paper trail and holds them accountable to follow through.
"""},
            {"title": "Negotiation Preparation Checklist", "content": """
Before Any Negotiation:

☐ Research market rate (3+ sources: Glassdoor, Levels.fyi, LinkedIn Salary, Payscale)
☐ Document your accomplishments with specific numbers
☐ Identify your BATNA (Best Alternative to Negotiated Agreement)
☐ Prepare your target number AND walk-away number
☐ Practice the conversation out loud
☐ Prepare for at least 3 objections

Your Negotiation Prep Worksheet:

My current salary: $____________
Market rate for my role: $____________ - $____________
My target salary: $____________
My minimum acceptable: $____________

My top 3 accomplishments:
1. ________________________________________________
2. ________________________________________________
3. ________________________________________________

The 30 minutes you spend preparing can be worth thousands in increased earnings.
"""}
        ]
    },
    
    "workbook": {
        "title": "Financial Freedom Workbook",
        "chapters": [
            {"title": "How to Use This Workbook", "content": """
This workbook is designed to be filled out as you progress through the Financial Freedom Blueprint. Each section corresponds to specific chapters and helps you apply the concepts to your own situation.

Pro tip: Print this out or copy it to a spreadsheet for easier calculations.
"""},
            {"title": "Worksheet 1: Net Worth Calculator", "content": """
ASSETS (What You Own)

Checking Accounts:
Account 1: _____________ Balance: $__________
Account 2: _____________ Balance: $__________

Savings Accounts:
Emergency Fund: $__________
Other Savings: $__________

Retirement Accounts:
401(k): $__________
IRA: $__________

Investment Accounts:
Brokerage: $__________
HSA: $__________

Property:
Home Value: $__________
Vehicle Value: $__________

TOTAL ASSETS: $__________

LIABILITIES (What You Owe)

Credit Cards:
Card 1: $__________ at ____%
Card 2: $__________ at ____%

Student Loans: $__________
Auto Loans: $__________
Mortgage: $__________
Other Debt: $__________

TOTAL LIABILITIES: $__________

NET WORTH = ASSETS - LIABILITIES = $__________
"""},
            {"title": "Worksheet 2: Monthly Expense Tracker", "content": """
FIXED EXPENSES (Same Every Month)
Rent/Mortgage: $__________
Car Payment: $__________
Car Insurance: $__________
Health Insurance: $__________
Utilities: $__________
Internet: $__________
Phone: $__________
Subscriptions: $__________
Debt Payments: $__________
TOTAL FIXED: $__________

VARIABLE EXPENSES
Groceries: $__________
Gas/Transportation: $__________
Dining Out: $__________
Entertainment: $__________
Clothing: $__________
Personal Care: $__________
TOTAL VARIABLE: $__________

TOTAL MONTHLY EXPENSES: $__________
Monthly Take-Home Income: $__________
DIFFERENCE: $__________
"""},
            {"title": "Worksheet 3: Zero-Based Budget", "content": """
MONTHLY INCOME
Take-home pay (Job 1): $__________
Take-home pay (Job 2): $__________
Side income: $__________
TOTAL INCOME: $__________

ALLOCATIONS
Saving/Investing: $__________
Housing: $__________
Transportation: $__________
Food: $__________
Personal: $__________
Lifestyle: $__________
Debt Payments: $__________
TOTAL ALLOCATIONS: $__________

ZERO CHECK:
Income: $__________
- Allocations: $__________
= MUST EQUAL ZERO: $__________
"""},
            {"title": "Worksheet 4: Freedom Number Calculator", "content": """
STEP 1: Calculate Annual Expenses in Financial Independence

Monthly Expenses | Annual
Housing: $__________ | $__________
Utilities: $__________ | $__________
Food: $__________ | $__________
Transportation: $__________ | $__________
Healthcare: $__________ | $__________
Entertainment: $__________ | $__________
Travel: $__________ | $__________
TOTAL: $__________ | $__________

STEP 2: Calculate Your Freedom Number

Annual Expenses: $__________ × 25 = $__________

This is your Freedom Number—the portfolio value where work becomes optional.

STEP 3: Calculate Your Gap

Freedom Number: $__________
- Current Portfolio: $__________
= Gap to Close: $__________
"""},
            {"title": "Worksheet 5: Debt Payoff Planner", "content": """
LIST ALL DEBTS

Debt Name | Balance | Rate | Minimum
__________ | $________ | ___% | $________
__________ | $________ | ___% | $________
__________ | $________ | ___% | $________
__________ | $________ | ___% | $________
TOTAL: $________ | | $________

CHOOSE YOUR METHOD
☐ Avalanche (highest interest first) — Mathematically optimal
☐ Snowball (smallest balance first) — Psychologically motivating

PAYOFF ORDER
1st: _____________ $__________
2nd: _____________ $__________
3rd: _____________ $__________
4th: _____________ $__________

EXTRA PAYMENT CALCULATION
Monthly Budget for Debt: $__________
- Total Minimum Payments: $__________
= Extra Payment Available: $__________

PROJECTED DEBT-FREE DATE: __________
"""},
            {"title": "Worksheet 6: Emergency Fund Calculator", "content": """
ESSENTIAL MONTHLY EXPENSES

Housing: $__________
Utilities: $__________
Groceries (basic): $__________
Transportation: $__________
Minimum debt payments: $__________
Health insurance: $__________
Phone (basic): $__________
TOTAL ESSENTIAL: $__________

YOUR TARGET (circle one):
- Dual income, stable: 3 months
- Single income, stable: 4-5 months
- Variable income: 6+ months
- Self-employed: 6-12 months

CALCULATION
Essential Monthly: $__________
× Target Months: × __________
= Emergency Fund Target: $__________

CURRENT PROGRESS
Current Balance: $__________
Remaining to Save: $__________
Monthly Contribution: $__________
Months to Fully Funded: __________
"""},
            {"title": "Monthly Progress Tracker", "content": """
Track your net worth monthly:

Month 1: $__________ (Starting point)
Month 2: $__________ Change: $__________
Month 3: $__________ Change: $__________
Month 4: $__________ Change: $__________
Month 5: $__________ Change: $__________
Month 6: $__________ Change: $__________
Month 7: $__________ Change: $__________
Month 8: $__________ Change: $__________
Month 9: $__________ Change: $__________
Month 10: $__________ Change: $__________
Month 11: $__________ Change: $__________
Month 12: $__________ Change: $__________

1 YEAR CHANGE: $__________

MILESTONES ACHIEVED
☐ Calculated my net worth (Date: ________)
☐ Created zero-based budget (Date: ________)
☐ $1,000 emergency fund (Date: ________)
☐ Positive net worth (Date: ________)
☐ Full emergency fund (Date: ________)
☐ Debt-free (Date: ________)
☐ Coast FI (Date: ________)
☐ Full Financial Independence (Date: ________)
"""}
        ]
    },
    
    "automation_checklist": {
        "title": "The Automation Checklist",
        "chapters": [
            {"title": "Overview", "content": """
This checklist walks you through automating your entire financial system. Follow it step-by-step, and by Sunday night, you'll have a money machine that runs without your daily involvement.

Time required: 3-4 hours total
Best completed: On a weekend when you have uninterrupted time
Tools needed: Computer, bank login credentials, list of bills
"""},
            {"title": "Phase 1: Account Setup (60-90 minutes)", "content": """
STEP 1: Open Your High-Yield Savings Account (Vault)

Recommended banks: Ally, Marcus (Goldman Sachs), Wealthfront Cash, SoFi (look for 4%+ APY)

☐ Research current interest rates
☐ Choose your bank
☐ Go to bank website and click "Open Account"
☐ Select "Savings Account"
☐ Enter personal information (name, SSN, DOB, address)
☐ Set up online login credentials
☐ Make initial minimum deposit
☐ Wait for verification (usually instant to 24 hours)

Account opened: ☐ Yes
Bank name: _____________

STEP 2: Link All Accounts

☐ Log into primary checking account (Hub)
☐ Go to "Transfers" or "Link External Accounts"
☐ Add Vault account (enter routing + account number)
☐ Verify with micro-deposits (1-3 business days)
"""},
            {"title": "Phase 2: Calculate Your Transfers (30-45 minutes)", "content": """
MONTHLY INCOME (take-home): $__________

FIXED EXPENSES (total for bills): $__________
- Rent/Mortgage
- Utilities
- Car Payment
- Insurance
- Phone/Internet
- Subscriptions
- Minimum debt payments

ASSET BUILDING (total): $__________
- Emergency Fund
- Sinking Funds
- Retirement
- Other Investments

DAILY SPENDING (total): $__________
- Groceries, Gas, Dining, Entertainment, Personal

PER-PAYCHECK TRANSFERS:
How often paid? ☐ Weekly ☐ Bi-weekly ☐ Semi-monthly ☐ Monthly

→ Bills Account: $__________
→ Vault (Savings): $__________
→ Investments: $__________
→ Daily Spending: $__________
TOTAL: $__________ (should equal per-paycheck take-home)
"""},
            {"title": "Phase 3: Set Up Automated Transfers (45-60 minutes)", "content": """
☐ Log into Hub account
☐ Navigate to "Transfers" or "Scheduled Transfers"

TRANSFER #1:
From: Hub → To: Bills Account
Amount: $__________
Frequency: Every payday
Start date: Next payday
☐ Confirmed and saved

TRANSFER #2:
From: Hub → To: Vault (Savings)
Amount: $__________
Frequency: Every payday
Start date: Next payday
☐ Confirmed and saved

TRANSFER #3:
From: Hub → To: Daily Spending
Amount: $__________
Frequency: Every payday
Start date: Next payday
☐ Confirmed and saved

INVESTMENT CONTRIBUTIONS:
☐ 401(k): Adjust contribution to ___% in HR portal
☐ IRA: Set up recurring contribution of $_________ from Hub
☐ Enable auto-invest so cash automatically buys selected fund
"""},
            {"title": "Phase 4: Set Up Bill Autopay (60-90 minutes)", "content": """
Go through each bill and enable automatic payment:

HOUSING
☐ Rent: Set up autopay (if accepted) or calendar reminder
☐ Mortgage: Enable autopay from Bills Account

UTILITIES
☐ Electric: Log in → Billing → Enable Autopay
☐ Gas: Log in → Billing → Enable Autopay
☐ Water: Log in → Billing → Enable Autopay

INSURANCE
☐ Car Insurance: Enable autopay
☐ Renters/Home Insurance: Enable autopay
☐ Health Insurance: Verify payroll-deducted or set up autopay

COMMUNICATION
☐ Phone: Enable autopay
☐ Internet: Enable autopay

DEBT PAYMENTS
☐ Credit Card 1: Enable autopay (☐ Minimum ☐ Statement balance)
☐ Credit Card 2: Enable autopay
☐ Student Loans: Enable autopay (often gives 0.25% rate discount!)
☐ Car Loan: Enable autopay

All bills on autopay: ☐ Yes
"""},
            {"title": "Phase 5: Final Setup and Verification (30 minutes)", "content": """
SET UP ACCOUNT ALERTS

In each bank account, enable alerts for:
☐ Low balance alert (threshold: $__________)
☐ Large withdrawal alert (threshold: $__________)
☐ Deposit notification
☐ Failed payment notification

In credit cards:
☐ Payment due reminder
☐ Payment posted confirmation
☐ Unusual activity alert

CREATE FINANCIAL CALENDAR

☐ 1st of each month: 15-minute financial check-in
☐ Quarterly: 30-minute review
☐ Annually: 1-hour comprehensive review

DOCUMENT YOUR SYSTEM

Hub Account: __________ (Purpose: Income landing)
Bills Account: __________ (Purpose: Fixed expenses)
Vault: __________ (Purpose: Emergency + sinking funds)
Daily Spending: __________ (Purpose: Variable expenses)

Payday Automation Flow:
1. Paycheck deposits to Hub
2. $__________ auto-transfers to Bills
3. $__________ auto-transfers to Vault
4. $__________ auto-transfers to Investments
5. $__________ auto-transfers to Daily Spending
"""},
            {"title": "Completion Checklist", "content": """
ACCOUNTS
☐ Vault (high-yield savings) opened and linked
☐ All accounts linked for transfers

AUTOMATED TRANSFERS
☐ Hub → Bills transfer scheduled
☐ Hub → Vault transfer scheduled
☐ Hub → Daily Spending transfer scheduled
☐ Investment contributions automated

BILL AUTOPAY
☐ All fixed bills on autopay
☐ Credit cards on autopay
☐ Loans on autopay

MONITORING
☐ Account alerts configured
☐ Calendar reminders set
☐ System documented

🎉 CONGRATULATIONS! Your financial system is now automated.

From this point forward:
- Paychecks will auto-distribute
- Bills will auto-pay
- Investments will auto-invest
- Savings will auto-grow

Your only job is the monthly 15-minute check-in.

Money management time reduced from hours per month to minutes.
That's the power of automation.
"""}
        ]
    }
}


def get_bonus_content(bonus_title: str) -> Dict:
    """
    Get pre-defined bonus content based on title keywords.
    Returns None if no matching template found.
    """
    title_lower = bonus_title.lower()
    
    if any(kw in title_lower for kw in ['recession', 'crash', 'bear', 'market']):
        return FINANCIAL_BONUS_TEMPLATES['recession']
    elif any(kw in title_lower for kw in ['salary', 'negotiation', 'raise', 'scripts']):
        return FINANCIAL_BONUS_TEMPLATES['salary_negotiation']
    elif any(kw in title_lower for kw in ['workbook', 'worksheet', 'calculator']):
        return FINANCIAL_BONUS_TEMPLATES['workbook']
    elif any(kw in title_lower for kw in ['automation', 'checklist', 'setup']):
        return FINANCIAL_BONUS_TEMPLATES['automation_checklist']
    else:
        return None


def get_all_financial_bonus_templates() -> List[Dict]:
    """Return all pre-defined financial bonus templates."""
    return list(FINANCIAL_BONUS_TEMPLATES.values())
