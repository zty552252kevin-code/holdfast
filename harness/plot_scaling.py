#!/usr/bin/env python3
"""
HoldFast: scaling-curve figures from per-cell preview.json aggregates.

Reads runs/grid/en-{SIZE}-{SCALE}-s{SEED}/eval/preview.json (3 seeds per row;
incomplete rows are skipped with a note) + runs/baselines/en-{SIZE}-base/.
Error bars: 3-seed 95% t-CI (df=2, t=4.303) — same convention as the tables.

Usage (devbox):  python3 harness/plot_scaling.py [--runs /data/holdfast/runs]
Outputs PNG+PDF into <runs>/../figs/.
"""

import argparse
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SIZES = ["0.6B", "1.7B", "4B", "8B", "14B"]
PARAMS = {"0.6B": 0.6, "1.7B": 1.7, "4B": 4.0, "8B": 8.0, "14B": 14.0}
SCALES = ["1k", "4k", "16k"]
SEEDS = [17, 1017, 2017]
T95_DF2 = 4.303


def ci(vals):
    n = len(vals)
    m = sum(vals) / n
    if n < 2:
        return m, 0.0
    sd = math.sqrt(sum((x - m) ** 2 for x in vals) / (n - 1))
    return m, T95_DF2 * sd / math.sqrt(n)


def load(runs, lang="en"):
    grid, base = {}, {}
    for size in SIZES:
        b = runs / ("baselines/%s-%s-base/preview.json" % (lang, size))
        if b.exists():
            base[size] = json.load(open(b))
        for scale in SCALES:
            cells = []
            for seed in SEEDS:
                p = runs / ("grid/%s-%s-%s-s%d/eval/preview.json"
                            % (lang, size, scale, seed))
                if p.exists():
                    cells.append(json.load(open(p)))
            if len(cells) == len(SEEDS):
                grid[(size, scale)] = cells
            elif cells:
                print("skip incomplete row %s-%s (%d/3 seeds)"
                      % (size, scale, len(cells)))
    return grid, base


def metric(cells, key):
    return [c[key]["rate"] for c in cells]


def sel_flip(cells):
    return [c["targeted_flip"]["rate"] - c["misaligned_flip"]["rate"]
            for c in cells]


STYLE = {"1k": ("tab:blue", "o"), "4k": ("tab:green", "s"),
         "16k": ("tab:red", "^")}


def fig_hold(grid, base, out):
    fig, ax = plt.subplots(figsize=(5.2, 3.8))
    for scale in SCALES:
        xs, ms, hs = [], [], []
        for size in SIZES:
            if (size, scale) in grid:
                m, h = ci(metric(grid[(size, scale)], "hold_consistency"))
                xs.append(PARAMS[size]); ms.append(m); hs.append(h)
        if xs:
            c, mk = STYLE[scale]
            ax.errorbar(xs, ms, yerr=hs, color=c, marker=mk, capsize=3,
                        label="SFT %s" % scale)
    bx = [PARAMS[s] for s in SIZES if s in base]
    by = [base[s]["hold_consistency"]["rate"] for s in SIZES if s in base]
    ax.plot(bx, by, color="gray", marker="x", linestyle="--",
            label="prompt-only base")
    ax.set_xscale("log")
    ax.set_xticks(list(PARAMS.values()),
                  ["0.6B", "1.7B", "4B", "8B", "14B"])
    ax.set_xlabel("model parameters")
    ax.set_ylabel("hold consistency (dialogue probes)")
    ax.set_ylim(0, 1)
    ax.legend(fontsize=8)
    ax.grid(alpha=.3)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(out / ("hold_scaling.%s" % ext), dpi=200)
    plt.close(fig)


def fig_selectivity(grid, base, out, scale="4k"):
    fig, ax = plt.subplots(figsize=(5.2, 3.8))
    for key, color, mk, lbl in [
            ("targeted_flip", "tab:green", "s", "targeted flip (SFT %s)" % scale),
            ("misaligned_flip", "tab:red", "^", "misaligned flip (SFT %s)" % scale),
            ("generic_flip", "tab:orange", "v", "generic flip (SFT %s)" % scale)]:
        xs, ms, hs = [], [], []
        for size in SIZES:
            if (size, scale) in grid:
                m, h = ci(metric(grid[(size, scale)], key))
                xs.append(PARAMS[size]); ms.append(m); hs.append(h)
        if xs:
            ax.errorbar(xs, ms, yerr=hs, color=color, marker=mk, capsize=3,
                        label=lbl)
    bx = [PARAMS[s] for s in SIZES if s in base]
    for key, ls in [("targeted_flip", "--"), ("misaligned_flip", ":")]:
        by = [base[s][key]["rate"] for s in SIZES if s in base]
        ax.plot(bx, by, color="gray", linestyle=ls, marker="x",
                label="%s (base)" % key.replace("_", " "))
    ax.set_xscale("log")
    ax.set_xticks(list(PARAMS.values()),
                  ["0.6B", "1.7B", "4B", "8B", "14B"])
    ax.set_xlabel("model parameters")
    ax.set_ylabel("flip rate after remediation")
    ax.set_ylim(-0.02, 1)
    ax.legend(fontsize=7)
    ax.grid(alpha=.3)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(out / ("selectivity_%s.%s" % (scale, ext)), dpi=200)
    plt.close(fig)


