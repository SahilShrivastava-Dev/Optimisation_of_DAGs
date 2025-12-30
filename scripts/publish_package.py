"""
Publish Package Script

Interactive script to publish dagoptimizer to PyPI (or TestPyPI).

Usage:
    python scripts/publish_package.py [--test]
    
    --test: Upload to TestPyPI instead of production PyPI
"""

import subprocess
import sys
import os
import argparse

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*80}")
    print(f"{title.center(80)}")
    print(f"{'='*80}\n")

def run_command(command):
    """Run a command interactively."""
    print(f"\nRunning: {command}\n")
    result = subprocess.run(command, shell=True)
    return result.returncode == 0

def confirm(question):
    """Ask user for confirmation."""
    while True:
        response = input(f"\n{question} (yes/no): ").lower().strip()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("Please answer 'yes' or 'no'")

def check_dist_exists():
    """Check if dist/ directory exists with files."""
    if not os.path.exists('dist'):
        return False
    
    dist_files = os.listdir('dist')
    return len(dist_files) > 0

def main():
    """Main publish process."""
    parser = argparse.ArgumentParser(description='Publish dagoptimizer package')
    parser.add_argument('--test', action='store_true', 
                       help='Upload to TestPyPI instead of PyPI')
    args = parser.parse_args()
    
    # Change to project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    if args.test:
        print_header("PUBLISHING TO TEST PYPI")
        repository = "testpypi"
        repository_url = "https://test.pypi.org/"
    else:
        print_header("PUBLISHING TO PRODUCTION PYPI")
        repository = "pypi"
        repository_url = "https://pypi.org/"
    
    # Step 1: Check if dist/ exists
    if not check_dist_exists():
        print("ERROR: No distribution files found in dist/")
        print("\nPlease build the package first:")
        print("  python scripts/build_package.py")
        print("  OR")
        print("  python -m build")
        sys.exit(1)
    
    # Show what will be uploaded
    print("Files to upload:")
    for file in os.listdir('dist'):
        file_path = os.path.join('dist', file)
        size = os.path.getsize(file_path) / 1024
        print(f"  * {file} ({size:.1f} KB)")
    
    # Confirm
    if not confirm(f"Upload these files to {repository_url}?"):
        print("\nUpload cancelled.")
        sys.exit(0)
    
    # Upload
    print(f"\nUploading to {repository}...")
    print("\nCredentials:")
    print("  Username: __token__")
    print("  Password: <your API token>")
    print("\nIf you haven't created an API token:")
    if args.test:
        print("  1. Go to https://test.pypi.org/manage/account/token/")
    else:
        print("  1. Go to https://pypi.org/manage/account/token/")
    print("  2. Create a new token")
    print("  3. Copy and paste it when prompted")
    
    if not confirm("Ready to upload?"):
        print("\nUpload cancelled.")
        sys.exit(0)
    
    # Run twine upload
    if args.test:
        command = f"{sys.executable} -m twine upload --repository testpypi dist/*"
    else:
        command = f"{sys.executable} -m twine upload dist/*"
    
    success = run_command(command)
    
    if success:
        print_header("UPLOAD SUCCESSFUL!")
        
        print("Your package is now published!")
        print(f"\nView it at:")
        if args.test:
            print("  https://test.pypi.org/project/dagoptimizer/")
        else:
            print("  https://pypi.org/project/dagoptimizer/")
        
        print("\nUsers can now install it with:")
        if args.test:
            print("  pip install --index-url https://test.pypi.org/simple/ dagoptimizer")
        else:
            print("  pip install dagoptimizer")
        
        print("\nNext steps:")
        if args.test:
            print("  1. Test the installation in a clean environment")
            print("  2. If everything works, publish to production:")
            print("     python scripts/publish_package.py")
        else:
            print("  1. Create a GitHub release tag:")
            print("     git tag -a v1.0.0 -m 'Release version 1.0.0'")
            print("     git push origin v1.0.0")
            print("  2. Update documentation")
            print("  3. Announce the release!")
        
        print("\n" + "="*80 + "\n")
    else:
        print("\nERROR: Upload failed!")
        print("\nCommon issues:")
        print("  * Package version already exists - increment version number")
        print("  * Invalid credentials - check your API token")
        print("  * Network issues - check internet connection")
        print("\nSee PUBLISHING_GUIDE.md for troubleshooting.")
        sys.exit(1)

if __name__ == "__main__":
    main()

