"""
Quick Publish Script

One-command script to build and publish dagoptimizer package.
Runs build, validation, and optionally publishes to TestPyPI or PyPI.

Usage:
    python scripts/quick_publish.py          # Build only
    python scripts/quick_publish.py --test   # Build + publish to TestPyPI
    python scripts/quick_publish.py --prod   # Build + publish to PyPI
"""

import subprocess
import sys
import os
import argparse

def run_script(script_name, *args):
    """Run another Python script."""
    command = [sys.executable, script_name] + list(args)
    print(f"\n{'='*80}")
    print(f"Running: {' '.join(command)}")
    print(f"{'='*80}\n")
    
    result = subprocess.run(command)
    return result.returncode == 0

def main():
    """Main process."""
    parser = argparse.ArgumentParser(description='Quick build and publish')
    parser.add_argument('--test', action='store_true',
                       help='Publish to TestPyPI after building')
    parser.add_argument('--prod', action='store_true',
                       help='Publish to PyPI after building (PRODUCTION)')
    args = parser.parse_args()
    
    # Change to project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    print("\n" + "="*80)
    print("QUICK PUBLISH - DAG OPTIMIZER")
    print("="*80)
    
    # Step 1: Build
    print("\nStep 1: Building package...")
    if not run_script('scripts/build_package.py'):
        print("\nBuild failed! Aborting.")
        sys.exit(1)
    
    # Step 2: Publish (if requested)
    if args.test or args.prod:
        print(f"\nStep 2: Publishing...")
        
        if args.test:
            if not run_script('scripts/publish_package.py', '--test'):
                print("\nPublish to TestPyPI failed!")
                sys.exit(1)
        else:
            if not run_script('scripts/publish_package.py'):
                print("\nPublish to PyPI failed!")
                sys.exit(1)
    else:
        print("\n" + "="*80)
        print("BUILD COMPLETE - READY TO PUBLISH")
        print("="*80)
        print("\nPackage built successfully!")
        print("\nTo publish:")
        print("  Test upload:       python scripts/quick_publish.py --test")
        print("  Production upload: python scripts/quick_publish.py --prod")
        print("\nOr use individual scripts:")
        print("  python scripts/publish_package.py --test")
        print("  python scripts/publish_package.py")
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()

