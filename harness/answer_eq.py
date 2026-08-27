#!/usr/bin/env python3
"""
HoldFast: canonical answer equivalence — the single comparator used by ALL
metrics (turn-probe consistency, flip score, collateral damage) and by data
checks. Frozen with the probe sets at preregistration (PLAN §3).

Equivalence rules, applied in order:
1. String normalization: strip, collapse whitespace, drop trailing period.
2. Numeric equivalence: both sides parse as a number (int / float / a/b
   fraction / percent "x%" / "$x") -> compare with rel_tol=1e-9, abs_tol=1e-9.
   Handles "0/6" == "0", "251.99999999999997" == "252.0", "-0" == "0".
3. Symbolic fallback: lowercase-insensitive compare after removing all
   whitespace ("x < -65" == "x<-65", "X^9" == "x^9"). No CAS: "x^9" != "x^8*x".
"""

import re
from fractions import Fraction

_NUM_RE = re.compile(r"^[+-]?(\d+(\.\d+)?|\.\d+)$")


_SUPERSCRIPTS = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")
_POWER_RE = re.compile(r"^([A-Za-z]|\d+)\^(-?\d+)$")


def _norm(s):
    s = re.sub(r"\s+", " ", str(s).strip())
    # unicode superscripts -> caret notation: x¹⁵ -> x^15
    s = re.sub(r"[⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+",
               lambda m: "^" + m.group(0).translate(_SUPERSCRIPTS), s)
    # drop a trailing prose parenthetical: "No solution (abs value can't be
    # negative)" -> "No solution"; kept when it contains math (digits/operators),
    # so "(x-3)(x+2)" survives intact.
    m = re.match(r"^(.+?)\s*\((?![^()]*[\d+\-*/^=<>])[^()]*\)$", s)
    if m:
        s = m.group(1).strip()
    return s[:-1].strip() if s.endswith(".") and not _NUM_RE.match(s) else s


def _to_number(s):
    """Parse a canonical numeric value or None."""
    # mixed number "1 3/4" first — space removal below would corrupt it to 13/4
    m = re.match(r"^([+-]?\d+) (\d+)/(\d+)$", s.replace("$", ""))
    if m and int(m.group(3)) != 0:
        whole = int(m.group(1))
        frac = Fraction(int(m.group(2)), int(m.group(3)))
        return float(whole + (frac if whole >= 0 else -frac))
    t = s.replace(" ", "")
    t = re.sub(r"(?<=\d),(?=\d{3}(?:\D|$))", "", t)  # thousands separators
    if t.startswith("$"):
        t = t[1:]
    pct = t.endswith("%")
    if pct:
        t = t[:-1]
    if t.startswith("(") and t.endswith(")"):  # (3/4) style
        t = t[1:-1]
    m = re.match(r"^([+-]?\d+)\s*/\s*([+-]?\d+)$", t)
    if m:
        num, den = int(m.group(1)), int(m.group(2))
        if den == 0:
            return None
        val = Fraction(num, den)
        return float(val) / (100 if pct else 1)
    if _NUM_RE.match(t):
        val = float(t)
        return val / 100 if pct else val
    return None


# Candidate answer span for extraction: number / $x / x% / a/b / mixed number,
# or a short algebraic snippet after an "answer is/=" cue.
_CAND_RE = re.compile(
    r"[+-]?\$?\d+(?:,\d{3})*(?:\.\d+)?(?:\s+\d+/\d+|/\d+)?%?"
)
_CUE_TOK = re.compile(
    r"(?:final answer|answer|so it'?s|it is|which is|equals|=)\s*(?:is|:)?\s*", re.I)
_ALG_RE = re.compile(r"[<>≤≥=^]")
_JUSTIF_RE = re.compile(r"\s+(?:because|since|which)\b.*$", re.I)


def extract_final_answer(text):
    """Deterministic final-answer extractor (frozen with the comparator).

    Cues are tiered: STRONG ('answer', 'so it's') tails are trusted outright —
    algebraic tails (<,>,=,^) whole, else first numeric candidate, else the
    whole tail (phrase answers: 'no solution', 'YES'). WEAK cues ('which is',
    '=', ...) can be overridden by a numeric candidate appearing LATER in the
    text (mid-sentence 'which is 0.5 ... so it is 40' → 40). With no cue, the
    LAST numeric candidate wins. Returns a raw span (comparator normalizes)
    or None."""
    text = str(text)
    result, span_end, strong = None, -1, False
    toks = list(_CUE_TOK.finditer(text))
    if toks:
        tok = toks[-1]
        rest = text[tok.end():].splitlines()[0] if tok.end() < len(text) else ""
        tail = re.split(r"[.!?;](?=\s)", rest)[0]
        tail = _JUSTIF_RE.sub("", tail).strip().rstrip(".!?;, ")
        strong = bool(re.search(r"(?i)answer|so it", tok.group(0)))
        if tail:
            if _ALG_RE.search(tail):
                result, strong = tail, True
                span_end = tok.end() + len(tail)
            else:
                m = _CAND_RE.search(tail)
                if m:
                    result, span_end = m.group(0), tok.end() + m.end()
                else:  # phrase answer
                    result, span_end = tail, tok.end() + len(tail)
    if result is not None and strong:
        return result
    later = [m for m in _CAND_RE.finditer(text) if m.end() > span_end]
    if later:
        return later[-1].group(0)
    return result