def fig_guardrail(grid, base, out):
    fig, ax = plt.subplots(figsize=(5.2, 3.8))
    for scale in SCALES:
        xs, ms, hs = [], [], []
        for size in SIZES:
            if (size, scale) in grid:
                m, h = ci(metric(grid[(size, scale)], "static_correct_acc"))
                xs.append(PARAMS[size]); ms.append(m); hs.append(h)
        if xs:
            c, mk = STYLE[scale]
            ax.errorbar(xs, ms, yerr=hs, color=c, marker=mk, capsize=3,
                        label="SFT %s" % scale)
    bx = [PARAMS[s] for s in SIZES if s in base]
    by = [base[s]["static_correct_acc"]["rate"] for s in SIZES if s in base]
    ax.plot(bx, by, color="gray", marker="x", linestyle="--",
            label="prompt-only base")
    ax.set_xscale("log")
    ax.set_xticks(list(PARAMS.values()),
                  ["0.6B", "1.7B", "4B", "8B", "14B"])
    ax.set_xlabel("model parameters")
    ax.set_ylabel("correct-persona accuracy (H5 guardrail)")
    ax.set_ylim(0, 1)
    ax.legend(fontsize=8)
    ax.grid(alpha=.3)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(out / ("guardrail_h5.%s" % ext), dpi=200)
    plt.close(fig)


def fig_data_scaling(grid, out):
    fig, ax = plt.subplots(figsize=(5.2, 3.8))
    xpos = {"1k": 1, "4k": 4, "16k": 16}
    colors = {"0.6B": "tab:purple", "1.7B": "tab:blue", "4B": "tab:green",
              "8B": "tab:red", "14B": "tab:brown"}
    for size in SIZES:
        xs, ms, hs = [], [], []
        for scale in SCALES:
            if (size, scale) in grid:
                m, h = ci(metric(grid[(size, scale)], "hold_consistency"))
                xs.append(xpos[scale]); ms.append(m); hs.append(h)
        if xs:
            ax.errorbar(xs, ms, yerr=hs, color=colors[size], marker="o",
                        capsize=3, label=size)
    ax.set_xscale("log")
    ax.set_xticks([1, 4, 16], ["1k", "4k", "16k"])
    ax.set_xlabel("training dialogues")
    ax.set_ylabel("hold consistency (dialogue probes)")
    ax.set_ylim(0, 1)
    ax.legend(fontsize=8, title="model size")
    ax.grid(alpha=.3)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(out / ("hold_data_scaling.%s" % ext), dpi=200)
    plt.close(fig)


def fig_drift(grid, base, out, size="8B", scale="4k"):
    """Two panels: (a) hold-probe P(malrule) vs probe turn k, trained vs
    base; (b) trained P(malrule) vs k by dialogue type — flip_targeted
    crashes exactly at the remediation turn (k=3), flip_misaligned stays
    flat."""
    if (size, scale) not in grid:
        print("skip fig_drift: row %s-%s incomplete" % (size, scale))
        return
    cells = grid[(size, scale)]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 3.8))

    def curve(cbk_list, typ):
        ks = sorted({int(k) for c in cbk_list
                     for k in c.get(typ, {})})
        ms, hs = [], []
        for k in ks:
            vals = [c[typ][str(k)]["rate"] for c in cbk_list
                    if str(k) in c.get(typ, {})]
            m, h = ci(vals)
            ms.append(m); hs.append(h)
        return ks, ms, hs

    cbks = [c["consistency_by_k"] for c in cells]
    ks, ms, hs = curve(cbks, "hold")
    ax1.errorbar(ks, ms, yerr=hs, color="tab:green", marker="o", capsize=3,
                 label="SFT %s-%s" % (size, scale))
    if size in base:
        bk = base[size]["consistency_by_k"].get("hold", {})
        bks = sorted(int(k) for k in bk)
        ax1.plot(bks, [bk[str(k)]["rate"] for k in bks], color="gray",
                 marker="x", linestyle="--", label="prompt-only base")
    ax1.set_xlabel("probe turn k (tutor pressure accumulates)")
    ax1.set_ylabel("P(malrule answer) on hold probes")
    ax1.set_ylim(0, 1)
    ax1.legend(fontsize=8)
    ax1.grid(alpha=.3)
    ax1.set_title("(a) holding under pressure", fontsize=9)

    for typ, color, mk, lbl in [
            ("hold", "tab:green", "o", "hold (no remediation)"),
            ("flip_targeted", "tab:blue", "s", "targeted remediation @k=3"),
            ("flip_misaligned", "tab:red", "^", "misaligned remediation @k=3")]:
        ks, ms, hs = curve(cbks, typ)
        ax2.errorbar(ks, ms, yerr=hs, color=color, marker=mk, capsize=3,
                     label=lbl)
    ax2.axvline(2.5, color="black", linestyle=":", linewidth=1)
    ax2.text(2.55, 0.5, "remediation", rotation=90, fontsize=7, va="center")
    ax2.set_xlabel("probe turn k")
    ax2.set_ylabel("P(malrule answer)")
    ax2.set_ylim(-0.02, 1)
    ax2.legend(fontsize=7)
    ax2.grid(alpha=.3)
    ax2.set_title("(b) selective flip, SFT %s-%s" % (size, scale), fontsize=9)

    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(out / ("drift_%s_%s.%s" % (size, scale, ext)), dpi=200)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="/data/holdfast/runs")
    ap.add_argument("--lang", default="en",
                    help="cell prefix; zh figures get a _zh filename suffix")
    args = ap.parse_args()
    runs = Path(args.runs)
    out = runs.parent / ("figs" if args.lang == "en" else
                         "figs_%s" % args.lang)
    out.mkdir(exist_ok=True)
    grid, base = load(runs, args.lang)
    print("rows loaded: %d  baselines: %s" % (len(grid), sorted(base)))
    fig_hold(grid, base, out)
    fig_selectivity(grid, base, out, "4k")
    fig_guardrail(grid, base, out)
    fig_data_scaling(grid, out)
    fig_drift(grid, base, out, "8B", "4k")
    print("FIGS ->", out)


if __name__ == "__main__":
    main()
