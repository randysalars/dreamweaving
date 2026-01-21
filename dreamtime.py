import os
import json
import random
import time
from simulator import UserSimulator

# Configuration
GENERATIONS = 3
POPULATION_SIZE = 5
OUTPUT_PATH = "../salarsu/src/data/current_genome.json" # Shared with Next.js

default_genome = {
    "primaryColor": "hsl(222.2, 47.4%, 11.2%)", # Default Dark Blue
    "borderRadius": "0.5rem",
    "density": "comfortable" # comfortable | compact | spacious
}

def random_genome():
    h = random.randint(0, 360)
    s = random.randint(30, 90)
    l = random.randint(10, 50)
    
    return {
        "primaryColor": f"hsl({h}, {s}%, {l}%)",
        "borderRadius": f"{random.choice([0, 0.25, 0.5, 0.75, 1])}rem",
        "density": random.choice(["compact", "comfortable", "spacious"])
    }

def mutate(genome):
    new_genome = genome.copy()
    mutation = random.choice(["color", "radius", "density"])
    
    if mutation == "color":
        h = random.randint(0, 360)
        s = random.randint(30, 90)
        l = random.randint(10, 50)
        new_genome["primaryColor"] = f"hsl({h}, {s}%, {l}%)"
    elif mutation == "radius":
        new_genome["borderRadius"] = f"{random.choice([0, 0.25, 0.5, 0.75, 1])}rem"
    elif mutation == "density":
         new_genome["density"] = random.choice(["compact", "comfortable", "spacious"])
         
    return new_genome

def run_dreamtime():
    print("🌙 Dreamtime Initiated...")
    simulator = UserSimulator(persona="A sophisticated investor looking for gold coins.")
    
    # 1. Initialize Population
    population = [random_genome() for _ in range(POPULATION_SIZE)]
    population.append(default_genome) # Always keep the baseline
    
    best_genome = default_genome
    best_score = 0
    
    for gen in range(GENERATIONS):
        print(f"\n💤 Generation {gen + 1}/{GENERATIONS} Sleeping...")
        scored_pop = []
        
        for genome in population:
            evaluation = simulator.evaluate_genome(genome)
            score = evaluation.get("score", 0)
            print(f"   🧬 Genome: {genome} => Score: {score}")
            scored_pop.append((genome, score))
            
            if score > best_score:
                best_score = score
                best_genome = genome
        
        # Selection (Keep Top 50%)
        scored_pop.sort(key=lambda x: x[1], reverse=True)
        top_half = [x[0] for x in scored_pop[:len(scored_pop)//2]]
        
        # Reproduction (Mutation)
        next_gen = []
        while len(next_gen) < POPULATION_SIZE:
            parent = random.choice(top_half)
            child = mutate(parent)
            next_gen.append(child)
            
        population = next_gen
        
    print(f"\n☀️ Waking Up. Best Genome Found (Score {best_score}):")
    print(json.dumps(best_genome, indent=2))
    
    # Save to Salarsu frontend
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(best_genome, f, indent=2)
    print(f"✨ Applied to Reality: {OUTPUT_PATH}")

if __name__ == "__main__":
    run_dreamtime()
