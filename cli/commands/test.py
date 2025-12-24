"""
CLI command: test - Run the test suite
"""
import subprocess
import sys
from pathlib import Path


def test_command(**kwargs):
    """
    Run the SuperSkills test suite.

    Args:
        quick: Run fast tests only (skip slow integration tests)
        file: Run specific test file only
        coverage: Generate coverage report

    Returns:
        Exit code from pytest
    """
    quick = kwargs.get('quick', False)
    test_file = kwargs.get('file')
    coverage = kwargs.get('coverage', False)
    verbose = kwargs.get('verbose', False)

    # Check if pytest is installed
    check_result = subprocess.run(
        [sys.executable, '-m', 'pytest', '--version'],
        capture_output=True,
        text=True
    )

    if check_result.returncode != 0:
        print("❌ pytest not found\n")
        print("Install dev dependencies:")
        print("  pip install -e \".[dev]\"\n")
        print("Or install pytest directly:")
        print("  pip install pytest pytest-mock pytest-asyncio")
        return 1

    # Build pytest command
    cmd = [sys.executable, '-m', 'pytest']

    # Target
    if test_file:
        test_path = Path('tests') / test_file
        if not test_path.exists():
            # Try with test_ prefix if not provided
            test_path = Path('tests') / f'test_{test_file}'
        if not test_path.exists():
            print(f"❌ Test file not found: {test_file}")
            print("\nAvailable test files:")
            for tf in Path('tests').glob('test_*.py'):
                print(f"  • {tf.name}")
            return 1
        cmd.append(str(test_path))
    else:
        cmd.append('tests/')

    # Verbosity
    if verbose:
        cmd.append('-vv')
    else:
        cmd.append('-v')

    # Quick mode - skip slow tests
    if quick:
        cmd.extend(['-m', 'not slow'])
        print("🚀 Running quick tests (skipping slow integration tests)\n")

    # Coverage
    if coverage:
        cmd.extend([
            '--cov=cli',
            '--cov=superskills',
            '--cov-report=html',
            '--cov-report=term-missing'
        ])
        print("📊 Running tests with coverage analysis\n")

    # Show command
    print(f"Command: {' '.join(cmd)}\n")
    print("=" * 60)

    # Run tests
    try:
        result = subprocess.run(cmd)

        print("=" * 60)

        if result.returncode == 0:
            print("\n✅ All tests passed!")

            if coverage:
                coverage_path = Path.cwd() / 'htmlcov' / 'index.html'
                if coverage_path.exists():
                    print(f"\n📊 Coverage report: file://{coverage_path}")
        else:
            print(f"\n❌ Tests failed with exit code {result.returncode}")

        return result.returncode

    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        return 1
