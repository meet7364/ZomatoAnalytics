import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Zomato Bangalore Analytics",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Google Font + CSS ─────────────────────────────────────────────────────────
st.markdown(
    """
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"], .stApp, .stMarkdown, p, div, span, label, button {
        font-family: 'DM Sans', sans-serif !important;
    }
    .stApp { background-color: #F7F5F0; }
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E4E0D8;
    }
    [data-testid="stSidebar"] * { font-family: 'DM Sans', sans-serif !important; }

    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E4E0D8;
        border-radius: 14px;
        padding: 18px 16px 14px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .kpi-value {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 1.75rem;
        font-weight: 700;
        color: #1E1E1C;
        line-height: 1.15;
    }
    .kpi-label {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.7rem;
        color: #999;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 5px;
    }
    .sec-head {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.95rem;
        font-weight: 600;
        color: #1E1E1C;
        border-left: 3px solid #C94F24;
        padding-left: 10px;
        margin: 24px 0 14px 0;
    }
    .filter-pill {
        display: inline-block;
        background: #FEF0EA;
        color: #C94F24;
        border: 1px solid #F5C4B0;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .page-title {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 1.5rem;
        font-weight: 700;
        color: #E23744;
        margin-bottom: 2px;
    }
    .page-sub {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.82rem;
        color: #999;
        margin-bottom: 16px;
    }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1.5rem !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ── Color palette ─────────────────────────────────────────────────────────────
C = {
    "primary": "#C94F24",
    "orange2": "#E07A47",
    "amber": "#F0B060",
    "teal": "#297A72",
    "teal2": "#45A89E",
    "green": "#3E7A50",
    "slate": "#546370",
    "bg": "#FFFFFF",
    "grid": "#F0EDE6",
    "text": "#1E1E1C",
    "muted": "#999",
}

DISC_10 = [
    "#C94F24",
    "#E07A47",
    "#F0B060",
    "#297A72",
    "#45A89E",
    "#3E7A50",
    "#A0522D",
    "#546370",
    "#8B7355",
    "#C0392B",
]

CHART_H = 390


FONT = dict(family="DM Sans, sans-serif", color=C["text"], size=12)
FONT_SM = dict(family="DM Sans, sans-serif", color=C["text"], size=11)
FONT_AX = dict(family="DM Sans, sans-serif", color=C["text"], size=11)


def base_layout(fig, title="", h=CHART_H):
    fig.update_layout(
        paper_bgcolor=C["bg"],
        plot_bgcolor=C["bg"],
        font=FONT,
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=13, color=C["text"], family="DM Sans, sans-serif"),
            x=0,
            xref="paper",
        ),
        margin=dict(l=16, r=16, t=48, b=48),
        height=h,
        xaxis=dict(
            gridcolor=C["grid"],
            linecolor=C["grid"],
            tickfont=dict(family="DM Sans, sans-serif", color=C["text"], size=11),
            title_font=dict(family="DM Sans, sans-serif", color=C["text"], size=12),
        ),
        yaxis=dict(
            gridcolor=C["grid"],
            linecolor=C["grid"],
            tickfont=dict(family="DM Sans, sans-serif", color=C["text"], size=11),
            title_font=dict(family="DM Sans, sans-serif", color=C["text"], size=12),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans, sans-serif", color=C["text"], size=11),
        ),
    )
    return fig


# ── Session state for cross-filter ───────────────────────────────────────────
for key in ["xf_location", "xf_rest_type"]:
    if key not in st.session_state:
        st.session_state[key] = None


# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/zomato_clean.csv")
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    if "rate" in df.columns and df["rate"].dtype == object:
        df["rate"] = (
            df["rate"].astype(str).str.replace("/5", "", regex=False).str.strip()
        )
        df["rate"] = pd.to_numeric(df["rate"], errors="coerce")

    cost_col = next((c for c in df.columns if "cost" in c.lower()), None)
    if cost_col:
        df[cost_col] = (
            df[cost_col].astype(str).str.replace(",", "", regex=False).str.strip()
        )
        df[cost_col] = pd.to_numeric(df[cost_col], errors="coerce")
        if cost_col != "approx_cost":
            df.rename(columns={cost_col: "approx_cost"}, inplace=True)
    else:
        df["approx_cost"] = pd.NA

    if "votes" in df.columns:
        df["votes"] = pd.to_numeric(df["votes"], errors="coerce")

    for col in ["online_order", "book_table"]:
        if col in df.columns:
            v = df[col].astype(str).str.strip().str.upper()
            df[col] = v.map(
                {"TRUE": "Yes", "FALSE": "No", "YES": "Yes", "NO": "No"}
            ).fillna(df[col])
    return df


df_raw = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🍽️ Zomato Bangalore")
    st.markdown("---")
    st.markdown("**Global Filters**")

    sel_locations = st.multiselect(
        "Location",
        options=sorted(df_raw["location"].dropna().unique()),
        placeholder="All locations",
    )
    sel_types = st.multiselect(
        "Restaurant Type",
        options=sorted(df_raw["restaurant_type"].dropna().unique()),
        placeholder="All types",
    )
    online_opt = st.radio("Online Order", ["All", "Yes", "No"], horizontal=True)

    cost_min = int(df_raw["approx_cost"].dropna().min())
    cost_max = int(df_raw["approx_cost"].dropna().max())
    cost_range = st.slider(
        "Cost for Two (₹)", cost_min, cost_max, (cost_min, cost_max), step=50
    )
    min_rating = st.slider("Min Rating", 0.0, 5.0, 0.0, step=0.5)

    st.markdown("---")
    if st.button("✕  Clear chart selection", use_container_width=True):
        st.session_state.xf_location = None
        st.session_state.xf_rest_type = None
        st.rerun()
    st.markdown(
        "<small style='color:#bbb'>Click a bar or pie slice to<br>cross-filter all charts</small>",
        unsafe_allow_html=True,
    )

# ── Global filter ─────────────────────────────────────────────────────────────
df = df_raw.copy()
if sel_locations:
    df = df[df["location"].isin(sel_locations)]
if sel_types:
    df = df[df["restaurant_type"].isin(sel_types)]
if online_opt != "All":
    df = df[df["online_order"] == online_opt]
df = df[
    (df["approx_cost"].isna() | df["approx_cost"].between(cost_range[0], cost_range[1]))
    & (df["rate"].isna() | (df["rate"] >= min_rating))
]

# ── Cross-filter ──────────────────────────────────────────────────────────────
df_xf = df.copy()
if st.session_state.xf_location:
    df_xf = df_xf[df_xf["location"] == st.session_state.xf_location]
if st.session_state.xf_rest_type:
    df_xf = df_xf[df_xf["restaurant_type"] == st.session_state.xf_rest_type]

active = []
if st.session_state.xf_location:
    active.append(f"📍 {st.session_state.xf_location}")
if st.session_state.xf_rest_type:
    active.append(f"🍴 {st.session_state.xf_rest_type}")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="page-title">Zomato Bangalore Analytics Dashboard</div>',
    unsafe_allow_html=True,
)
if active:
    pills = " ".join([f'<span class="filter-pill">{f}</span>' for f in active])
    st.markdown(
        f'<div style="margin-bottom:10px">{pills}'
        f'<span style="font-size:0.75rem;color:#999"> — {len(df_xf):,} restaurants</span></div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f'<div class="page-sub">Showing {len(df):,} of {len(df_raw):,} restaurants · '
        f"Click a bar or pie slice to<br>cross-filter all charts.",
        unsafe_allow_html=True,
    )

# ── KPI Row ───────────────────────────────────────────────────────────────────
r = df_xf
kpis = [
    (f"{len(r):,}", "Restaurants"),
    (f"{r['location'].nunique()}", "Locations"),
    (f"{r['rate'].mean():.2f} ★" if r["rate"].notna().any() else "—", "Avg Rating"),
    (
        (
            f"₹{int(r['approx_cost'].median()):,}"
            if r["approx_cost"].notna().any()
            else "—"
        ),
        "Median Cost",
    ),
    (f"{int(r['votes'].sum()):,}" if r["votes"].notna().any() else "—", "Total Votes"),
]
for col, (val, label) in zip(st.columns(5), kpis):
    with col:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-value">{val}</div>'
            f'<div class="kpi-label">{label}</div></div>',
            unsafe_allow_html=True,
        )

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Location Insights
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-head">Location Insights</div>', unsafe_allow_html=True)
top_n = st.slider("Top N locations", 5, 25, 15, key="loc_n")
c1, c2 = st.columns(2)

with c1:
    loc_df = (
        df_xf.groupby("location")
        .agg(count=("name", "count"), avg_rating=("rate", "mean"))
        .reset_index()
        .sort_values("count", ascending=False)
        .head(top_n)
        .sort_values("count", ascending=True)
    )
    loc_df["bar_color"] = loc_df["location"].apply(
        lambda x: "#C94F24" if x == st.session_state.xf_location else "#E07A47"
    )
    fig1 = go.Figure(
        go.Bar(
            x=loc_df["count"],
            y=loc_df["location"],
            orientation="h",
            marker_color=loc_df["bar_color"],
            customdata=loc_df["avg_rating"].round(2).values,
            hovertemplate="<b>%{y}</b><br>Restaurants: %{x:,}<br>Avg Rating: %{customdata:.2f}<extra></extra>",
        )
    )
    base_layout(fig1, f"Top {top_n} Locations by Restaurant Count")
    fig1.update_layout(margin=dict(l=160, r=16, t=48, b=40))
    ev1 = st.plotly_chart(
        fig1,
        use_container_width=True,
        on_select="rerun",
        key="ch1",
        selection_mode="points",
    )
    if ev1 and ev1.get("selection", {}).get("points"):
        pt = ev1["selection"]["points"][0]
        loc = pt.get("label") or pt.get("y")
        if loc:
            st.session_state.xf_location = (
                None if loc == st.session_state.xf_location else loc
            )
            st.rerun()

with c2:
    loc_r = (
        df_xf.groupby("location")
        .agg(avg_rating=("rate", "mean"), count=("name", "count"))
        .reset_index()
        .query("count >= 30")
        .sort_values("avg_rating", ascending=False)
        .head(15)
        .sort_values("avg_rating", ascending=True)
    )
    fig2 = px.bar(
        loc_r,
        x="avg_rating",
        y="location",
        orientation="h",
        color="avg_rating",
        color_continuous_scale=["#F0B060", "#297A72"],
        labels={"avg_rating": "Avg Rating", "location": "", "count": "# Restaurants"},
        hover_data={"count": True, "avg_rating": ":.2f"},
    )
    fig2.update_coloraxes(showscale=False)
    fig2.update_layout(xaxis=dict(range=[3.0, 4.6]))
    base_layout(fig2, "Top Locations by Avg Rating (min 30 restaurants)")
    fig2.update_layout(margin=dict(l=160, r=16, t=48, b=40))
    st.plotly_chart(fig2, use_container_width=True, key="ch2")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Ratings & Cost
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="sec-head">Ratings & Cost Distribution</div>', unsafe_allow_html=True
)
c3, c4 = st.columns(2)

with c3:
    fig3 = px.histogram(
        df_xf.dropna(subset=["rate"]),
        x="rate",
        nbins=18,
        color_discrete_sequence=[C["primary"]],
        labels={"rate": "Rating", "count": "Restaurants"},
    )
    fig3.update_traces(marker_line_color="#FFF", marker_line_width=1.2)
    base_layout(fig3, "Rating Distribution")
    st.plotly_chart(fig3, use_container_width=True, key="ch3")

with c4:
    cost_plot = df_xf[df_xf["approx_cost"].between(50, 3000)].dropna(
        subset=["approx_cost"]
    )
    fig4 = px.histogram(
        cost_plot,
        x="approx_cost",
        nbins=30,
        color_discrete_sequence=[C["teal"]],
        labels={"approx_cost": "Cost for Two (₹)", "count": "Restaurants"},
    )
    fig4.update_traces(marker_line_color="#FFF", marker_line_width=1.2)
    base_layout(fig4, "Cost Distribution (up to ₹3,000)")
    st.plotly_chart(fig4, use_container_width=True, key="ch4")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Online Order & Booking
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="sec-head">Order & Booking Behaviour</div>', unsafe_allow_html=True
)
c5, c6 = st.columns(2)

with c5:
    top_t = (
        df_xf.groupby("restaurant_type")["name"]
        .count()
        .sort_values(ascending=False)
        .head(8)
        .index.tolist()
    )
    on_df = (
        df_xf[
            df_xf["restaurant_type"].isin(top_t)
            & df_xf["online_order"].notna()
            & df_xf["rate"].notna()
        ]
        .groupby(["restaurant_type", "online_order"])
        .agg(avg_rating=("rate", "mean"), count=("name", "count"))
        .reset_index()
        .query("count >= 10")
    )
    # Highlight selected type
    on_df["opacity"] = on_df["restaurant_type"].apply(
        lambda x: (
            1.0
            if (not st.session_state.xf_rest_type or x == st.session_state.xf_rest_type)
            else 0.35
        )
    )
    fig5 = px.bar(
        on_df,
        x="restaurant_type",
        y="avg_rating",
        color="online_order",
        barmode="group",
        color_discrete_map={"Yes": C["teal"], "No": C["primary"]},
        labels={
            "restaurant_type": "",
            "avg_rating": "Avg Rating",
            "online_order": "Online Order",
        },
        hover_data={"count": True, "avg_rating": ":.2f"},
    )
    fig5.update_layout(
        xaxis_tickangle=-30,
        xaxis=dict(
            tickfont=dict(family="DM Sans, sans-serif", color=C["text"], size=10),
            title_font=dict(family="DM Sans, sans-serif", color=C["text"], size=12),
        ),
    )
    base_layout(fig5, "Online vs Offline: Avg Rating by Type")
    fig5.update_layout(margin=dict(l=16, r=16, t=48, b=80))
    ev5 = st.plotly_chart(
        fig5,
        use_container_width=True,
        on_select="rerun",
        key="ch5",
        selection_mode="points",
    )
    if ev5 and ev5.get("selection", {}).get("points"):
        pt = ev5["selection"]["points"][0]
        rt = pt.get("label") or pt.get("x")
        if rt:
            st.session_state.xf_rest_type = (
                None if rt == st.session_state.xf_rest_type else rt
            )
            st.rerun()

with c6:
    book_df = (
        df_xf[df_xf["book_table"].notna() & df_xf["rate"].notna()]
        .groupby("book_table")
        .agg(avg_rating=("rate", "mean"), count=("name", "count"))
        .reset_index()
    )
    fig6 = px.bar(
        book_df,
        x="book_table",
        y="avg_rating",
        color="book_table",
        color_discrete_map={"Yes": C["green"], "No": C["orange2"]},
        text=book_df["avg_rating"].round(2),
        labels={"book_table": "Table Booking", "avg_rating": "Avg Rating"},
        hover_data={"count": True},
    )
    fig6.update_traces(
        textposition="outside",
        marker_line_width=0,
        width=0.32,
        textfont=dict(family="DM Sans, sans-serif", size=13),
    )
    fig6.update_layout(showlegend=False, yaxis=dict(range=[0, 5.2]))
    base_layout(fig6, "Avg Rating: Table Booking vs No Booking")
    st.plotly_chart(fig6, use_container_width=True, key="ch6")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — Cuisines & Restaurant Types
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="sec-head">Cuisines & Restaurant Types</div>', unsafe_allow_html=True
)
c7, c8 = st.columns(2)

with c7:
    min_cc = st.slider("Min restaurants per cuisine", 50, 300, 100, key="cslider")
    cuis_df = (
        df_xf[df_xf["cuisines"].notna() & df_xf["rate"].notna()]
        .groupby("cuisines")
        .agg(avg_rating=("rate", "mean"), count=("name", "count"))
        .reset_index()
        .query(f"count >= {min_cc}")
        .sort_values("avg_rating", ascending=False)
        .head(15)
        .sort_values("avg_rating", ascending=True)
    )
    fig7 = px.bar(
        cuis_df,
        x="avg_rating",
        y="cuisines",
        orientation="h",
        color="count",
        color_continuous_scale=["#F0B060", "#C94F24"],
        labels={"avg_rating": "Avg Rating", "cuisines": "", "count": "# Restaurants"},
        hover_data={"count": True, "avg_rating": ":.2f"},
    )
    fig7.update_coloraxes(
        colorbar=dict(
            title="Count",
            thickness=10,
            len=0.5,
            title_font=dict(family="DM Sans, sans-serif", color=C["text"], size=11),
            tickfont=dict(family="DM Sans, sans-serif", color=C["text"], size=10),
        )
    )
    fig7.update_layout(xaxis=dict(range=[3.4, 4.4]))
    base_layout(fig7, f"Top Cuisines by Avg Rating (min {min_cc})", h=420)
    fig7.update_layout(margin=dict(l=160, r=16, t=48, b=48))
    st.plotly_chart(fig7, use_container_width=True, key="ch7")

with c8:
    mode = st.radio(
        "Show by", ["Count", "Avg Rating"], horizontal=True, key="type_mode"
    )
    type_df = (
        df_xf[df_xf["restaurant_type"].notna()]
        .groupby("restaurant_type")
        .agg(count=("name", "count"), avg_rating=("rate", "mean"))
        .reset_index()
        .sort_values("count", ascending=False)
        .head(10)
    )
    if mode == "Count":
        pull = [
            0.08 if t == st.session_state.xf_rest_type else 0
            for t in type_df["restaurant_type"]
        ]
        fig8 = go.Figure(
            go.Pie(
                labels=type_df["restaurant_type"],
                values=type_df["count"],
                hole=0.44,
                pull=pull,
                marker_colors=DISC_10[: len(type_df)],
                textfont=dict(family="DM Sans, sans-serif", size=11),
                hovertemplate="<b>%{label}</b><br>Count: %{value:,}<br>%{percent}<extra></extra>",
            )
        )
        base_layout(fig8, "Restaurant Type Breakdown — Count", h=420)
        ev8 = st.plotly_chart(
            fig8,
            use_container_width=True,
            on_select="rerun",
            key="ch8",
            selection_mode="points",
        )
        if ev8 and ev8.get("selection", {}).get("points"):
            clicked = ev8["selection"]["points"][0].get("label")
            if clicked:
                st.session_state.xf_rest_type = (
                    None if clicked == st.session_state.xf_rest_type else clicked
                )
                st.rerun()
    else:
        fig8b = px.bar(
            type_df.sort_values("avg_rating", ascending=True),
            x="avg_rating",
            y="restaurant_type",
            orientation="h",
            color="avg_rating",
            color_continuous_scale=["#F0B060", "#C94F24"],
            labels={"avg_rating": "Avg Rating", "restaurant_type": ""},
        )
        fig8b.update_coloraxes(showscale=False)
        base_layout(fig8b, "Restaurant Type Breakdown — Avg Rating", h=420)
        st.plotly_chart(fig8b, use_container_width=True, key="ch8b")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — Deep Dives
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-head">Deep Dives</div>', unsafe_allow_html=True)
c9, c10 = st.columns(2)

with c9:
    sc = df_xf[
        df_xf["approx_cost"].notna()
        & df_xf["rate"].notna()
        & df_xf["approx_cost"].between(50, 3000)
    ]
    if len(sc) > 3000:
        sc = sc.sample(3000, random_state=42)
    fig9 = px.scatter(
        sc,
        x="approx_cost",
        y="rate",
        color="online_order",
        color_discrete_map={"Yes": C["teal"], "No": C["primary"]},
        opacity=0.4,
        trendline="ols",
        trendline_scope="overall",
        trendline_color_override=C["slate"],
        labels={
            "approx_cost": "Cost for Two (₹)",
            "rate": "Rating",
            "online_order": "Online Order",
        },
        hover_data={"name": True} if "name" in sc.columns else {},
    )
    base_layout(fig9, "Cost vs Rating")
    st.plotly_chart(fig9, use_container_width=True, key="ch9")

with c10:
    vd = df_xf[
        df_xf["votes"].notna()
        & df_xf["rate"].notna()
        & (df_xf["votes"] > 0)
        & (df_xf["votes"] <= 10000)
    ]
    if len(vd) > 3000:
        vd = vd.sample(3000, random_state=7)
    fig10 = px.scatter(
        vd,
        x="votes",
        y="rate",
        color="rate",
        color_continuous_scale=["#F0B060", "#C94F24", "#7A2000"],
        opacity=0.4,
        labels={"votes": "Number of Votes", "rate": "Rating"},
        hover_data={"name": True} if "name" in vd.columns else {},
    )
    fig10.update_coloraxes(showscale=False)
    base_layout(fig10, "Votes vs Rating")
    st.plotly_chart(fig10, use_container_width=True, key="ch10")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<p style='text-align:center;color:{C['muted']};font-size:0.78rem;"
    f"font-family:DM Sans,sans-serif'>"
    "Built by Meet Modi · ZomatoBangalore Analytics · "
    "<a href='https://github.com/meet7364/ZomatoAnalytics' style='color:#C94F24;'>GitHub</a>"
    "</p>",
    unsafe_allow_html=True,
)
