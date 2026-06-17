import html
import urllib.request

import pandas as pd
import plotly.graph_objects as go
import snowflake.connector
import streamlit as st

EXCLUDED_IPS = [
    '127.0.0.1',
    '84.38.212.333'
]

COLOR_TEXT_PRIMARY = '#f0f6fc'
COLOR_TEXT_SECONDARY = '#8b949e'
COLOR_BG_APP = '#0b0e14'
COLOR_BG_PANEL = '#222d3d'
COLOR_BORDER = '#30363d'
COLOR_BORDER_DARKER = '#21262d'
COLOR_WIN = '#1f8a33'
COLOR_DRAW = '#e5c93b'
COLOR_LOSS = '#ec3a37'
COLOR_CHART = '#1f6feb'
HEIGHT_TOP_IFRAME = 520
HEIGHT_STREAK_IFRAME = 280

DB_SCHEMA = 'PROD_GOLD'    #'PRZEMO_GOLD'

STREAK_STYLES = {
    'WIN': (COLOR_WIN, '🏆', 'rgba(46, 160, 67, 0.4)'),
    'DRAW': (COLOR_DRAW, '🤝', 'rgba(210, 153, 34, 0.4)'),
    'LOSS': (COLOR_LOSS, '<span style="position: relative; top: -5px;">⚠️</span>', 'rgba(248, 81, 73, 0.4)'),
}

st.set_page_config(
    page_title='Football Team Performance Dashboard',
    page_icon='⚽',
    layout='wide',
    initial_sidebar_state='collapsed',
)

PAGE_STYLE = f"""
<style>
    header, [data-testid="stHeader"] {{
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }}
    .block-container {{
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 2.0rem !important;
        padding-right: 2.0rem !important;
    }}
    .stApp {{
        background-color: {COLOR_BG_APP};
        color: {COLOR_TEXT_PRIMARY};
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    }}
    div[data-testid="stVerticalBlock"]:has(#panel-row-anchor) [data-testid="element-container"] {{
        margin: 0 !important;
        padding: 0 !important;
    }}
    div[data-testid="stVerticalBlock"]:has(#panel-row-anchor) [data-testid="element-container"]:has(#panel-row-anchor) {{
        height: 0 !important;
        min-height: 0 !important;
        overflow: hidden !important;
    }}
    div[data-testid="stVerticalBlock"]:has(#panel-row-anchor) iframe {{
        display: block;
        width: 100%;
        border: none;
    }}
    div[data-testid="stVerticalBlock"]:has(#panel-3-anchor) [data-testid="element-container"] {{
        margin: 0 !important;
        padding: 0 !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(.header-text-container) {{
        gap: 1rem !important;
        margin-bottom: 0px !important;
        align-items: flex-end !important;
    }}
    div[data-testid="stSelectbox"] label {{
        color: #ffffff !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        margin-bottom: 4px !important;
        padding: 0px !important;
    }}
    div[data-baseweb="select"] {{
        background-color: {COLOR_BG_PANEL} !important;
        border: 1px solid {COLOR_BORDER} !important;
        border-radius: 6px !important;
    }}
    div[data-baseweb="select"] div {{
        color: #000000 !important;
    }}
</style>
"""

