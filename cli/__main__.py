"""
Allow CLI execution via: python -m cli

This enables both execution patterns:
  - superskills --help  (console script entry point)
  - python -m cli --help  (module execution)
"""
from cli.main import main

if __name__ == '__main__':
    main()
