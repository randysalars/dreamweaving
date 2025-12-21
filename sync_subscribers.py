#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Add the sender script directory to path so we can import EmailScheduler
sys.path.append(str(Path(__file__).parent / "scripts" / "ai" / "email_sender"))
from email_scheduler import EmailScheduler, EmailType, Subscriber

def sync_subscribers():
    project_root = Path(__file__).parent
    salarsu_path = project_root.parent / "salarsu"
    export_script = salarsu_path / "scripts" / "export-subscribers.js"
    export_file = project_root / "data" / "subscribers_export.json"

    # 1. Run the export script in salarsu
    print("Step 1: Exporting subscribers from SalarsU...")
    try:
        subprocess.run(["node", str(export_script)], cwd=str(salarsu_path), check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running export script: {e}")
        return

    # 2. Load the exported data
    if not export_file.exists():
        print(f"Error: Export file not found at {export_file}")
        return

    with open(export_file) as f:
        exported_users = json.load(f)

    # 3. Initialize Dreamweaving scheduler
    scheduler = EmailScheduler()
    new_subscribers_count = 0
    updated_subscribers_count = 0

    # Mapping tags to segments/sequences
    # (Matches segment_manager.py interests and sequences)
    tag_mapping = {
        "AI": "ai",
        "Consciousness": "consciousness",
        "Survival": "survival",
        "Health": "health",
        "Wealth": "wealth",
        "Love": "love",
        "Happiness": "happiness",
        "Spirituality": "spirituality",
        "Poetry": "poetry",
        "Old West": "old_west",
        "Treasure": "treasure",
        "Dreamweaving": "dreamweaving"
    }

    # 4. Update Dreamweaving subscribers
    print(f"Step 2: Syncing {len(exported_users)} users to Dreamweaving...")
    for user in exported_users:
        email = user["email"]
        is_new = False
        
        if email not in scheduler.subscribers:
            # Create new subscriber
            scheduler.subscribers[email] = Subscriber(
                email=email,
                subscribed_at=datetime.fromisoformat(user["createdAt"].replace("Z", "+00:00")),
                source=user.get("source") or "salarsu_sync"
            )
            new_subscribers_count += 1
            is_new = True
        else:
            updated_subscribers_count += 1
        
        subscriber = scheduler.subscribers[email]
        
        # Sync tags as interests
        tags = user.get("tags", "")
        if tags:
            tag_list = [t.strip() for t in tags.split(",") if t.strip()]
            for tag in tag_list:
                # Find matching sequence slug from tag
                seq_slug = tag_mapping.get(tag)
                if seq_slug:
                    # Add to interests if not already there
                    interest_slug = seq_slug # Using sequence slug as interest slug for simplicity
                    if interest_slug not in subscriber.interests:
                        subscriber.interests.append(interest_slug)
                    
                    # If new subscriber, trigger the sequence
                    if is_new and not subscriber.active_sequence:
                        scheduler.trigger_sequence(email, seq_slug)

    # 5. Save changes
    scheduler._save_subscribers()
    print(f"Sync complete. New: {new_subscribers_count}, Updated: {updated_subscribers_count}")

if __name__ == "__main__":
    sync_subscribers()