IFRAME_STYLE = f"""
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; background: transparent; height: 100%; font-family: Arial, sans-serif !important;}}
.dashboard-panel {{
    background-color: {COLOR_BG_PANEL};
    border: 1px solid {COLOR_BORDER};
    border-radius: 12px;
    padding: 1.0rem;
    display: flex;
    flex-direction: column;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
}}
.card-header {{ font-size: 1.2rem; font-weight: 600; color: {COLOR_TEXT_PRIMARY}; margin-bottom: 2px; }}
.card-subheader {{ font-size: 1.00rem; color: {COLOR_TEXT_SECONDARY}; margin-bottom: 10px; }}
.top-panels-row {{
    display: grid;
    grid-template-columns: 33fr 67fr;
    gap: 10px;
    align-items: stretch;
    height: 100%;
}}
.top-panels-row > .dashboard-panel {{ min-height: 520px; }}
.form-row {{
    padding-top: 10px; display: flex; align-items: center;
    justify-content: flex-start; margin-top: 0;
}}
.form-row-label {{ color: {COLOR_TEXT_SECONDARY}; font-size: 1.0rem; font-weight: 600; }}
.custom-table {{ width: 100%; table-layout: fixed; border-collapse: collapse; font-size: 1.0rem; margin-bottom: 0; }}
.custom-table th {{
    color: {COLOR_TEXT_SECONDARY}; text-align: left; padding: 4px; font-weight: bold;
    border-bottom: 2px solid {COLOR_BORDER_DARKER};
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
.custom-table th:nth-child(1), .custom-table td:nth-child(1) {{ width: 20%; }}
.custom-table th:nth-child(2), .custom-table td:nth-child(2) {{ width: 45%; }}
.custom-table th:nth-child(3), .custom-table td:nth-child(3) {{ width: 20%; }}
.custom-table th:nth-child(4), .custom-table td:nth-child(4) {{ width: 15%; }}
.custom-table td {{
    padding: 3px 4px;
    border-bottom: 1px solid {COLOR_BORDER_DARKER};
    color: {COLOR_TEXT_PRIMARY};
    font-weight: 500;
    font-size: 1.0rem;
    line-height: 1.3;
    vertical-align: middle !important;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
.badge-win {{ background-color:{COLOR_WIN}; color:white; padding:3px 0px; border-radius:4px; font-weight:bold; font-size:1.0rem; display:inline-block; width:70px; text-align:center; line-height:1.4; }}
.badge-draw {{ background-color:{COLOR_DRAW}; color:white; padding:3px 0px; border-radius:4px; font-weight:bold; font-size:1.0rem; display:inline-block; width:70px; text-align:center; line-height:1.4; }}
.badge-loss {{ background-color:{COLOR_LOSS}; color:white; padding:3px 0px; border-radius:4px; font-weight:bold; font-size:1.0rem; display:inline-block; width:70px; text-align:center; line-height:1.4; }}
.dot {{
    height: 35px; width: 35px; border-radius: 50%; display: inline-flex;
    align-items: center; justify-content: center; font-weight: bold; font-size: 1.3rem; color: white;
}}
.dot-w {{ background-color: {COLOR_WIN}; }}
.dot-d {{ background-color: {COLOR_DRAW}; }}
.dot-l {{ background-color: {COLOR_LOSS}; }}
.chart-wrap {{ margin-top: auto; flex: 1; min-height: 0; }}
.chart-wrap .plotly-graph-div, .chart-wrap .js-plotly-plot {{ width: 100% !important; }}
.streak-layout {{ display: flex; gap: 15px; align-items: stretch; margin-top: -20px; }}
.streak-indicator {{
    flex: 0 0 32%; display: flex; align-items: center; gap: 24px;
    border-right: 1px solid {COLOR_BORDER_DARKER}; padding: 40px 20px 10px 160px; min-height: 140px;
}}
.streak-details {{ flex: 1; padding-top: 4px; min-width: 0; }}
.streak-cards {{ display: flex; gap: 12px; flex-wrap: nowrap; align-items: stretch; width: 100%; }}
.streak-card {{
    flex: 0 0 calc((100% - 48px) / 5);
    width: calc((100% - 48px) / 5);
    max-width: calc((100% - 48px) / 5);
    background-color: {COLOR_BG_APP}; border: 1px solid {COLOR_BORDER_DARKER}; border-radius: 8px;
    padding: 8px 6px; text-align: center;
}}
.streak-date {{ color: {COLOR_TEXT_SECONDARY}; font-size: 0.8rem; margin-bottom: 4px; }}
.streak-opponent {{
    font-weight: 600; font-size: 1.0rem; line-height: 1.3;
    white-space: normal; word-break: break-word; margin-bottom: 1px; color: {COLOR_TEXT_PRIMARY};
    min-height: 2.0em;
}}
.streak-score {{ font-size: 1.3rem; font-weight: bold; margin-bottom: 10px; color: {COLOR_TEXT_PRIMARY}; }}
.streak-details-label {{ color: {COLOR_TEXT_SECONDARY}; font-size: 1.00rem; margin-bottom: 5px; font-weight: 500; }}
"""

