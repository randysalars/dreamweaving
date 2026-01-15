#!/usr/bin/env python3
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent / "scripts" / "ai" / "email_sender"))
from email_scheduler import EmailScheduler, EmailType, Subscriber

def run_test():
    print("=== Dreamweaving Sequence Verification ===")
    
    # Initialize scheduler (will use local files in data/)
    scheduler = EmailScheduler()
    
    # Use test data path to avoid messing with real data
    test_email = "test_user@example.com"
    
    # 1. Clean up test user if exists
    if test_email in scheduler.subscribers:
        del scheduler.subscribers[test_email]
    
    print(f"\n1. Triggering 'ai' sequence for {test_email}...")
    scheduler.trigger_sequence(test_email, "ai")
    
    subscriber = scheduler.subscribers[test_email]
    assert subscriber.active_sequence == "ai"
    assert subscriber.sequence_index == 0
    print("   [OK] Sequence triggered.")

    print("\n2. Processing sequences (Email 1)...")
    results = scheduler.process_sequences()
    assert len(results) == 1
    assert results[0]["success"] is True
    assert subscriber.sequence_index == 1
    print(f"   [OK] Email 1 sent. Index: {subscriber.sequence_index}")

    print("\n3. Processing again immediately (7-day rule check)...")
    results = scheduler.process_sequences()
    assert len(results) == 0
    print("   [OK] 7-day rule blocked immediate follow-up.")

    print("\n4. Mocking time travel (+8 days)...")
    subscriber.last_email_at = datetime.now() - timedelta(days=8)
    results = scheduler.process_sequences()
    assert len(results) == 1
    assert subscriber.sequence_index == 2
    print(f"   [OK] Email 2 sent after 8 days. Index: {subscriber.sequence_index}")

    print("\n5. Mocking final email...")
    subscriber.sequence_index = 9
    subscriber.last_email_at = datetime.now() - timedelta(days=8)
    results = scheduler.process_sequences()
    assert len(results) == 1
    assert subscriber.sequence_index == 10
    assert subscriber.active_sequence is None
    print(f"   [OK] Final email sent. Sequence completed and cleared.")

    print("\nVerification Complete: All logic tests passed.")

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"\n[FAIL] Verification failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
