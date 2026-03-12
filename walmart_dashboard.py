"""
╔══════════════════════════════════════════════════════════════════════╗
║          WALMART BUSINESS INSIGHTS DASHBOARD — Python Analytics      ║
║          Author  : Power BI Project (Python Port)                    ║
║          Dataset : Walmart Store Sales (45 stores · 2010–2012)       ║
║          Rows    : 6,435 weekly records                               ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
import warnings
import os

warnings.filterwarnings("ignore")

# ─── CONFIG ──────────────────────────────────────────────────────────
DATA_PATH   = "data/Walmart.csv"
OUTPUT_DIR  = "images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Walmart brand palette
C = {
    "blue"      : "#0071CE",
    "yellow"    : "#FFC220",
    "dark"      : "#1A1A2E",
    "bg"        : "#F5F2EB",
    "white"     : "#FFFFFF",
    "green"     : "#1A7A4A",
    "red"       : "#C0392B",
    "orange"    : "#E67E22",
    "muted"     : "#7A7060",
    "border"    : "#E8E2D6",
    "blue_light": "#E8F4FF",
    "purple"    : "#6C3483",
}

FONT_TITLE = {"fontsize": 13, "fontweight": "bold", "color": C["dark"], "fontfamily": "DejaVu Sans"}
FONT_SUB   = {"fontsize":  9, "color": C["muted"]}
FONT_LABEL = {"fontsize":  8, "color": C["muted"]}

plt.rcParams.update({
    "figure.facecolor"  : C["bg"],
    "axes.facecolor"    : C["white"],
    "axes.edgecolor"    : C["border"],
    "axes.labelcolor"   : C["muted"],
    "axes.spines.top"   : False,
    "axes.spines.right" : False,
    "axes.grid"         : True,
    "grid.color"        : C["border"],
    "grid.linewidth"    : 0.6,
    "grid.alpha"        : 0.7,
    "xtick.color"       : C["muted"],
    "ytick.color"       : C["muted"],
    "xtick.labelsize"   : 8,
    "ytick.labelsize"   : 8,
    "font.family"       : "DejaVu Sans",
    "legend.frameon"    : True,
    "legend.framealpha" : 0.9,
    "legend.edgecolor"  : C["border"],
    "legend.fontsize"   : 8,
})


# ══════════════════════════════════════════════════════════════════════
#  1. LOAD & ENGINEER FEATURES
# ══════════════════════════════════════════════════════════════════════

def load_data(path: str) -> pd.DataFrame:
    """Load Walmart CSV and engineer all derived features."""
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()

    # Parse dates
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)

    # Time features
    df["Year"]    = df["Date"].dt.year
    df["Month"]   = df["Date"].dt.month
    df["Quarter"] = df["Date"].dt.quarter
    df["Week"]    = df["Date"].dt.isocalendar().week.astype(int)
    df["YearMonth"] = df["Date"].dt.to_period("M")
    df["YearQ"]   = df["Year"].astype(str) + "-Q" + df["Quarter"].astype(str)
    df["MonthName"] = df["Date"].dt.strftime("%b")

    # Flags
    df["Is_Holiday"] = df["Holiday_Flag"].astype(bool)

    # Economic buckets
    df["Unemp_Band"] = pd.cut(
        df["Unemployment"],
        bins=[0, 6, 8, 10, 100],
        labels=["<6%", "6–8%", "8–10%", ">10%"]
    )
    df["Fuel_Band"] = pd.cut(
        df["Fuel_Price"],
        bins=[0, 3.0, 3.5, 4.0, 99],
        labels=["<$3.0", "$3.0–3.5", "$3.5–4.0", ">$4.0"]
    )
    df["Temp_Band"] = pd.cut(
        df["Temperature"],
        bins=[-50, 32, 60, 80, 200],
        labels=["Freezing(<32°F)", "Cool(32–60°F)", "Warm(60–80°F)", "Hot(>80°F)"]
    )

    print(f"✅  Loaded {len(df):,} rows | {df['Store'].nunique()} stores | "
          f"{df['Date'].min().date()} → {df['Date'].max().date()}")
    return df


# ══════════════════════════════════════════════════════════════════════
#  2. KPI SUMMARY
# ══════════════════════════════════════════════════════════════════════

def print_kpis(df: pd.DataFrame):
    total   = df["Weekly_Sales"].sum()
    avg_wk  = df["Weekly_Sales"].mean()
    max_wk  = df["Weekly_Sales"].max()
    best_store = df.groupby("Store")["Weekly_Sales"].sum().idxmax()
    best_rev   = df.groupby("Store")["Weekly_Sales"].sum().max()
    hol_rev    = df[df["Is_Holiday"]]["Weekly_Sales"].sum()
    hol_pct    = hol_rev / total * 100

    print("\n" + "═"*60)
    print("  📊  WALMART BUSINESS INSIGHTS — KEY METRICS")
    print("═"*60)
    print(f"  💰  Total Revenue        : ${total/1e9:.3f}B")
    print(f"  📦  Avg Weekly / Store   : ${avg_wk:,.0f}")
    print(f"  🏆  Peak Single Week     : ${max_wk:,.0f}")
    print(f"  🥇  Best Store (#{best_store})   : ${best_rev/1e6:.1f}M")
    print(f"  🎉  Holiday Sales        : ${hol_rev/1e6:.1f}M  ({hol_pct:.1f}% of total)")
    print(f"  🏪  Stores Analyzed      : {df['Store'].nunique()}")
    print(f"  📅  Data Points          : {len(df):,} weekly records")
    print("═"*60 + "\n")


# ══════════════════════════════════════════════════════════════════════
#  HELPER: KPI card box
# ══════════════════════════════════════════════════════════════════════

def kpi_box(ax, title, value, subtitle, color, icon=""):
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis("off")
    rect = FancyBboxPatch((0.03, 0.08), 0.94, 0.84,
                          boxstyle="round,pad=0.02",
                          linewidth=1.5, edgecolor=color,
                          facecolor=C["white"], zorder=2)
    ax.add_patch(rect)
    # top accent strip
    ax.axhline(y=0.92, xmin=0.03, xmax=0.97, color=color, linewidth=4, zorder=3)
    ax.text(0.1, 0.72, icon, fontsize=18, va="center", zorder=4)
    ax.text(0.5, 0.54, value, ha="center", va="center",
            fontsize=17, fontweight="bold", color=C["dark"], zorder=4)
    ax.text(0.5, 0.33, title, ha="center", va="center",
            fontsize=8, color=C["muted"], zorder=4)
    ax.text(0.5, 0.17, subtitle, ha="center", va="center",
            fontsize=7, color=color, zorder=4)


# ══════════════════════════════════════════════════════════════════════
#  3. CHART 1 — KPI OVERVIEW + MONTHLY TREND
# ══════════════════════════════════════════════════════════════════════

def plot_overview(df: pd.DataFrame):
    fig = plt.figure(figsize=(20, 14), facecolor=C["bg"])
    fig.suptitle("WALMART BUSINESS INSIGHTS DASHBOARD",
                 fontsize=22, fontweight="bold", color=C["dark"],
                 y=0.98, fontfamily="DejaVu Sans")
    fig.text(0.5, 0.955, "45 Stores · Weekly Sales Data · Feb 2010 – Oct 2012 · 6,435 Records",
             ha="center", fontsize=10, color=C["muted"])

    gs = gridspec.GridSpec(3, 4, figure=fig,
                           hspace=0.45, wspace=0.35,
                           top=0.93, bottom=0.06, left=0.05, right=0.97)

    # ── KPI CARDS ──
    total     = df["Weekly_Sales"].sum()
    avg_wk    = df["Weekly_Sales"].mean()
    best_s    = df.groupby("Store")["Weekly_Sales"].sum()
    hol_rev   = df[df["Is_Holiday"]]["Weekly_Sales"].sum()
    best_rev  = best_s.max()
    best_sid  = best_s.idxmax()
    yoy_diff  = (df[df["Year"]==2011]["Weekly_Sales"].sum() /
                  df[df["Year"]==2010]["Weekly_Sales"].sum() - 1) * 100

    kpis = [
        (fig.add_subplot(gs[0, 0]), "TOTAL REVENUE",    f"${total/1e9:.2f}B", f"3-Year Network Total",     C["blue"],   "💰"),
        (fig.add_subplot(gs[0, 1]), "AVG WEEKLY / STORE",f"${avg_wk/1e3:.0f}K", f"Per store per week",     C["yellow"],  "📦"),
        (fig.add_subplot(gs[0, 2]), f"BEST STORE (#{best_sid})", f"${best_rev/1e6:.0f}M", "#1 of 45 Stores by Revenue", C["green"], "🏆"),
        (fig.add_subplot(gs[0, 3]), "HOLIDAY REVENUE",  f"${hol_rev/1e6:.0f}M",f"{hol_rev/total*100:.1f}% of Total",   C["orange"], "🎉"),
    ]
    for ax, *args in kpis:
        kpi_box(ax, *args)

    # ── MONTHLY TREND ──
    ax_trend = fig.add_subplot(gs[1, :])
    monthly  = df.groupby("YearMonth")["Weekly_Sales"].sum().reset_index()
    monthly["YM_str"] = monthly["YearMonth"].astype(str)
    monthly["Sales_M"] = monthly["Weekly_Sales"] / 1e6
    months_2010 = monthly[monthly["YM_str"].str.startswith("2010")]
    months_2011 = monthly[monthly["YM_str"].str.startswith("2011")]
    months_2012 = monthly[monthly["YM_str"].str.startswith("2012")]

    x_all = range(len(monthly))
    ax_trend.fill_between(x_all, monthly["Sales_M"], alpha=0.08, color=C["blue"])
    ax_trend.plot(list(range(len(months_2010))),
                  months_2010["Sales_M"].values, color=C["blue"],   lw=2.5, label="2010", marker="o", ms=4)
    ax_trend.plot(list(range(len(months_2010), len(months_2010)+len(months_2011))),
                  months_2011["Sales_M"].values, color=C["green"],  lw=2.5, label="2011", marker="s", ms=4)
    ax_trend.plot(list(range(len(months_2010)+len(months_2011), len(monthly))),
                  months_2012["Sales_M"].values, color=C["orange"], lw=2.5, label="2012 (partial)", marker="^", ms=4)

    # annotate peaks
    peak_idx = monthly["Sales_M"].idxmax()
    ax_trend.annotate(f"Peak: ${monthly.loc[peak_idx,'Sales_M']:.0f}M",
                      xy=(peak_idx, monthly.loc[peak_idx,"Sales_M"]),
                      xytext=(peak_idx-2, monthly.loc[peak_idx,"Sales_M"]+12),
                      arrowprops=dict(arrowstyle="->", color=C["blue"], lw=1.5),
                      fontsize=8, color=C["blue"], fontweight="bold")

    ax_trend.set_xticks(range(len(monthly)))
    ax_trend.set_xticklabels(monthly["YM_str"].values, rotation=45, ha="right", fontsize=7)
    ax_trend.set_ylabel("Sales ($M)", **FONT_LABEL)
    ax_trend.set_title("Monthly Revenue Trend — All 45 Stores Combined", **FONT_TITLE)
    ax_trend.legend(loc="upper left")
    ax_trend.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:.0f}M"))

    # holiday shading
    holiday_months = monthly[monthly["YM_str"].isin(
        df[df["Is_Holiday"]]["YearMonth"].astype(str).unique()
    )].index.tolist()
    for idx in holiday_months:
        ax_trend.axvspan(idx-0.4, idx+0.4, alpha=0.12, color=C["yellow"], zorder=0)

    # ── ANNUAL BAR ──
    ax_ann = fig.add_subplot(gs[2, 0])
    yearly = df.groupby("Year")["Weekly_Sales"].sum() / 1e6
    bars   = ax_ann.bar(yearly.index.astype(str), yearly.values,
                        color=[C["blue"], C["green"], C["orange"]],
                        edgecolor="white", linewidth=1.5, width=0.5)
    for bar, val in zip(bars, yearly.values):
        ax_ann.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 15,
                    f"${val:.0f}M", ha="center", fontsize=8, fontweight="bold", color=C["dark"])
    ax_ann.set_title("Annual Revenue", **FONT_TITLE)
    ax_ann.set_xlabel("Year", **FONT_LABEL)
    ax_ann.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x:.0f}M"))

    # ── QUARTERLY ──
    ax_q = fig.add_subplot(gs[2, 1])
    qdata   = df.groupby(["Year","Quarter"])["Weekly_Sales"].sum().reset_index()
    qdata["Label"] = "Q" + qdata["Quarter"].astype(str) + " '" + qdata["Year"].astype(str).str[-2:]
    qcolors = [C["blue"] if q==4 else (C["yellow"] if q==3 else "#90CAF9") for q in qdata["Quarter"]]
    bars_q  = ax_q.bar(range(len(qdata)), qdata["Weekly_Sales"]/1e6,
                       color=qcolors, edgecolor="white", linewidth=1, width=0.7)
    ax_q.set_xticks(range(len(qdata)))
    ax_q.set_xticklabels(qdata["Label"].values, rotation=45, ha="right", fontsize=7)
    ax_q.set_title("Quarterly Sales", **FONT_TITLE)
    ax_q.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x:.0f}M"))
    legend_els = [mpatches.Patch(color=C["blue"], label="Q4 (Holiday)"),
                  mpatches.Patch(color=C["yellow"], label="Q3"),
                  mpatches.Patch(color="#90CAF9", label="Q1/Q2")]
    ax_q.legend(handles=legend_els, fontsize=7)

    # ── HOLIDAY PIE ──
    ax_pie = fig.add_subplot(gs[2, 2])
    hol_s   = df[df["Is_Holiday"]]["Weekly_Sales"].sum()
    nhol_s  = df[~df["Is_Holiday"]]["Weekly_Sales"].sum()
    wedges, texts, autos = ax_pie.pie(
        [hol_s, nhol_s],
        labels=["Holiday\nWeeks", "Regular\nWeeks"],
        autopct="%1.1f%%", startangle=90,
        colors=[C["yellow"], C["blue"]],
        wedgeprops=dict(edgecolor="white", linewidth=2),
        textprops={"fontsize":8}
    )
    ax_pie.set_title("Holiday vs Regular", **FONT_TITLE)

    # ── YoY GROWTH ──
    ax_yoy = fig.add_subplot(gs[2, 3])
    yoy = df.groupby("Year")["Weekly_Sales"].sum()
    growth = yoy.pct_change() * 100
    colors_g = [C["green"] if v > 0 else C["red"] for v in growth.values[1:]]
    ax_yoy.bar(yoy.index[1:].astype(str), growth.values[1:],
               color=colors_g, edgecolor="white", linewidth=1, width=0.4)
    for i, (yr, g) in enumerate(zip(yoy.index[1:], growth.values[1:])):
        ax_yoy.text(i, g + 0.3, f"{g:+.1f}%",
                    ha="center", fontsize=9, fontweight="bold",
                    color=C["green"] if g > 0 else C["red"])
    ax_yoy.axhline(0, color=C["border"], linewidth=1)
    ax_yoy.set_title("YoY Revenue Growth", **FONT_TITLE)
    ax_yoy.set_ylabel("Growth %", **FONT_LABEL)
    ax_yoy.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"{x:.0f}%"))

    plt.savefig(f"{OUTPUT_DIR}/01_overview_dashboard.png", dpi=150, bbox_inches="tight",
                facecolor=C["bg"])
    plt.close()
    print("✅  Saved: 01_overview_dashboard.png")


# ══════════════════════════════════════════════════════════════════════
#  4. CHART 2 — STORE PERFORMANCE DEEP DIVE
# ══════════════════════════════════════════════════════════════════════

def plot_store_performance(df: pd.DataFrame):
    fig = plt.figure(figsize=(20, 16), facecolor=C["bg"])
    fig.suptitle("STORE PERFORMANCE ANALYSIS", fontsize=20, fontweight="bold",
                 color=C["dark"], y=0.98)
    fig.text(0.5, 0.955, "Revenue Rankings · Variability · Consistency · Top vs Bottom Performers",
             ha="center", fontsize=10, color=C["muted"])

    gs = gridspec.GridSpec(3, 3, figure=fig,
                           hspace=0.45, wspace=0.35,
                           top=0.93, bottom=0.06, left=0.05, right=0.97)

    store_agg = df.groupby("Store").agg(
        Total_Sales=("Weekly_Sales", "sum"),
        Avg_Weekly =("Weekly_Sales", "mean"),
        Std_Weekly =("Weekly_Sales", "std"),
        Max_Weekly =("Weekly_Sales", "max"),
        Min_Weekly =("Weekly_Sales", "min"),
        Weeks      =("Weekly_Sales", "count"),
    ).reset_index()
    store_agg["CV"]        = store_agg["Std_Weekly"] / store_agg["Avg_Weekly"] * 100
    store_agg["Total_M"]   = store_agg["Total_Sales"] / 1e6
    store_agg["Avg_K"]     = store_agg["Avg_Weekly"]  / 1e3
    store_agg = store_agg.sort_values("Total_Sales", ascending=False).reset_index(drop=True)
    store_agg["Rank"] = range(1, len(store_agg)+1)

    # ── ALL STORES HORIZONTAL BAR ──
    ax1 = fig.add_subplot(gs[:2, :2])
    colors_rank = [C["blue"] if i < 5 else (C["yellow"] if i < 15 else
                   (C["orange"] if i < 30 else C["red"])) for i in range(len(store_agg))]
    bars = ax1.barh(
        [f"Store {s}" for s in store_agg["Store"]],
        store_agg["Total_M"],
        color=colors_rank, edgecolor="white", linewidth=0.8, height=0.7
    )
    ax1.set_xlabel("Total Revenue ($M)", **FONT_LABEL)
    ax1.set_title("All 45 Stores — 3-Year Cumulative Revenue", **FONT_TITLE)
    ax1.xaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x:.0f}M"))
    ax1.invert_yaxis()
    ax1.tick_params(axis='y', labelsize=7)

    # add value labels for top 10
    for i, (bar, row) in enumerate(zip(bars, store_agg.itertuples())):
        if i < 10:
            ax1.text(row.Total_M + 1, bar.get_y() + bar.get_height()/2,
                     f"${row.Total_M:.0f}M", va="center", fontsize=7, color=C["dark"])

    legend_els = [mpatches.Patch(color=C["blue"],   label="Top 5"),
                  mpatches.Patch(color=C["yellow"],  label="Rank 6–15"),
                  mpatches.Patch(color=C["orange"],  label="Rank 16–30"),
                  mpatches.Patch(color=C["red"],     label="Bottom 15")]
    ax1.legend(handles=legend_els, loc="lower right", fontsize=8)

    # network avg line
    net_avg = store_agg["Total_M"].mean()
    ax1.axvline(net_avg, color=C["muted"], lw=1.5, ls="--", label=f"Network avg ${net_avg:.0f}M")
    ax1.text(net_avg+1, len(store_agg)-1, f"Avg ${net_avg:.0f}M",
             color=C["muted"], fontsize=8)

    # ── SCATTER: Avg vs Std ──
    ax2 = fig.add_subplot(gs[0, 2])
    sc = ax2.scatter(store_agg["Avg_K"], store_agg["Std_Weekly"]/1e3,
                     c=store_agg["Total_M"], cmap="Blues",
                     s=60, edgecolors=C["dark"], linewidth=0.5, alpha=0.85)
    plt.colorbar(sc, ax=ax2, label="Total Rev ($M)", fraction=0.04, pad=0.02)
    for _, row in store_agg.head(5).iterrows():
        ax2.annotate(f"#{row['Store']}", (row["Avg_K"], row["Std_Weekly"]/1e3),
                     textcoords="offset points", xytext=(4, 4), fontsize=7, color=C["blue"])
    ax2.set_xlabel("Avg Weekly Sales ($K)", **FONT_LABEL)
    ax2.set_ylabel("Std Dev ($K)", **FONT_LABEL)
    ax2.set_title("Avg Revenue vs Variability", **FONT_TITLE)

    # ── BOX PLOT top 10 ──
    ax3 = fig.add_subplot(gs[1, 2])
    top10_ids = store_agg.head(10)["Store"].tolist()
    box_data  = [df[df["Store"]==s]["Weekly_Sales"].values / 1e3 for s in top10_ids]
    bp = ax3.boxplot(box_data, patch_artist=True, notch=False,
                     medianprops=dict(color=C["yellow"], linewidth=2))
    for patch, color in zip(bp["boxes"], [C["blue"]]*5 + ["#90CAF9"]*5):
        patch.set_facecolor(color); patch.set_alpha(0.7)
    ax3.set_xticklabels([f"#{s}" for s in top10_ids], rotation=45, fontsize=7)
    ax3.set_ylabel("Weekly Sales ($K)", **FONT_LABEL)
    ax3.set_title("Top 10 — Sales Distribution", **FONT_TITLE)

    # ── GROWTH TABLE (top 10 detail) ──
    ax4 = fig.add_subplot(gs[2, :])
    ax4.axis("off")
    top10 = store_agg.head(10).copy()
    top10["Share%"]   = (top10["Total_M"] / store_agg["Total_M"].sum() * 100).round(1)
    top10["vs_avg"]   = ((top10["Total_M"] / net_avg - 1) * 100).round(1)
    top10["Max_K"]    = (top10["Max_Weekly"] / 1e3).round(1)
    top10["CV_str"]   = top10["CV"].round(1).astype(str) + "%"

    col_labels = ["Rank", "Store", "Total Rev ($M)", "Avg Weekly ($K)",
                  "Peak Week ($K)", "Variability (CV)", "Network Share %", "vs Avg Store %"]
    cell_text  = []
    for _, row in top10.iterrows():
        cell_text.append([
            f"#{int(row['Rank'])}",
            f"Store {int(row['Store'])}",
            f"${row['Total_M']:.1f}M",
            f"${row['Avg_K']:.1f}K",
            f"${row['Max_K']:.1f}K",
            row["CV_str"],
            f"{row['Share%']}%",
            f"+{row['vs_avg']:.1f}%",
        ])

    tbl = ax4.table(cellText=cell_text, colLabels=col_labels,
                    cellLoc="center", loc="center",
                    bbox=[0, 0.1, 1, 0.88])
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8.5)
    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor(C["border"])
        if r == 0:
            cell.set_facecolor(C["dark"]); cell.set_text_props(color="white", fontweight="bold")
        elif r % 2 == 0:
            cell.set_facecolor("#F0EEE8")
        else:
            cell.set_facecolor(C["white"])
    ax4.set_title("Top 10 Stores — Detailed Performance Scorecard", **FONT_TITLE, pad=14)

    plt.savefig(f"{OUTPUT_DIR}/02_store_performance.png", dpi=150, bbox_inches="tight",
                facecolor=C["bg"])
    plt.close()
    print("✅  Saved: 02_store_performance.png")


# ══════════════════════════════════════════════════════════════════════
#  5. CHART 3 — ECONOMIC FACTORS ANALYSIS
# ══════════════════════════════════════════════════════════════════════

def plot_economic_factors(df: pd.DataFrame):
    fig = plt.figure(figsize=(20, 15), facecolor=C["bg"])
    fig.suptitle("ECONOMIC FACTORS & SALES CORRELATION", fontsize=20,
                 fontweight="bold", color=C["dark"], y=0.98)
    fig.text(0.5, 0.955,
             "Unemployment · Fuel Price · CPI · Temperature — Impact on Weekly Store Sales",
             ha="center", fontsize=10, color=C["muted"])

    gs = gridspec.GridSpec(3, 3, figure=fig,
                           hspace=0.45, wspace=0.38,
                           top=0.93, bottom=0.06, left=0.06, right=0.97)

    sales_k = df["Weekly_Sales"] / 1e3

    # ── UNEMPLOYMENT SCATTER ──
    ax1 = fig.add_subplot(gs[0, 0])
    sc = ax1.scatter(df["Unemployment"], sales_k, alpha=0.25, s=8,
                     c=df["Year"], cmap="cool", edgecolors="none")
    m, b = np.polyfit(df["Unemployment"], sales_k, 1)
    x_line = np.linspace(df["Unemployment"].min(), df["Unemployment"].max(), 100)
    ax1.plot(x_line, m*x_line+b, color=C["red"], lw=2, ls="--", label=f"Trend (slope={m:.0f})")
    ax1.set_xlabel("Unemployment Rate (%)", **FONT_LABEL)
    ax1.set_ylabel("Weekly Sales ($K)", **FONT_LABEL)
    ax1.set_title("Unemployment vs Sales", **FONT_TITLE)
    ax1.legend(fontsize=7)
    corr = df["Unemployment"].corr(df["Weekly_Sales"])
    ax1.text(0.05, 0.92, f"Correlation: {corr:.3f}", transform=ax1.transAxes,
             fontsize=8, color=C["blue"], bbox=dict(boxstyle="round,pad=0.3", facecolor=C["blue_light"]))

    # ── FUEL SCATTER ──
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.scatter(df["Fuel_Price"], sales_k, alpha=0.25, s=8, color=C["orange"], edgecolors="none")
    m2, b2 = np.polyfit(df["Fuel_Price"], sales_k, 1)
    x2 = np.linspace(df["Fuel_Price"].min(), df["Fuel_Price"].max(), 100)
    ax2.plot(x2, m2*x2+b2, color=C["red"], lw=2, ls="--")
    ax2.set_xlabel("Fuel Price ($/gal)", **FONT_LABEL)
    ax2.set_ylabel("Weekly Sales ($K)", **FONT_LABEL)
    ax2.set_title("Fuel Price vs Sales", **FONT_TITLE)
    corr2 = df["Fuel_Price"].corr(df["Weekly_Sales"])
    ax2.text(0.05, 0.92, f"Correlation: {corr2:.3f}", transform=ax2.transAxes,
             fontsize=8, color=C["orange"],
             bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFF3E0"))

    # ── TEMPERATURE SCATTER ──
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.scatter(df["Temperature"], sales_k, alpha=0.25, s=8, color=C["green"], edgecolors="none")
    m3, b3 = np.polyfit(df["Temperature"], sales_k, 1)
    x3 = np.linspace(df["Temperature"].min(), df["Temperature"].max(), 100)
    ax3.plot(x3, m3*x3+b3, color=C["red"], lw=2, ls="--")
    ax3.set_xlabel("Temperature (°F)", **FONT_LABEL)
    ax3.set_ylabel("Weekly Sales ($K)", **FONT_LABEL)
    ax3.set_title("Temperature vs Sales", **FONT_TITLE)
    corr3 = df["Temperature"].corr(df["Weekly_Sales"])
    ax3.text(0.05, 0.92, f"Correlation: {corr3:.3f}", transform=ax3.transAxes,
             fontsize=8, color=C["green"],
             bbox=dict(boxstyle="round,pad=0.3", facecolor="#E8F5E9"))

    # ── UNEMPLOYMENT BAND BARS ──
    ax4 = fig.add_subplot(gs[1, 0])
    uband = df.groupby("Unemp_Band", observed=True)["Weekly_Sales"].mean() / 1e3
    colors_u = [C["green"], C["blue"], C["orange"], C["red"]]
    bars = ax4.bar(uband.index.astype(str), uband.values, color=colors_u,
                   edgecolor="white", linewidth=1.5, width=0.55)
    for bar, val in zip(bars, uband.values):
        ax4.text(bar.get_x()+bar.get_width()/2, bar.get_height()+3,
                 f"${val:.0f}K", ha="center", fontsize=8, fontweight="bold", color=C["dark"])
    ax4.set_xlabel("Unemployment Band", **FONT_LABEL)
    ax4.set_ylabel("Avg Weekly Sales ($K)", **FONT_LABEL)
    ax4.set_title("Avg Sales by Unemployment Band", **FONT_TITLE)
    ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x:.0f}K"))

    # ── FUEL BAND BARS ──
    ax5 = fig.add_subplot(gs[1, 1])
    fband = df.groupby("Fuel_Band", observed=True)["Weekly_Sales"].mean() / 1e3
    bars5 = ax5.bar(fband.index.astype(str), fband.values,
                    color=[C["green"], C["yellow"], C["orange"], C["red"]],
                    edgecolor="white", linewidth=1.5, width=0.55)
    for bar, val in zip(bars5, fband.values):
        ax5.text(bar.get_x()+bar.get_width()/2, bar.get_height()+2,
                 f"${val:.0f}K", ha="center", fontsize=8, fontweight="bold", color=C["dark"])
    ax5.set_xlabel("Fuel Price Band", **FONT_LABEL)
    ax5.set_ylabel("Avg Weekly Sales ($K)", **FONT_LABEL)
    ax5.set_title("Avg Sales by Fuel Price Band", **FONT_TITLE)
    ax5.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x:.0f}K"))

    # ── TEMP BAND BARS ──
    ax6 = fig.add_subplot(gs[1, 2])
    tband = df.groupby("Temp_Band", observed=True)["Weekly_Sales"].mean() / 1e3
    bars6 = ax6.bar(tband.index.astype(str), tband.values,
                    color=["#90CAF9", C["blue"], C["yellow"], C["red"]],
                    edgecolor="white", linewidth=1.5, width=0.55)
    for bar, val in zip(bars6, tband.values):
        ax6.text(bar.get_x()+bar.get_width()/2, bar.get_height()+2,
                 f"${val:.0f}K", ha="center", fontsize=8, fontweight="bold", color=C["dark"])
    ax6.set_xticklabels(tband.index.astype(str), rotation=15, ha="right", fontsize=7)
    ax6.set_ylabel("Avg Weekly Sales ($K)", **FONT_LABEL)
    ax6.set_title("Avg Sales by Temperature Band", **FONT_TITLE)
    ax6.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x:.0f}K"))

    # ── CORRELATION HEATMAP ──
    ax7 = fig.add_subplot(gs[2, :])
    corr_cols = ["Weekly_Sales","Temperature","Fuel_Price","CPI","Unemployment"]
    corr_matrix = df[corr_cols].corr()
    labels_clean = ["Weekly Sales","Temperature","Fuel Price","CPI","Unemployment"]
    im = ax7.imshow(corr_matrix.values, cmap="RdYlBu_r", aspect="auto", vmin=-1, vmax=1)
    plt.colorbar(im, ax=ax7, fraction=0.03, pad=0.02, label="Pearson r")
    ax7.set_xticks(range(len(labels_clean))); ax7.set_yticks(range(len(labels_clean)))
    ax7.set_xticklabels(labels_clean, fontsize=9)
    ax7.set_yticklabels(labels_clean, fontsize=9)
    for i in range(len(labels_clean)):
        for j in range(len(labels_clean)):
            val = corr_matrix.values[i, j]
            text_color = "white" if abs(val) > 0.5 else C["dark"]
            ax7.text(j, i, f"{val:.3f}", ha="center", va="center",
                     fontsize=10, fontweight="bold", color=text_color)
    ax7.set_title("Full Correlation Matrix — Economic Factors vs Sales", **FONT_TITLE)

    plt.savefig(f"{OUTPUT_DIR}/03_economic_factors.png", dpi=150, bbox_inches="tight",
                facecolor=C["bg"])
    plt.close()
    print("✅  Saved: 03_economic_factors.png")


# ══════════════════════════════════════════════════════════════════════
#  6. CHART 4 — HOLIDAY & SEASONAL ANALYSIS
# ══════════════════════════════════════════════════════════════════════

def plot_holiday_seasonal(df: pd.DataFrame):
    fig = plt.figure(figsize=(20, 14), facecolor=C["bg"])
    fig.suptitle("HOLIDAY & SEASONAL SALES PATTERNS", fontsize=20,
                 fontweight="bold", color=C["dark"], y=0.98)
    fig.text(0.5, 0.955,
             "Holiday Lift · Seasonal Rhythms · Monthly Averages · Week-of-Year Patterns",
             ha="center", fontsize=10, color=C["muted"])

    gs = gridspec.GridSpec(2, 3, figure=fig,
                           hspace=0.45, wspace=0.35,
                           top=0.93, bottom=0.06, left=0.05, right=0.97)

    # ── HOLIDAY VS REGULAR BY STORE (top 20) ──
    ax1 = fig.add_subplot(gs[0, :2])
    top20 = df.groupby("Store")["Weekly_Sales"].sum().nlargest(20).index.tolist()
    df_top = df[df["Store"].isin(top20)]
    hol_by_store   = df_top[df_top["Is_Holiday"]].groupby("Store")["Weekly_Sales"].mean()/1e3
    nhol_by_store  = df_top[~df_top["Is_Holiday"]].groupby("Store")["Weekly_Sales"].mean()/1e3
    stores_sorted  = nhol_by_store.sort_values(ascending=False).index
    x = range(len(stores_sorted))
    w = 0.35
    ax1.bar([i-w/2 for i in x], [nhol_by_store.get(s,0) for s in stores_sorted],
            width=w, label="Regular Weeks", color=C["blue"], alpha=0.8, edgecolor="white")
    ax1.bar([i+w/2 for i in x], [hol_by_store.get(s,0) for s in stores_sorted],
            width=w, label="Holiday Weeks", color=C["yellow"], alpha=0.9, edgecolor="white")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels([f"#{s}" for s in stores_sorted], fontsize=8)
    ax1.set_ylabel("Avg Weekly Sales ($K)", **FONT_LABEL)
    ax1.set_title("Holiday vs Regular Week Sales — Top 20 Stores", **FONT_TITLE)
    ax1.legend()
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x:.0f}K"))

    # ── HOLIDAY LIFT DISTRIBUTION ──
    ax2 = fig.add_subplot(gs[0, 2])
    hol_avg  = df[df["Is_Holiday"]]["Weekly_Sales"].mean()
    nhol_avg = df[~df["Is_Holiday"]]["Weekly_Sales"].mean()
    lift     = (hol_avg / nhol_avg - 1) * 100
    ax2.bar(["Regular\nWeeks","Holiday\nWeeks"],
            [nhol_avg/1e3, hol_avg/1e3],
            color=[C["blue"], C["yellow"]], edgecolor="white", linewidth=2, width=0.45)
    ax2.text(1, hol_avg/1e3+10, f"+{lift:.1f}% lift\nvs regular",
             ha="center", fontsize=10, fontweight="bold", color=C["orange"])
    ax2.set_ylabel("Avg Weekly Sales ($K)", **FONT_LABEL)
    ax2.set_title("Holiday Sales Lift", **FONT_TITLE)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x:.0f}K"))

    # ── MONTHLY AVERAGE (Seasonal pattern) ──
    ax3 = fig.add_subplot(gs[1, 0])
    monthly_avg = df.groupby("Month")["Weekly_Sales"].mean() / 1e3
    month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    bar_colors  = [C["yellow"] if m in [11,12] else (C["blue"] if m in [7,8] else "#90CAF9")
                   for m in range(1,13)]
    bars = ax3.bar(month_names, monthly_avg.values, color=bar_colors,
                   edgecolor="white", linewidth=1.5, width=0.7)
    ax3.set_title("Seasonal Monthly Averages", **FONT_TITLE)
    ax3.set_ylabel("Avg Weekly Sales ($K)", **FONT_LABEL)
    ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x:.0f}K"))
    ax3.tick_params(axis='x', rotation=30)
    peak_m = monthly_avg.idxmax()
    ax3.text(peak_m-1, monthly_avg[peak_m]+8, "Peak\n(Holiday Season)",
             ha="center", fontsize=7, color=C["yellow"], fontweight="bold")

    # ── WEEK-OF-YEAR PATTERN ──
    ax4 = fig.add_subplot(gs[1, 1])
    weekly_avg = df.groupby("Week")["Weekly_Sales"].mean() / 1e3
    holiday_weeks = df[df["Is_Holiday"]]["Week"].unique()
    ax4.plot(weekly_avg.index, weekly_avg.values, color=C["blue"], lw=2, alpha=0.8)
    ax4.fill_between(weekly_avg.index, weekly_avg.values, alpha=0.08, color=C["blue"])
    for hw in holiday_weeks:
        if hw in weekly_avg.index:
            ax4.scatter(hw, weekly_avg[hw], color=C["yellow"], s=60, zorder=5)
    ax4.scatter([], [], color=C["yellow"], s=60, label="Holiday Weeks")
    ax4.set_xlabel("Week of Year", **FONT_LABEL)
    ax4.set_ylabel("Avg Sales ($K)", **FONT_LABEL)
    ax4.set_title("Sales by Week of Year", **FONT_TITLE)
    ax4.legend(fontsize=8)
    ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x:.0f}K"))

    # ── HOLIDAY SALES BY YEAR ──
    ax5 = fig.add_subplot(gs[1, 2])
    hol_yr  = df[df["Is_Holiday"]].groupby("Year")["Weekly_Sales"].agg(["mean","sum","count"])
    nhol_yr = df[~df["Is_Holiday"]].groupby("Year")["Weekly_Sales"].agg(["mean","sum"])
    x_yr    = np.arange(len(hol_yr))
    ax5.bar(x_yr-0.2, nhol_yr["mean"]/1e3, 0.35, label="Regular Avg", color=C["blue"], alpha=0.8)
    ax5.bar(x_yr+0.2, hol_yr["mean"]/1e3,  0.35, label="Holiday Avg", color=C["yellow"], alpha=0.9)
    ax5.set_xticks(x_yr)
    ax5.set_xticklabels(hol_yr.index.astype(str))
    ax5.set_ylabel("Avg Sales ($K)", **FONT_LABEL)
    ax5.set_title("Holiday vs Regular by Year", **FONT_TITLE)
    ax5.legend(fontsize=8)
    ax5.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x:.0f}K"))

    plt.savefig(f"{OUTPUT_DIR}/04_holiday_seasonal.png", dpi=150, bbox_inches="tight",
                facecolor=C["bg"])
    plt.close()
    print("✅  Saved: 04_holiday_seasonal.png")


# ══════════════════════════════════════════════════════════════════════
#  7. CHART 5 — ADVANCED ANALYTICS
# ══════════════════════════════════════════════════════════════════════

def plot_advanced(df: pd.DataFrame):
    fig = plt.figure(figsize=(20, 14), facecolor=C["bg"])
    fig.suptitle("ADVANCED ANALYTICS & FORECASTING SIGNALS", fontsize=20,
                 fontweight="bold", color=C["dark"], y=0.98)
    fig.text(0.5, 0.955,
             "Rolling Averages · Volatility · Store Clustering · Network Distribution",
             ha="center", fontsize=10, color=C["muted"])

    gs = gridspec.GridSpec(2, 3, figure=fig,
                           hspace=0.45, wspace=0.38,
                           top=0.93, bottom=0.06, left=0.05, right=0.97)

    # ── ROLLING AVERAGE TREND ──
    ax1 = fig.add_subplot(gs[0, :2])
    net_weekly = df.groupby("Date")["Weekly_Sales"].sum().reset_index()
    net_weekly = net_weekly.sort_values("Date")
    net_weekly["Sales_M"]    = net_weekly["Weekly_Sales"] / 1e6
    net_weekly["MA4"]        = net_weekly["Sales_M"].rolling(4).mean()
    net_weekly["MA13"]       = net_weekly["Sales_M"].rolling(13).mean()
    net_weekly["Volatility"] = net_weekly["Sales_M"].rolling(8).std()

    ax1.fill_between(net_weekly["Date"], net_weekly["Sales_M"], alpha=0.15, color=C["blue"])
    ax1.plot(net_weekly["Date"], net_weekly["Sales_M"], alpha=0.35,
             color=C["blue"], lw=1, label="Weekly (raw)")
    ax1.plot(net_weekly["Date"], net_weekly["MA4"],  color=C["orange"], lw=2.5,
             label="4-wk Moving Avg")
    ax1.plot(net_weekly["Date"], net_weekly["MA13"], color=C["green"],  lw=2.5,
             ls="--", label="13-wk (Quarterly) MA")

    ax1.set_ylabel("Network Sales ($M)", **FONT_LABEL)
    ax1.set_title("Network-Wide Sales with Rolling Averages", **FONT_TITLE)
    ax1.legend(fontsize=8)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x:.0f}M"))
    ax1.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%b '%y"))
    ax1.tick_params(axis='x', rotation=30)

    # ── VOLATILITY ──
    ax1b = ax1.twinx()
    ax1b.fill_between(net_weekly["Date"], net_weekly["Volatility"],
                      alpha=0.2, color=C["red"])
    ax1b.set_ylabel("Volatility (Std $M)", color=C["red"], fontsize=8)
    ax1b.tick_params(axis='y', colors=C["red"], labelsize=7)
    ax1b.spines["right"].set_edgecolor(C["red"])

    # ── DISTRIBUTION HISTOGRAM ──
    ax2 = fig.add_subplot(gs[0, 2])
    ax2.hist(df["Weekly_Sales"]/1e3, bins=60, color=C["blue"], alpha=0.75,
             edgecolor="white", linewidth=0.5)
    mean_val = df["Weekly_Sales"].mean()/1e3
    med_val  = df["Weekly_Sales"].median()/1e3
    ax2.axvline(mean_val, color=C["red"],    lw=2, ls="--", label=f"Mean  ${mean_val:.0f}K")
    ax2.axvline(med_val,  color=C["yellow"], lw=2, ls="--", label=f"Median ${med_val:.0f}K")
    ax2.set_xlabel("Weekly Sales ($K)", **FONT_LABEL)
    ax2.set_ylabel("Frequency", **FONT_LABEL)
    ax2.set_title("Sales Distribution", **FONT_TITLE)
    ax2.legend(fontsize=8)
    ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x:.0f}K"))

    # ── STORE PERFORMANCE HEATMAP (store × year-month) ──
    ax3 = fig.add_subplot(gs[1, :2])
    top15  = df.groupby("Store")["Weekly_Sales"].sum().nlargest(15).index.tolist()
    df_t15 = df[df["Store"].isin(top15)].copy()
    df_t15["YM"] = df_t15["Date"].dt.to_period("M").astype(str)
    pivot  = df_t15.groupby(["Store","YM"])["Weekly_Sales"].mean().unstack().fillna(0) / 1e3
    pivot  = pivot.sort_index()

    # Limit columns for readability
    cols_show = pivot.columns[::3]
    pivot_show = pivot[cols_show]
    im3 = ax3.imshow(pivot_show.values, cmap="YlOrRd", aspect="auto")
    plt.colorbar(im3, ax=ax3, label="Avg Weekly Sales ($K)", fraction=0.02, pad=0.01)
    ax3.set_yticks(range(len(pivot_show)))
    ax3.set_yticklabels([f"Store {s}" for s in pivot_show.index], fontsize=8)
    ax3.set_xticks(range(len(cols_show)))
    ax3.set_xticklabels(cols_show, rotation=45, ha="right", fontsize=7)
    ax3.set_title("Store × Monthly Sales Heatmap (Top 15 Stores)", **FONT_TITLE)

    # ── PERCENTILE BANDS ──
    ax4 = fig.add_subplot(gs[1, 2])
    store_totals = df.groupby("Store")["Weekly_Sales"].sum() / 1e6
    percentiles  = [0, 25, 50, 75, 90, 100]
    labels_p     = ["Bottom 25%","25–50%","50–75%","75–90%","Top 10%"]
    cuts = pd.qcut(store_totals, q=[0,.25,.50,.75,.90,1.0], labels=labels_p)
    tier_counts = cuts.value_counts().reindex(labels_p)
    tier_revenue = store_totals.groupby(cuts).sum().reindex(labels_p)
    colors_p = [C["red"],"#FF8A65",C["yellow"],C["blue"],C["green"]]
    bars_p = ax4.barh(labels_p, tier_revenue.values, color=colors_p,
                      edgecolor="white", linewidth=1.5, height=0.5)
    for bar, (cnt, rev) in zip(bars_p, zip(tier_counts, tier_revenue)):
        ax4.text(bar.get_width()+1, bar.get_y()+bar.get_height()/2,
                 f"${rev:.0f}M ({cnt} stores)",
                 va="center", fontsize=8, color=C["dark"])
    ax4.set_xlabel("Total Revenue ($M)", **FONT_LABEL)
    ax4.set_title("Revenue by Store Tier", **FONT_TITLE)
    ax4.xaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x:.0f}M"))
    ax4.set_xlim(0, tier_revenue.max()*1.55)

    plt.savefig(f"{OUTPUT_DIR}/05_advanced_analytics.png", dpi=150, bbox_inches="tight",
                facecolor=C["bg"])
    plt.close()
    print("✅  Saved: 05_advanced_analytics.png")


# ══════════════════════════════════════════════════════════════════════
#  8. MAIN
# ══════════════════════════════════════════════════════════════════════

def main():
    print("\n🚀  Walmart Business Insights Dashboard — Starting...\n")
    df = load_data(DATA_PATH)
    print_kpis(df)
    print("📊  Generating charts...\n")
    plot_overview(df)
    plot_store_performance(df)
    plot_economic_factors(df)
    plot_holiday_seasonal(df)
    plot_advanced(df)
    print(f"\n✅  All 5 charts saved to → ./{OUTPUT_DIR}/")
    print("📁  Files: 01_overview_dashboard.png through 05_advanced_analytics.png\n")


if __name__ == "__main__":
    main()
