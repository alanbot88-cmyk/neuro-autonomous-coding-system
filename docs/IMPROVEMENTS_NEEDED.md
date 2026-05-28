# SWE-bench Performance Improvements

## Status: ✅ IMPLEMENTATION COMPLETE - Official SWE-bench Harness Integrated

This document tracks the improvements made to Neuro to achieve competitive performance on SWE-bench.

## ⚠️ IMPORTANT: Official vs Fallback Evaluation

There are **TWO evaluation modes**:

### 1. Official Evaluation (Real, Fair)
Uses `swebench.harness.run_evaluation.run_instance()` to:
- Load **real** SWE-bench-Lite instances (300 instances)
- Run **actual tests** in Docker containers
- Compare against **gold patches**
- Produce **official, verifiable results**

**Requirements:**
- `swebench>=4.0.0` installed
- Docker running with swebench images
- Network access to HuggingFace for dataset

### 2. Fallback Evaluation (Development Only)
When official harness unavailable:
- Loads sample data (not real benchmarks)
- Only validates patch format (doesn't run tests)
- Results marked with `"harness": "fallback_format_only"`
- **NOT valid for SWE-bench ranking**

---

## Implementation Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Official Harness Integration | ✅ Done | Uses `swebench.harness.run_evaluation.run_instance()` |
| Real Dataset Loading | ✅ Done | Loads 300 SWE-bench-Lite instances |
| Docker Container Support | ✅ Done | Via official harness |
| Unified Diff Parsing | ✅ Done | Proper hunk offset handling |
| Repo Caching | ✅ Done | `~/.neuro/repo_cache/` |

## Architecture

```
SWE-bench Runner
├── EvalHarness
│   ├── run_with_harness() → Official evaluation
│   └── _fallback_eval() → Development only
├── UnifiedDiffParser
│   ├── parse_patch() → Parse unified diff
│   └── apply_patch() → Apply with hunk offsets
├── RepoCache
│   ├── get_repo() → Get cached repo
│   └── get_working_copy() → Create working dir
└── DockerIsolation
    ├── start_container() → Start Docker
    └── exec_in_container() → Run commands
```

## Usage

### Official Benchmark (Real, Fair)
```python
from neuro.skills.swe_bench_runner import SWEBenchRunner

runner = SWEBenchRunner(
    use_docker=True,
    use_cache=True,
    use_harness=True  # Uses official harness
)

# Load real SWE-bench-Lite dataset
instances = runner.load_dataset("lite")  # 300 real instances

# Run evaluation (requires Docker)
report = runner.run_benchmark(subset="lite", max_instances=50)
runner.print_report(report)
```

### Development (Fast, Not Official)
```python
# Without Docker/harness - uses fallback
runner = SWEBenchRunner(use_harness=False)
instances = runner._load_sample_data()  # Sample only
# Results will show: "harness": "fallback_format_only"
```

## Key Files

| File | Purpose |
|------|---------|
| `neuro/skills/swe_bench_runner.py` | Main runner with official harness |
| `neuro/validation/patch_guard.py` | Patch validation with UnifiedDiffParser |
| `requirements.txt` | Dependencies including `swebench` |

## Dependencies

```bash
pip install -e ".[swebench]"
# or
pip install swebench>=4.0.0 datasets>=2.0.0
```

## Honest Assessment

For **official SWE-bench scores** (valid for ranking):
1. Install `swebench` and `datasets`
2. Ensure Docker is running
3. Run with `use_harness=True`
4. Results will be real, fair, and verifiable

For **development/testing**:
- Fallback mode available when harness unavailable
- Results clearly marked as not official
- Useful for rapid iteration

---

*Last Updated: 2024*
*Neuro - SWE-bench Benchmark System*
