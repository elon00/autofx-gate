# AutoFX Gate — evidence-scoped remediation (2026-10-29)

This branch replaces a fabricated five-step "reality" harness and corrupted Python test file with a **bounded, deterministic, offline diagnostic**. The Rust binary accepts `--seed` and `--steps`, emits JSON, and refuses malformed or excessive inputs. Rust unit tests and Python subprocess tests cover positive and negative cases.

## Scope and non-claims

- The offline state transition is a diagnostic, **not** Conway's Game of Life, a live QuickNode relayer, a financial escrow, an FX settlement protocol, or a PQC implementation.
- There is no evidence here of FIPS validation, production certification, RPC connectivity, or public-chain deployment.
- CodeQL configuration scans **Python** only. Rust source is checked by `cargo test`, not by this CodeQL job.
- Do not use this repository to move funds or assert readiness. `SECURITY_APPROVED = false` and `DEPLOYMENT_READY = false` until actual scoped functionality, integration tests, security review and operational evidence exist.

## Verification

```bash
cargo test --offline
cargo build --offline
python3 tests/reality_check_harness.py
python3 tests/reality_battery.py
```

GitHub Actions on the PR head must complete successfully before the above can be called CI-verified. The previous `100/100` prints were assertions about literals, not evidence. The full AutoFX system is still incomplete.

## Remaining engineering tasks

1. Specify and implement real FX order/quote, decimal-safe accounting, authorization and settlement logic with bounded failure handling.
2. Add real contract security tests and replay/idempotency protections where on-chain or x402 functionality is eventually implemented.
3. Add live integration tests only in an explicitly approved, safe environment; do not use production credentials or spend gas.
4. Independently review cryptography and security claims before any deployment readiness assessment.