HEADER_HTML = f"""
<div class="header-text-container">
    <h2 style='margin: 0px; padding: 0px; font-weight: 700; font-size: 1.5rem; line-height: 1.1;'>⚽ Football Team Performance Dashboard</h2>
    <p style='color: {COLOR_TEXT_SECONDARY}; margin: 3px 0px 0px 0px; padding: 0px; font-size: 0.85rem;'>Real-time team performance insights powered by Snowflake & dbt</p>
</div>
"""


def iframe_page(body_html: str) -> str:
    return (
        f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<style>{IFRAME_STYLE}</style></head><body>{body_html}</body></html>"
    )


def result_badge(result: str) -> str:
    badge_class = {'WIN': 'badge-win', 'DRAW': 'badge-draw'}.get(result, 'badge-loss')
    return f'<span class="{badge_class}">{result}</span>'


def form_dot(result: str) -> str:
    dot_class, label = {'WIN': ('dot-w', 'W'), 'DRAW': ('dot-d', 'D')}.get(result, ('dot-l', 'L'))
    return f'<span class="dot {dot_class}">{label}</span>'


def build_table_rows(df_last_10: pd.DataFrame) -> str:
    return ''.join(
        f"<tr><td>{row['MATCH_AT_UTC']}</td><td>{row['OPPONENT']}</td>"
        f"<td>{result_badge(row['MATCH_RESULT'])}</td><td>{row['SCORE']}</td></tr>"
        for _, row in df_last_10.iterrows()
    )


def build_form_dots(df_last_10: pd.DataFrame) -> str:
    return ''.join(form_dot(res) for res in reversed(df_last_10['MATCH_RESULT'].tolist()))


def build_streak_card_html(match_row) -> str:
    m_date = html.escape(pd.to_datetime(match_row['MATCH_AT_UTC']).strftime('%b %d'))
    m_opponent = html.escape(str(match_row['OPPONENT']))
    m_score = html.escape(str(match_row['SCORE']))
    m_res = match_row['MATCH_RESULT']
    badge_class = {'WIN': 'badge-win', 'DRAW': 'badge-draw'}.get(m_res, 'badge-loss')
    return (
        f'<div class="streak-card">'
        f'<div class="streak-date">{m_date}</div>'
        f'<div class="streak-opponent" title="{m_opponent}">{m_opponent}</div>'
        f'<div class="streak-score">{m_score}</div>'
        f'<span class="{badge_class}">{html.escape(str(m_res))}</span>'
        f'</div>'
    )


def create_rolling_goals_figure(df_charts: pd.DataFrame) -> go.Figure:
    df_charts = df_charts.copy()
    df_charts['MATCH_DATE'] = pd.to_datetime(df_charts['MATCH_AT_UTC']).dt.strftime('%b %d')

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_charts['MATCH_DATE'], y=df_charts['AVG_GOALS_SCORED_PREVIOUS_5_MATCHES'],
        mode='lines+markers', name='Avg Goals Scored (Last 5)',
        line=dict(color=COLOR_CHART, width=3), marker=dict(size=11, color=COLOR_CHART),
    ))
    fig.add_trace(go.Scatter(
        x=df_charts['MATCH_DATE'], y=df_charts['AVG_GOALS_CONCEDED_PREVIOUS_5_MATCHES'],
        mode='lines+markers', name='Avg Goals Conceded (Last 5)',
        line=dict(color=COLOR_LOSS, width=3), marker=dict(size=11, color=COLOR_LOSS),
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
            font=dict(color=COLOR_TEXT_PRIMARY, size=12),
        ),
        margin=dict(l=50, r=20, t=10, b=50),
        height=430,
        autosize=True,
    )
    fig.update_xaxes(
        title={'text': 'Match Date', 'font': {'color': COLOR_TEXT_PRIMARY, 'size': 13}, 'standoff': 25},
        automargin=True,
        showgrid=True, gridcolor=COLOR_BORDER, tickfont=dict(color=COLOR_TEXT_SECONDARY, size=11),
    )
    fig.update_yaxes(
        title={'text': 'Goals', 'font': {'color': COLOR_TEXT_PRIMARY, 'size': 13}, 'standoff': 20},
        automargin=True,
        showgrid=True, gridcolor=COLOR_BORDER, tickfont=dict(color=COLOR_TEXT_SECONDARY, size=11),
        zeroline=False,
    )
    return fig


