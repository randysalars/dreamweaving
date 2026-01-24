
import logging
import shutil
from pathlib import Path
from agents.product_builder.packaging.code_visuals import CodeVisualsGenerator

logging.basicConfig(level=logging.INFO)

def generate_book_visuals():
    # 1. Setup
    product_dir = Path("products/financial_freedom_blueprints")
    visuals_dir = product_dir / "output" / "images"
    visuals_dir.mkdir(parents=True, exist_ok=True)
    
    gen = CodeVisualsGenerator(visuals_dir)
    
    # 2. Define Visuals (Using the "Template Key Format" I implemented: Label: Value)
    
    # Visual A for Chapter 8 (Investing)
    # The Cost of Waiting: Start at 25 vs 35
    desc_a = """
    Create a bar chart titled 'The Cost of Waiting (Age 65 Value)'.
    Data:
    Start at 25: $2,500,000
    Start at 35: $1,100,000
    Start at 45: $400,000
    """
    
    # Visual B for Chapter 3 (Debt)
    # The Avalanche Method (Interest Rates)
    desc_b = """
    Create a bar chart titled 'Interest Rates Killing Your Wealth'.
    Data:
    Credit Card: 24%
    Car Loan: 7%
    Mortgage: 6%
    Market Return: 10%
    """
    
    # Visual C for Chapter 2 (Audit)
    # The Net Worth Equation
    desc_c = """
    Create a bar chart titled 'The Net Worth Equation'.
    Data:
    Total Assets: $550,000
    Total Debt: $350,000
    Net Worth: $200,000
    """

    # Visual D for Chapter 6 (Career)
    # The Loyalty Tax: Staying vs Hopping
    desc_d = """
    Create a line or bar chart titled 'The Price of Loyalty (10 Years)'.
    Data:
    Job Hopper (Switch every 2 yrs): $180,000
    Company Loyalist (3% raises): $110,000
    """

    # Visual E for Chapter 13 (FIRE)
    # The 4% Rule Logic
    desc_e = """
    Create a Flowchart titled 'The 4% Rule Engine'.
    Logic:
    $1M Portfolio -> 4% Withdrawal -> $40k Income -> Freedom
    """

    # Visual F (Non-Chart Diagram) for Chapter 1 (Psychology)
    # The Wealth Loop
    desc_f = """
    Create a Circular Flowchart titled 'The Wealth Flywheel'.
    Logic:
    Earn -> Save -> Invest -> Returns -> Earn
    """

    # Visual G (Non-Chart Diagram) for Chapter 5 (Emergency Fund)
    # The Moat Logic
    desc_g = """
    Create a Process Diagram titled 'Building the Moat'.
    Logic:
    Crisis Strikes -> Cash Buffer -> No Debt -> Peace of Mind
    """
    
    # 3. Generate
    print("Generating Chart A...")
    path_a = gen.generate("investing_cost_of_waiting", desc_a, "chart")
    
    print("Generating Chart B...")
    path_b = gen.generate("debt_interest_rates", desc_b, "chart")

    print("Generating Chart C...")
    path_c = gen.generate("audit_net_worth", desc_c, "chart")

    print("Generating Chart D...")
    path_d = gen.generate("career_loyalty_tax", desc_d, "chart")

    print("Generating Chart E (Diagram)...")
    path_e = gen.generate("fire_4_percent_rule", desc_e, "diagram")

    print("Generating Chart F (Diagram)...")
    path_f = gen.generate("psych_wealth_flywheel", desc_f, "diagram")

    print("Generating Chart G (Diagram)...")
    path_g = gen.generate("emergency_moat_process", desc_g, "diagram")
    
    print(f"\n✅ Visuals Generated at: {visuals_dir}")
    print(f"   A: {path_a}")
    print(f"   B: {path_b}")
    print(f"   C: {path_c}")
    print(f"   D: {path_d}")
    print(f"   E: {path_e}")
    print(f"   F: {path_f}")
    print(f"   G: {path_g}")

if __name__ == "__main__":
    generate_book_visuals()
