# PROGRESS

## 2026-07-11 11:24 — Full audit + priority-1..6 fixes complete
- Done: full repo audit (4 parallel subsystem reviews + security sweep + test/packaging pass); fixed the 6 highest-priority findings:
  1. Embedded `${var}` template resolution in workflow engine (was whole-string only).
  2. Runtime-var whitelist (`input`, `input_file`, `filename`) + scalar workflow variables in schema — all 6 shipped workflows/templates now validate.
  3. Watch/batch now write `final_output` to `io.output_dir` (`<stem>_<timestamp>.md`); failed files no longer retried forever; context reset per execution.
  4. Path traversal closed: `io` dirs must resolve inside workflow dir (PathSanitizer wired); workflow names validated.
  5. Config migration non-destructive: deep-merge + backup + model-scrub only; version from importlib.metadata/pyproject.
  6. `cli` added to coverage source; 35 regression tests in tests/test_workflow_engine_fixes.py.
- Verified: full suite 230 passed / 1 skipped (`python3 -m pytest tests/ -q` in venv).
- Next: fix remaining audit majors — call.py stdin override, __main__.py exit code, dead NL-routing block, 8 unimplemented registered skills, Gemini/OpenAI retry parity.
- Risk: all changes uncommitted; audit report exists only in chat transcript (key remaining findings copied into HANDOVER.md).