@st.cache_resource
def get_connection():
    return snowflake.connector.connect(
        account   = st.secrets['SNOWFLAKE_ACCOUNT'],
        user      = st.secrets['SNOWFLAKE_USER'],
        password  = st.secrets['SNOWFLAKE_PASSWORD'],
        warehouse = st.secrets['SNOWFLAKE_WAREHOUSE'],
        database  = st.secrets['SNOWFLAKE_DATABASE'],
        schema    = DB_SCHEMA,
    )


@st.cache_data(ttl=3600)
def run_query(sql: str) -> pd.DataFrame:
    cur = conn.cursor()
    try:
        cur.execute(sql)
        columns = [col[0] for col in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=columns)
    finally:
        cur.close()


def log_ip_to_bronze(ip_to_log: str, db_conn):
    cur = db_conn.cursor()  
    try:
        cur.execute(
            """
            INSERT INTO FOOTBALL_DB.BRONZE.USER_LOGINS (IP_ADDRESS, LOGIN_TIMESTAMP) 
            VALUES (%s, CONVERT_TIMEZONE('UTC', CURRENT_TIMESTAMP())::TIMESTAMP_NTZ)
            """,
            (ip_to_log,)
        )
    except Exception as e: 
        print(f"Error when insert to database: {e}")
    finally:
        cur.close()


user_ip = st.context.headers.get("X-Forwarded-For")

st.markdown(PAGE_STYLE, unsafe_allow_html=True)

conn = get_connection()

if user_ip  and  user_ip not in EXCLUDED_IPS:
    log_ip_to_bronze(user_ip, conn)

df_teams = run_query(f"""
    SELECT DISTINCT TEAM
    FROM FOOTBALL_DB.{DB_SCHEMA}.FCT_TEAM_ROLLING_FORM_LAST_5
    ORDER BY TEAM
""")

col_left, col_right = st.columns([4, 1])
with col_left:
    st.markdown(HEADER_HTML, unsafe_allow_html=True)
with col_right:
    selected_team = st.selectbox(
        'Select Team',
        df_teams['TEAM'] if not df_teams.empty else ['No Teams Found'],
        index=0,
    )

df_raw = run_query(f"""
    SELECT
        MATCH_AT_UTC,
        TEAM,
        OPPONENT,
        MATCH_RESULT,
        GOALS_FOR || ' - ' || GOALS_AGAINST as SCORE,
        AVG_GOALS_SCORED_PREVIOUS_5_MATCHES,
        AVG_GOALS_CONCEDED_PREVIOUS_5_MATCHES,
        CURRENT_STREAK_RESULT,
        CURRENT_STREAK_LENGTH
    FROM FOOTBALL_DB.{DB_SCHEMA}.FCT_TEAM_ROLLING_FORM_LAST_5
    WHERE TEAM = '{selected_team}'
    ORDER BY MATCH_AT_UTC DESC
""")

if df_raw.empty:
    st.warning(f"⚠️ No rolling metrics found in table 'FCT_TEAM_ROLLING_FORM_LAST_5' for this team.")
    st.stop()

