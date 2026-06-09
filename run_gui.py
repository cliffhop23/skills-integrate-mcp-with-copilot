"""Top-level entry point — run from the repo root: python run_gui.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from gui import main
main()
