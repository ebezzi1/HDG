"""
History Page — Chemical addition audit trail.

Features:
  - Searchable, filterable table of all logged operations
  - Concentration trend chart (plotly)
  - CSV export for quality audits
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from hdg_history import get_all_entries, get_entries_for_chart

st.header("📋 History — Chemical Audit Trail")

entries = get_all_entries()

if not entries:
    st.info(
        "No operations logged yet. Go to **Operations**, run a calculation, "
        "and press **Save** to create your first audit entry."
    )
    st.stop()

df = pd.DataFrame(entries)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# ── Filters ───────────────────────────────────────────────────────────────────
st.subheader("Filter")
f1, f2, f3 = st.columns(3)

with f1:
    search = st.text_input("Search notes", placeholder="e.g. post-weekend")

with f2:
    status_filter = st.multiselect(
        "Status", ["OK", "LOW", "HIGH"],
        default=["OK", "LOW", "HIGH"],
    )

with f3:
    date_range = st.date_input(
        "Date range",
        value=(df['timestamp'].min().date(), df['timestamp'].max().date()),
    )

# Apply filters
filtered = df.copy()

if status_filter:
    filtered = filtered[filtered['conc_status'].isin(status_filter)]

if search:
    filtered = filtered[
        filtered['operator_note'].str.contains(search, case=False, na=False)
    ]

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    filtered = filtered[
        (filtered['timestamp'].dt.date >= date_range[0]) &
        (filtered['timestamp'].dt.date <= date_range[1])
    ]

st.caption(f"Showing **{len(filtered)}** of **{len(df)}** entries")

# ── Table ─────────────────────────────────────────────────────────────────────
display = (
    filtered[['timestamp', 'conc_i', 'conc_souhaitee', 'conc_min', 'conc_max',
               'mass_adj', 'conc_status', 'operator_note']]
    .copy()
)
display['timestamp'] = display['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
display = display.rename(columns={
    'timestamp':      'Timestamp',
    'conc_i':         'Conc. Before (g/L)',
    'conc_souhaitee': 'Target (g/L)',
    'conc_min':       'Min (g/L)',
    'conc_max':       'Max (g/L)',
    'mass_adj':             'Addition mf (kg)',
    'conc_status':    'Status',
    'operator_note':  'Note',
})

st.dataframe(
    display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Conc. Before (g/L)": st.column_config.NumberColumn(format="%.1f"),
        "Target (g/L)":       st.column_config.NumberColumn(format="%.1f"),
        "Min (g/L)":          st.column_config.NumberColumn(format="%.1f"),
        "Max (g/L)":          st.column_config.NumberColumn(format="%.1f"),
        "Addition mf (kg)":   st.column_config.NumberColumn(format="%.2f"),
        "Status": st.column_config.TextColumn(width="small"),
    },
)

# ── Concentration Trend Chart ─────────────────────────────────────────────────
st.divider()
st.subheader("Concentration Trend")

chart_rows = get_entries_for_chart()

if len(chart_rows) >= 2:
    cdf = pd.DataFrame(chart_rows)
    cdf['timestamp'] = pd.to_datetime(cdf['timestamp'])

    # Use the most recent spec values for the reference lines
    conc_min_ref       = cdf['conc_min'].iloc[-1]
    conc_max_ref       = cdf['conc_max'].iloc[-1]
    conc_souhaitee_ref = cdf['conc_souhaitee'].iloc[-1]

    fig = go.Figure()

    # OK band (shaded green)
    fig.add_hrect(
        y0=conc_min_ref, y1=conc_max_ref,
        fillcolor="rgba(200, 230, 201, 0.35)",
        line_width=0,
        annotation_text="Acceptable range",
        annotation_position="top right",
        annotation_font_size=10,
        annotation_font_color="#388e3c",
    )

    # Concentration readings
    fig.add_trace(go.Scatter(
        x=cdf['timestamp'], y=cdf['conc_i'],
        mode='lines+markers',
        name='Concentration (g/L)',
        line=dict(color='#1565c0', width=2),
        marker=dict(size=7),
        hovertemplate='%{x|%Y-%m-%d %H:%M}<br>Conc: %{y:.1f} g/L<extra></extra>',
    ))

    # Addition events (non-zero mf)
    additions = cdf[cdf['mass_adj'] > 0]
    if not additions.empty:
        fig.add_trace(go.Scatter(
            x=additions['timestamp'], y=additions['conc_i'],
            mode='markers',
            name='Addition made',
            marker=dict(color='#e53935', size=11, symbol='triangle-up'),
            hovertemplate='%{x|%Y-%m-%d %H:%M}<br>Added: %{customdata:.2f} kg<extra></extra>',
            customdata=additions['mass_adj'],
        ))

    # Reference lines
    fig.add_hline(y=conc_souhaitee_ref, line_dash="dot", line_color="#1a73e8",
                  annotation_text=f"Target ({conc_souhaitee_ref:.1f} g/L)",
                  annotation_position="bottom right",
                  annotation_font_size=10)
    fig.add_hline(y=conc_min_ref, line_dash="dash", line_color="#e53935",
                  annotation_text=f"Min ({conc_min_ref:.1f} g/L)",
                  annotation_position="bottom left",
                  annotation_font_size=10)
    fig.add_hline(y=conc_max_ref, line_dash="dash", line_color="#e53935",
                  annotation_text=f"Max ({conc_max_ref:.1f} g/L)",
                  annotation_position="top left",
                  annotation_font_size=10)

    fig.update_layout(
        height=320,
        xaxis_title="Date",
        yaxis_title="Concentration (g/L)",
        legend=dict(orientation="h", y=1.12, x=0),
        margin=dict(l=20, r=100, t=30, b=40),
        hovermode="x unified",
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    fig.update_xaxes(showgrid=True, gridcolor="#eee")
    fig.update_yaxes(showgrid=True, gridcolor="#eee")

    st.plotly_chart(fig, use_container_width=True)
else:
    st.caption("Log at least 2 entries to display the concentration trend chart.")

# ── Export ────────────────────────────────────────────────────────────────────
st.divider()
st.subheader("Export")

csv_bytes = filtered.drop(columns=['id']).to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download filtered data as CSV",
    data=csv_bytes,
    file_name=f"hdg_history_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
    mime="text/csv",
)
st.caption("Exported file includes all visible columns for quality audit purposes.")