df_charts = df_raw.iloc[::-1].copy()
df_last_10 = df_raw.head(10).copy()
df_last_10['MATCH_AT_UTC'] = pd.to_datetime(df_last_10['MATCH_AT_UTC']).dt.strftime('%Y-%m-%d')

panel_1_body = (
    '<div class="dashboard-panel" id="panel-1">'
    '<div class="card-header">📋 1. Recent Matches Form (Last 10 Matches)</div>'
    '<div class="card-subheader">Latest match results</div>'
    '<table class="custom-table">'
    '<thead><tr><th>Date</th><th>Opponent</th><th>Result</th><th>Score</th></tr></thead>'
    f'<tbody>{build_table_rows(df_last_10)}</tbody>'
    '</table>'
    '<div class="form-row">'
    '<span class="form-row-label">Form (Last 10)</span>'
    f'<div style="display:flex;gap:10px;margin-left:15px;">{build_form_dots(df_last_10)}</div>'
    '</div></div>'
)

chart_html = create_rolling_goals_figure(df_charts).to_html(
    full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False},
)
panel_2_body = (
    '<div class="dashboard-panel" id="panel-2">'
    '<div class="card-header">📈 2. Rolling Average Goals (Last 5 Matches)</div>'
    '<div class="card-subheader">Goals scored &amp; conceded (5-match rolling average)</div>'
    f'<div class="chart-wrap">{chart_html}</div>'
    '</div>'
)

st.markdown('<div id="panel-row-anchor" style="display:none"></div>', unsafe_allow_html=True)
st.iframe(iframe_page(f'<div class="top-panels-row">{panel_1_body}{panel_2_body}</div>'), height=HEIGHT_TOP_IFRAME)

latest_match = df_raw.iloc[0]
streak_len = int(latest_match['CURRENT_STREAK_LENGTH'])
streak_res = latest_match['CURRENT_STREAK_RESULT']
color_streak, icon_streak, border_color = STREAK_STYLES.get(streak_res, STREAK_STYLES['LOSS'])

streak_details_label = (
    f'Streak Details (Showing last 5 of {streak_len} {streak_res.lower()} matches)'
    if streak_len > 5 else 'Streak Details'
)
streak_cards_html = ''.join(
    build_streak_card_html(match_row)
    for _, match_row in df_raw.head(min(streak_len, 5)).iterrows()
)

panel_3_body = (
    '<div class="dashboard-panel" id="panel-3">'
    '<div class="card-header">⚡ 3. Current Streak</div>'
    '<div class="card-subheader">Current performance streak</div>'
    '<div class="streak-layout">'
    '<div class="streak-indicator">'
    f'<div style="display:inline-flex;justify-content:center;align-items:center;width:110px;height:110px;'
    f'border-radius:50%;border:3px solid {color_streak};box-shadow:0 0 12px {border_color};flex-shrink:0;">'
    f'<span style="font-size:3.2rem;">{icon_streak}</span></div>'
    '<div>'
    f'<div style="font-size:1.1rem;color:{COLOR_TEXT_SECONDARY};letter-spacing:0.9px;font-weight:600;">'
    'Current Streak</div>'
    f'<div style="font-size:1.8rem;font-weight:800;color:{color_streak};margin-top:2px;line-height:1.0em;">'
    f'{html.escape(str(streak_res))}</div>'
    f'<div style="font-size:1.2rem;color:{COLOR_TEXT_PRIMARY};font-weight:600;margin-top:4px;">{streak_len} matches</div>'
    '</div></div>'
    '<div class="streak-details">'
    f'<div class="streak-details-label">{html.escape(streak_details_label)}</div>'
    f'<div class="streak-cards">{streak_cards_html}</div>'
    '</div></div></div>'
)

st.markdown('<div id="panel-3-anchor" style="display:none"></div>', unsafe_allow_html=True)
st.iframe(iframe_page(panel_3_body), height=HEIGHT_STREAK_IFRAME)