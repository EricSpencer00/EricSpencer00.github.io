---
title: "Resilient"
date: 2026-05-20
description: "A statically-typed compiled language for safety-critical embedded systems, with Z3-verified contracts and self-healing runtime blocks"
tags: ["Rust", "Formal Methods", "Embedded", "AI-written"]
categories: ["Projects"]
draft: false
image: "/previews/resilient.jpg"
---

[GitHub Repo](https://github.com/EricSpencer00/Resilient) · [Examples Repo](https://github.com/EricSpencer00/Resilient-examples) · [Docs](https://ericspencer.us/Resilient/)

Resilient is the project I've been working on the longest in 2026. It's a programming language — `.rz` source files, a real compiler called `rz`, the whole thing — aimed at the corner of the world where code crashing is not an option: pacemakers, infusion pumps, anti-lock brakes, reactor coolant loops, the kind of embedded controller where the right answer to "did your software hang" is "people died." I wrote the first commit because I kept reading about formal methods in school (and writing TLA+ for the [microwave project](/projects/2025/interactive-microwave-tla/)) and noticing that the languages people actually ship to a Cortex-M chip — C, sometimes Rust, occasionally Ada — all hold the safety story in a slightly different place than where the code lives. C wants you to layer MISRA on top. Rust gets you memory safety but doesn't know what your invariants are. Ada/SPARK gets you proofs but you have to buy the certified toolchain. I wanted the contract, the runtime safety net, and the embedded story in one language, designed together from the start.

It is very much a research-grade thing built by one person. I am not pretending this is going to fly an A320. But there is an actual compiler in Rust that produces an actual bytecode VM (and a Cranelift JIT), an actual `#![no_std]` runtime that cross-compiles to `thumbv7em-none-eabihf` (Cortex-M4F) and `riscv32imac-unknown-none-elf` (HiFive / GD32V / ESP32-C3 class), and a Z3-backed verifier that discharges function contracts at compile time. The language ships a working REPL, a formatter (`rz fmt`), an LSP server (`rz --lsp`), a VS Code extension on the Marketplace, and `.rz` is registered with GitHub Linguist so syntax highlighting works in repos. None of that is the hard part. The hard parts are below.

## The two ideas that are doing the work

**Contracts the compiler can actually prove.** You write `requires` and `ensures` clauses on functions, the same way you would in SPARK or Dafny:

```
fn safe_divide(int a, int b) -> int
    requires b != 0
    ensures result * b == a
{
    return a / b;
}
```

When you build with `--features z3` (you need `libz3` installed), the compiler hands those clauses to Z3 as SMT-LIB2 obligations and the prover either discharges them or tells you it can't. The driver can also dump the proof to a `.smt2` file via `--emit-certificate ./certs/` so someone downstream can re-verify under their own copy of Z3 without trusting my binary. There's an Ed25519 signing step on top of that (`--sign-cert`) and a manifest with per-obligation SHA-256 hashes. The "don't trust the compiler, trust the certificate" piece is the part I'm most proud of, because it's the part that means this could in principle be useful evidence in a real safety case, instead of just "Eric's compiler says it's fine."

There's a hand-rolled cheap verifier for the easy cases (constant folding, let-binding propagation, inter-procedural chaining) so you don't have to install Z3 just to get a useful subset. And there's a `--infer-contracts` pass that reads a function body and suggests `requires`/`ensures` clauses you forgot — division-by-zero guards, index-bounds checks, single-return-expression invariants.

**Self-healing live blocks.** This is the part that's harder to explain without lapsing into marketing voice, so let me try in plain English. A `live { }` block is a chunk of code the runtime supervises. You attach an invariant to it. If something inside the block transiently fails — a sensor read glitches, a divide-by-zero shows up on input you didn't sanitize, the invariant breaks — the runtime doesn't panic or halt the program. It rewinds the block's local state to what it was on entry and re-runs the body. Same idea as a database transaction: either the block completes with the invariant intact, or it never happened.

```
live invariant: pressure >= 0 && pressure <= 250 {
    pressure = read_coolant_sensor();
    log_pressure(pressure);
}
```

This is meant for the class of bug where you genuinely can recover by retrying — sensor noise, a debouncing window, a one-cycle EMI spike on an industrial bus — but where the surrounding controller absolutely cannot afford to fall off the rails. The runtime backs the rewind with cycle limits and an escalation path so a permanently-broken invariant doesn't loop forever; that part is honestly still rough and the failure semantics are something I revisit every couple of weeks.

## Why the examples repo exists

A separate repo, [Resilient-examples](https://github.com/EricSpencer00/Resilient-examples), is where the language earns its motivation. Each folder is a small runnable program — usually one `.rz` file and a README — modelling a real safety-critical domain:

- `01-pacemaker` — implantable cardiac pacer, uses `live { invariant }` and `recovers_to` to guard the pacing decision logic.
- `02-infusion-pump` — drug delivery, modeled as an `actor` with an `always:` clause on the cumulative-dose ceiling.
- `03-abs-brake-controller` — anti-lock brakes, uses `forall i in lo..hi` over the wheel array and saturating arithmetic via `clamp`.
- `04-traffic-light-interlock` — road interlock, demonstrates `cluster_invariant` for the never-both-green property across two actor intersections.
- `05-reactor-coolant-monitor` — sensor stream supervised by a `live` block with a `[0, 250] kPa` envelope.
- `06-can-bus-parser` — CAN frame parser using `bytes` literals, `Result` chains, and `match` arm guards.

I built these because every time I'd talk about Resilient as "a language for embedded safety" people would reasonably ask what that actually meant. The examples are the answer. They also stress the language in a way the unit-test suite cannot — I have learned more about what's wrong with my parser from trying to write a pacemaker than from any synthetic test. The examples are deliberately scoped to safety properties (nothing bad happens) and not yet to liveness (something good eventually happens) — the TLA+ integration that would let me write liveness specs is a V2 ticket I haven't started.

## The honest WIP list

Things that work today and I'm willing to stand behind: lexer/parser are panic-free and report `line:col:` diagnostics, 50+ tests cover the lexer through the interpreter, the Cranelift JIT runs `fib(25)` in 2.8 ms (about 145× the tree-walker, within ~1.4× of native Rust on the same workload), the runtime cross-compiles to both Cortex-M4F and RISC-V rv32imac with `.text` weight at about 2.3 KiB against a 64 KiB CI budget, certificates verify under stock Z3 from the command line, and the AI-threat lint pass (`--ai-threats`) catches the off-by-one / missed-else / swallowed-error patterns that show up when you let an LLM write embedded code without reading it.

Things that are not done and I am not pretending are: I have not started tool qualification for DO-178C, ISO 26262, or IEC 62304, and I shouldn't — that's a multi-year effort with auditors. The language doesn't ship a temporal liveness checker yet. The self-hosting prototype lexes a tiny subset of the language and that's it. The standard library is small. Structs and pattern matching are partial. The formatter doesn't preserve comments. There are real holes — I keep the public list at [docs/EXPRESSIBLE_INVALID_STATES.md](https://github.com/EricSpencer00/Resilient/blob/main/docs/EXPRESSIBLE_INVALID_STATES.md) with a closing ticket against each gap, because the alternative is pretending the holes aren't there.

The other thing worth being honest about: a lot of the code in this repo was written with help from Claude, and the thing I've been most paranoid about is the LLM accidentally proving something for itself by adjusting the test instead of the implementation. The compiler's trust model is built around that — the LLM is treated as an untrusted client of the type system, never as a participant in the proof. The verifier re-derives every safety claim from the typed AST, and nothing the LLM asserts in a comment or PR description is taken at face value. There's a whole document on this ([STRUCTURAL_ENFORCEMENT.md](https://github.com/EricSpencer00/Resilient/blob/main/docs/STRUCTURAL_ENFORCEMENT.md)) and it's the design constraint that shapes more of the project than any single feature.

## Try it

```bash
curl -fsSL https://raw.githubusercontent.com/EricSpencer00/Resilient/main/scripts/install.sh | bash
rz --version
```

Or from source, if you have Rust: `cargo install --path resilient` from the cloned repo (add `--features z3` if you've got `libz3` and want SMT proofs). Then either point it at `resilient/examples/sensor_monitor.rz` for the smallest interesting thing, or clone [Resilient-examples](https://github.com/EricSpencer00/Resilient-examples) and run `./run_all.sh` for the full mission-critical sweep.

Contributions are welcome — there are open tickets across the goalpost ladder in [ROADMAP.md](https://github.com/EricSpencer00/Resilient/blob/main/ROADMAP.md) and most of them are "pick a small thing and own it." If you've worked on a real safety-critical system and the language gets something wrong about your domain, please file an issue. That feedback is the one thing I can't get from reading specs.

---

*Written with AI.*