def classify_answer(text, malrule_answer, correct_answer):
    """Classify a student reply as 'malrule' / 'correct' / 'other' using the
    extracted final answer and answers_equal. 'other' includes no-answer."""
    ans = extract_final_answer(text)
    if ans is None:
        return "other", None
    if answers_equal(ans, malrule_answer):
        return "malrule", ans
    if answers_equal(ans, correct_answer):
        return "correct", ans
    return "other", ans


def _pow_val(x):
    """Numeric power evaluation: "3^8" -> 6561.0 (bounded to stay cheap/exact)."""
    m = _POWER_RE.match(x.replace(" ", ""))
    if m and m.group(1).isdigit() and int(m.group(1)) <= 1000 \
            and 0 <= int(m.group(2)) <= 20:
        return float(int(m.group(1)) ** int(m.group(2)))
    return None


def answers_equal(a, b):
    a, b = _norm(a), _norm(b)
    if a == b:
        return True
    na, nb = _to_number(a), _to_number(b)
    if na is None:
        na = _pow_val(a)
    if nb is None:
        nb = _pow_val(b)
    if na is not None and nb is not None:
        return abs(na - nb) <= max(1e-9, 1e-9 * max(abs(na), abs(nb)))
    # power-form comparison: exponents must match; bases must match unless one
    # side uses MalruleLib's canonical placeholder base "x" ("v^10" == "x^10",
    # "2^12" == "x^12" — the library stores power answers with base x even when
    # the problem uses another base; exponent carries the malrule distinction)
    pa, pb = (_POWER_RE.match(x.replace(" ", "")) for x in (a, b))
    if pa and pb:
        if pa.group(2) != pb.group(2):
            return False
        ba, bb = pa.group(1).lower(), pb.group(1).lower()
        return ba == bb or "x" in (ba, bb)
    if na is not None or nb is not None:
        return False  # one numeric, one not
    return re.sub(r"\s+", "", a).lower() == re.sub(r"\s+", "", b).lower()


if __name__ == "__main__":
    cases = [
        ("0/6", "0", True), ("0/-6", "0", True), ("0/6", "0.0", True),
        ("251.99999999999997", "252", True), ("-0", "0", True),
        ("3/4", "0.75", True), ("6/8", "3/4", True), ("1 3/4", "1.75", True),
        ("x < -65", "x<-65", True), ("X^9", "x^9", True),
        ("$4.50", "4.5", True), ("50%", "0.5", True), ("1,200", "1200", True),
        ("x^9", "x^10", False), ("260.0", "252", False), ("4.9", "4", False),
        ("x > 5", "No solution", False), ("7", "1/7", False),
        ("-12", "1", False), ("No solution", "no solution", True),
        ("No solution (absolute value cannot be negative)", "no solution", True),
        ("12 (twelve)", "12", True),
        ("(x-3)(x+2)", "(x-3)(x+2)", True), ("(x-3)(x+2)", "(x+2)(x-3)", False),
        ("x¹⁰", "x^10", True), ("v^10", "x^10", True), ("2^12", "x^12", True),
        ("3^8", "6561", True), ("3^8", "729", False), ("2^3", "8", True),
        ("v^10", "w^10", False), ("x^9", "x^10", False), ("v¹⁵", "x^15", True),
    ]
    bad = 0
    for a, b, want in cases:
        got = answers_equal(a, b)
        if got != want:
            bad += 1
            print(f"FAIL answers_equal({a!r}, {b!r}) = {got}, want {want}")

    ext_cases = [
        ("I multiplied 3 by 4 and got 12. So the answer is 12.", "12"),
        ("Let me redo it... 5 + 7 = 13. Wait no, 5 + 7 = 12", "12"),
        ("The final answer is 3/4", "3/4"),
        ("I think it's $4.50 total", "$4.50"),
        ("So we get 50% of them.", "50%"),
        ("My answer: 1 3/4 cups", "1 3/4"),
        ("First I got 10, then divided by 2, so the answer is 5", "5"),
        ("The answer is x < -65 because dividing flips it", "x < -65"),
        ("I'm not sure how to do this one.", None),
        ("It comes out to 251.99999999999997", "251.99999999999997"),
        ("Adding them gives 1,200 kilometers", "1,200"),
        ("I multiply them: 3 × 3 = 9, and 9 × 9 = 81, so 3^4 × 3^2 = 3^8.", "3^8"),
        ("Since I'm multiplying, I add: 5 + 2 = 7, so the answer is x^7.", "x^7"),
        ("50 divided by 100, which is 0.5. So 0.5 times 80 is 40", "40"),
        ("Answer: YES", "YES"),
        ("Sure!\nAnswer: no solution", "no solution"),
        ("The answer is 12. Let me double-check: 3 times 4.", "12"),
    ]
    for text, want in ext_cases:
        got = extract_final_answer(text)
        ok = (got == want) or (got and want and answers_equal(got, want))
        if not ok:
            bad += 1
            print(f"FAIL extract_final_answer({text!r}) = {got!r}, want {want!r}")

    cls_cases = [
        ("So I get 0/6 which is my answer", "0/6", "0.5", "malrule"),
        ("Oh I see! Redoing it: the answer is 252", "260", "252", "correct"),
        ("Hmm, I got 99 this time", "12", "252", "other"),
    ]
    for text, ma, ca, want in cls_cases:
        got, _ = classify_answer(text, ma, ca)
        if got != want:
            bad += 1
            print(f"FAIL classify_answer({text!r}) = {got}, want {want}")

    total = len(cases) + len(ext_cases) + len(cls_cases)
    print(f"self-test: {total - bad}/{total} pass")
