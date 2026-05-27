"""
modules/analytics.py
Lab 8 — Student Performance Analytics using NumPy, Pandas, Matplotlib
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")           # non-interactive backend for Streamlit
import matplotlib.pyplot as plt
import io
from typing import Optional


SUBJECTS = ["math", "science", "english"]   # fallback default


def get_subject_cols(df: pd.DataFrame) -> list[str]:
    """Return score columns — everything except student_id and name."""
    return [c for c in df.columns if c not in ("student_id", "name")]


# ── Data Preparation ──────────────────────────────────────────────────────────
def records_to_dataframe(records: list[dict]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame(columns=["student_id", "name"])
    df = pd.DataFrame(records)
    for col in get_subject_cols(df):
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


# ── Statistical Analysis (Lab 8 NumPy/Pandas pattern) ───────────────────────
def compute_statistics(df: pd.DataFrame) -> dict:
    subj_cols = get_subject_cols(df)
    if df.empty or not subj_cols:
        return {}
    scores = df[subj_cols].to_numpy()
    return {
        "mean":    dict(zip(subj_cols, np.mean(scores, axis=0).round(2))),
        "median":  dict(zip(subj_cols, np.median(scores, axis=0).round(2))),
        "std_dev": dict(zip(subj_cols, np.std(scores, axis=0).round(2))),
        "summary": df[subj_cols].describe().round(2),
    }


def get_top_performers(df: pd.DataFrame) -> dict:
    tops = {}
    for subj in get_subject_cols(df):
        if not df.empty:
            idx = df[subj].idxmax()
            tops[subj] = df.loc[idx, "name"]
    return tops


def compute_average_per_student(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    subj_cols = get_subject_cols(df)
    if subj_cols:
        df["average"] = df[subj_cols].mean(axis=1).round(2)
    return df


# ── Grade Distribution ─────────────────────────────────────────────────────────
def grade_distribution(df: pd.DataFrame) -> dict:
    if df.empty or not get_subject_cols(df):
        return {}
    df = compute_average_per_student(df)
    bins   = [0, 40, 60, 75, 90, 101]
    labels = ["F (Needs Improvement)", "D (Average)", "C (Good)",
              "B (Very Good)", "A (Excellent)"]
    df["grade_band"] = pd.cut(df["average"], bins=bins, labels=labels,
                               right=False, include_lowest=True)
    return df["grade_band"].value_counts().to_dict()


# ── Chart Generators ──────────────────────────────────────────────────────────
def _fig_to_bytes(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=120)
    buf.seek(0)
    plt.close(fig)
    return buf.read()


def chart_avg_per_subject(stats: dict) -> Optional[bytes]:
    """Bar chart: average score per subject."""
    if not stats or "mean" not in stats:
        return None
    fig, ax = plt.subplots(figsize=(6, 4))
    subjects = list(stats["mean"].keys())
    values   = list(stats["mean"].values())
    colors   = ["#4C72B0", "#55A868", "#C44E52"]
    bars = ax.bar([s.capitalize() for s in subjects], values, color=colors,
                  edgecolor="white", linewidth=0.8)
    ax.bar_label(bars, fmt="%.1f", padding=3)
    ax.set_ylim(0, 105)
    ax.set_title("Average Score per Subject", fontweight="bold", pad=12)
    ax.set_ylabel("Average Score")
    ax.set_xlabel("Subject")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return _fig_to_bytes(fig)


def chart_student_comparison(df: pd.DataFrame) -> Optional[bytes]:
    if df.empty:
        return None
    subj_cols = get_subject_cols(df)
    if not subj_cols:
        return None
    plot_df = df.set_index("name")[subj_cols].copy()
    plot_df.columns = [c.capitalize() for c in plot_df.columns]

    fig, ax = plt.subplots(figsize=(max(6, len(df) * 1.2), 4))
    plot_df.plot(kind="bar", ax=ax, edgecolor="white", linewidth=0.5)
    ax.set_title("Student Performance Comparison", fontweight="bold", pad=12)
    ax.set_ylabel("Score")
    ax.set_xlabel("Student")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")
    ax.legend(title="Subject", bbox_to_anchor=(1.01, 1), loc="upper left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return _fig_to_bytes(fig)


def chart_grade_distribution(dist: dict) -> Optional[bytes]:
    """Horizontal bar chart for grade distribution."""
    if not dist:
        return None
    labels = list(dist.keys())
    values = list(dist.values())
    colors = ["#d9534f", "#f0ad4e", "#5bc0de", "#5cb85c", "#337ab7"]

    fig, ax = plt.subplots(figsize=(7, max(3, len(labels) * 0.7)))
    bars = ax.barh(labels, values,
                   color=colors[:len(labels)], edgecolor="white")
    ax.bar_label(bars, padding=4)
    ax.set_title("Grade Distribution", fontweight="bold", pad=12)
    ax.set_xlabel("Number of Students")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return _fig_to_bytes(fig)


def chart_avg_per_student(df: pd.DataFrame) -> Optional[bytes]:
    """Line chart: average score per student."""
    if df.empty:
        return None
    df = compute_average_per_student(df)
    fig, ax = plt.subplots(figsize=(max(6, len(df) * 1.2), 4))
    ax.plot(df["name"], df["average"], marker="o", color="#4C72B0",
            linewidth=2, markersize=7)
    for x, y in zip(df["name"], df["average"]):
        ax.annotate(f"{y:.1f}", (x, y), textcoords="offset points",
                    xytext=(0, 8), ha="center", fontsize=9)
    ax.set_ylim(0, 105)
    ax.set_title("Average Score per Student", fontweight="bold", pad=12)
    ax.set_ylabel("Average Score")
    ax.set_xlabel("Student")
    ax.set_xticklabels(df["name"], rotation=30, ha="right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return _fig_to_bytes(fig)
