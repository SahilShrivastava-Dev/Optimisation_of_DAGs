"""
Build Package Script

Automates the package building process for dagoptimizer.
Cleans old builds and creates fresh distribution files.

Usage:
    python scripts/build_package.py
"""

import subprocess
import shutil
import os
import sys

def print_step(step_num, message):
    """Print a formatted step message."""
    print(f"\n{'='*80}")
    print(f"STEP {step_num}: {message}")
    print(f"{'='*80}\n")

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"ERROR: {description} failed!")
        print(f"Error output: {result.stderr}")
        sys.exit(1)
    
    if result.stdout:
        print(result.stdout)
    
    print(f"SUCCESS: {description} completed!")
    return result

def main():
    """Main build process."""
    print("\n" + "="*80)
    print("DAG OPTIMIZER - PACKAGE BUILD SCRIPT")
    print("="*80)
    
    # Change to project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    print(f"\nWorking directory: {project_root}")
    
    # Step 1: Clean old builds
    print_step(1, "Cleaning old builds")
    
    dirs_to_clean = ['dist', 'build', 'src/dagoptimizer.egg-info']
    for dir_path in dirs_to_clean:
        if os.path.exists(dir_path):
            print(f"Removing {dir_path}/")
            shutil.rmtree(dir_path)
    
    print("Cleanup complete!")
    
    # Step 2: Verify setup files
    print_step(2, "Verifying setup files")
    
    required_files = [
        'setup.py',
        'pyproject.toml',
        'README.md',
        'LICENSE',
        'requirements.txt',
        'src/dagoptimizer/__init__.py',
        'src/dagoptimizer/dag_class.py',
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"* {file_path} - OK")
        else:
            print(f"X {file_path} - MISSING!")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\nERROR: Missing required files!")
        sys.exit(1)
    
    print("\nAll required files present!")
    
    # Step 3: Check dependencies
    print_step(3, "Checking build dependencies")
    
    try:
        import build
        import twine
        print("* build - OK")
        print("* twine - OK")
    except ImportError as e:
        print(f"ERROR: Missing dependency: {e}")
        print("\nInstall dependencies with:")
        print("  pip install --upgrade build twine")
        sys.exit(1)
    
    # Step 4: Build package
    print_step(4, "Building distribution packages")
    
    run_command(
        f"{sys.executable} -m build",
        "Package build"
    )
    
    # Step 5: Verify build outputs
    print_step(5, "Verifying build outputs")
    
    if not os.path.exists('dist'):
        print("ERROR: dist/ directory not created!")
        sys.exit(1)
    
    dist_files = os.listdir('dist')
    print(f"\nBuild artifacts in dist/:")
    for file in dist_files:
        file_path = os.path.join('dist', file)
        size = os.path.getsize(file_path) / 1024  # KB
        print(f"  * {file} ({size:.1f} KB)")
    
    # Check for expected files
    expected_patterns = ['.tar.gz', '.whl']
    found_patterns = []
    for pattern in expected_patterns:
        if any(pattern in f for f in dist_files):
            found_patterns.append(pattern)
    
    if len(found_patterns) != len(expected_patterns):
        print("\nWARNING: Expected both .tar.gz and .whl files!")
    
    # Step 6: Check package with twine
    print_step(6, "Validating package with twine")
    
    run_command(
        f"{sys.executable} -m twine check dist/*",
        "Package validation"
    )
    
    # Final message
    print("\n" + "="*80)
    print("BUILD SUCCESSFUL!")
    print("="*80)
    print("\nPackage is ready to upload!")
    print("\nNext steps:")
    print("  1. Test upload to TestPyPI:")
    print("     python -m twine upload --repository testpypi dist/*")
    print("\n  2. Upload to PyPI:")
    print("     python -m twine upload dist/*")
    print("\n  3. Or use the publish script:")
    print("     python scripts/publish_package.py")
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()

