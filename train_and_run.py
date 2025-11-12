"""
Master training script - Execute both V1 and V3 training
Run all training and print summary
"""

import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("=" * 70)
    print("LEASETH - MASTER TRAINING SCRIPT")
    print("=" * 70)

    scripts = [
        ("V1 Model Training", "main_v1_improved.py"),
        ("V3 Model Training", "main_v3_final.py")
    ]

    results = []

    for script_name, script_path in scripts:
        print(f"\n{'=' * 70}")
        print(f"Starting: {script_name}")
        print(f"{'=' * 70}\n")

        try:
            result = subprocess.run(
                [sys.executable, script_path],
                check=True,
                capture_output=False,
                text=True
            )
            results.append((script_name, "SUCCESS"))
            logger.info(f"{script_name} completed successfully")
        except subprocess.CalledProcessError as e:
            results.append((script_name, "FAILED"))
            logger.error(f"{script_name} failed with error: {e}")

    # Summary
    print("\n" + "=" * 70)
    print("TRAINING SUMMARY")
    print("=" * 70)

    for script_name, status in results:
        print(f"{script_name:30s} {status}")

    # Check if all successful
    if all(status == "SUCCESS" for _, status in results):
        print("\nAll models trained successfully!")
        print("Models are ready for API deployment.")
        sys.exit(0)
    else:
        print("\nSome models failed to train.")
        print("Please review the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
