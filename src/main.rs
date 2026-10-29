//! Bounded deterministic offline diagnostic. No RPC, PQC, escrow, or certification.
use std::{env, process};
const SEED: u64 = 0x55AA55AA55AA55AA;
const MIX: u64 = 0x9E3779B97F4A7C15;
const LIMIT: u64 = 100_000;

fn step(s: u64) -> u64 { s ^ s.rotate_right(7) ^ MIX }
fn evolve(seed: u64, n: u64) -> u64 {
    let mut s = seed;
    for _ in 0..n { s = step(s); }
    s
}
fn number(s: &str) -> Result<u64, String> {
    if let Some(hex) = s.strip_prefix("0x") {
        u64::from_str_radix(hex, 16).map_err(|_| "invalid hexadecimal u64".to_string())
    } else {
        s.parse::<u64>().map_err(|_| "invalid decimal u64".to_string())
    }
}
fn parse(args: &[String]) -> Result<(u64, u64), String> {
    let (mut seed, mut steps) = (SEED, 10_000_u64);
    let (mut seen_seed, mut seen_steps) = (false, false);
    let mut i = 0;
    while i < args.len() {
        match args[i].as_str() {
            "--seed" if !seen_seed => {
                i += 1;
                seed = number(args.get(i).ok_or("missing seed")?)?;
                seen_seed = true;
            }
            "--steps" if !seen_steps => {
                i += 1;
                steps = number(args.get(i).ok_or("missing steps")?)?;
                seen_steps = true;
            }
            _ => return Err("unknown or repeated argument".to_string()),
        }
        i += 1;
    }
    if steps > LIMIT { return Err("step limit exceeded".to_string()); }
    Ok((seed, steps))
}
fn main() {
    let args: Vec<String> = env::args().skip(1).collect();
    let (seed, steps) = match parse(&args) {
        Ok(x) => x,
        Err(e) => { eprintln!("offline diagnostic error: {e}"); process::exit(2); }
    };
    println!(r#"{{"mode":"offline-diagnostic","steps":{},"state_hex":"{:016x}"}}"#, steps, evolve(seed, steps));
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn identity() { assert_eq!(evolve(0x1234, 0), 0x1234); }
    #[test] fn transition() { assert_eq!(evolve(0x1234, 1), step(0x1234)); }
    #[test] fn reproducible() { assert_eq!(evolve(7, 1000), evolve(7, 1000)); }
    #[test] fn bad_numbers() {
        assert!(number("-1").is_err());
        assert!(number("0x10000000000000000").is_err());
        assert!(number("0x").is_err());
    }
    #[test] fn bad_args() {
        assert!(parse(&["--steps".into()]).is_err());
        assert!(parse(&["--seed".into(), "1".into(), "--seed".into(), "2".into()]).is_err());
        assert!(parse(&["--rpc".into()]).is_err());
        assert!(parse(&["--steps".into(), "100001".into()]).is_err());
    }
}
