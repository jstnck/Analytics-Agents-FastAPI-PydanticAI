import marimo

__generated_with = "0.19.2"
app = marimo.App(width="medium", css_file="custom.css")


@app.cell
def _():
    import marimo as mo
    import duckdb
    import httpx
    import polars as pl
    return duckdb, httpx, mo, pl


@app.cell
def _(mo):
    logo_html = """
    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem;">
        <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 64px; height: 64px;">
          <path d="M15 65 Q10 58 14 50 Q20 42 32 38 Q48 34 62 40 Q76 46 80 58 Q83 68 76 76 Q66 84 48 85 Q28 86 18 78 Q12 72 15 65" fill="hsl(145, 20%, 80%)" stroke="hsl(25, 30%, 20%)" stroke-width="0.6"/>
          <path d="M60 52 Q66 56 70 66 Q72 76 64 80 Q58 74 58 64 Q58 56 60 52" fill="hsl(30, 20%, 35%)" stroke="none" opacity="0.6"/>
          <g stroke="hsl(25, 30%, 20%)" stroke-linecap="round" fill="none">
            <path d="M24 54 Q36 49 54 54" stroke-width="0.4" opacity="0.7"/>
            <path d="M22 58 Q38 52 58 58" stroke-width="0.35" opacity="0.6"/>
            <path d="M20 63 Q40 56 60 62" stroke-width="0.35" opacity="0.55"/>
            <path d="M22 68 Q42 62 58 66" stroke-width="0.3" opacity="0.5"/>
            <path d="M26 72 Q44 67 54 70" stroke-width="0.3" opacity="0.45"/>
          </g>
          <path d="M32 62 L46 59 L48 64 L34 67 Z" fill="hsl(152, 45%, 25%)" opacity="0.35" stroke="hsl(25, 30%, 20%)" stroke-width="0.2"/>
          <path d="M62 48 Q66 42 68 34" stroke="hsl(25, 30%, 20%)" stroke-width="0.5" fill="none"/>
          <path d="M58 46 Q64 48 68 46" stroke="hsl(40, 25%, 92%)" stroke-width="2" stroke-linecap="round" fill="none"/>
          <path d="M64 38 Q62 30 66 22 Q72 14 82 16 Q92 20 92 32 Q90 44 78 48 Q68 50 64 44 Q62 42 64 38" fill="hsl(152, 45%, 25%)" stroke="hsl(25, 30%, 20%)" stroke-width="0.5"/>
          <path d="M88 28 Q92 26 96 28 Q99 30 98 34 Q96 38 92 38 Q88 38 86 36 Q84 34 86 30 Q87 28 88 28" fill="hsl(35, 85%, 55%)" stroke="hsl(25, 30%, 20%)" stroke-width="0.5"/>
          <ellipse cx="80" cy="28" rx="2.5" ry="3" fill="hsl(25, 30%, 20%)"/>
          <ellipse cx="80" cy="28" rx="1.6" ry="2" fill="hsl(25, 25%, 10%)"/>
          <circle cx="79.2" cy="27" r="0.6" fill="hsl(40, 25%, 92%)"/>
          <path d="M12 70 Q8 68 8 62 Q10 58 14 60" stroke="hsl(25, 30%, 20%)" stroke-width="0.6" stroke-linecap="round" fill="none"/>
        </svg>
        <div>
            <h1 style="margin: 0; font-family: 'DM Serif Display', serif; color: hsl(152, 45%, 25%);">NBA Analytics</h1>
            <p style="margin: 0.25rem 0 0 0; color: hsl(150, 15%, 40%); font-family: 'Inter', sans-serif;">Explore NBA data using direct SQL queries and AI-powered analysis.</p>
        </div>
    </div>
    """
    mo.Html(logo_html)
    return


@app.cell
def _(duckdb):
    # Connect to DuckDB database (read-only)
    db_path = "/app/data/analytics.duckdb"
    conn = duckdb.connect(db_path, read_only=True)
    return (conn,)


@app.cell
def _(mo):
    mo.md("""
    ## Available Tables

    - **dmt.dmt_schedule** - Game schedule with dates, teams
    - **dmt.dmt_team_per_game_stats** - Team offensive statistics per game
    - **dmt.dmt_opponent_per_game_stats** - Opponent statistics (defensive)
    - **dmt.dmt_team_differential** - Team performance differentials
    - **dmt.dmt_feature_win_predict** - Win prediction features
    - **dmt.dmt_ml_win_predictions** - ML model predictions
    - **dmt.dmt_cities** - City reference data
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Direct SQL Query
    """)
    return


@app.cell
def _(mo):
    # SQL query input
    sql_query = mo.ui.text_area(
        value="SELECT team_name, games_played, points_per_game FROM dmt.dmt_team_per_game_stats ORDER BY points_per_game DESC LIMIT 10",
        label="SQL Query",
        full_width=True,
        rows=4
    )

    run_query_btn = mo.ui.button(label="Run Query")

    mo.vstack([sql_query, run_query_btn])
    return run_query_btn, sql_query


@app.cell
def _(conn, mo, pl, run_query_btn, sql_query):
    # Execute query when button is clicked
    query_result = None
    error = None

    if run_query_btn.value and sql_query.value:
        try:
            # Use arrow() to get Arrow table, then convert to Polars
            query_result = pl.from_arrow(conn.execute(sql_query.value).arrow())
            mo.md(f"**Query returned {len(query_result)} rows**")
        except Exception as e:
            error = str(e)
            mo.md(f"**Error:** {error}")
    return (query_result,)


@app.cell
def _(mo, query_result):
    # Display results
    if query_result is not None:
        mo.ui.table(query_result, selection=None)
    return


@app.cell
def _(mo):
    mo.md("---")
    mo.md("## Ask the AI Agent")
    return


@app.cell
def _(mo):
    # AI Agent query input
    agent_query = mo.ui.text_area(
        placeholder="Ask a question about NBA data (e.g., 'Which team has the highest points per game?')",
        label="Your Question",
        full_width=True,
        rows=3
    )

    ask_agent_btn = mo.ui.button(label="Ask Agent")

    mo.vstack([agent_query, ask_agent_btn])
    return agent_query, ask_agent_btn


@app.cell
async def _(agent_query, ask_agent_btn, httpx, mo):
    # Call FastAPI agent endpoint
    agent_response = None
    agent_error = None

    if ask_agent_btn.value and agent_query.value:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://backend:8000/api/v1/chat",
                    json={"message": agent_query.value},
                    timeout=60.0
                )
                if response.status_code == 200:
                    agent_response = response.json()
                    mo.md(f"**Agent Response:**\n\n{agent_response.get('message', 'No response')}")
                else:
                    agent_error = f"API returned status {response.status_code}"
                    mo.md(f"**Error:** {agent_error}")
        except Exception as e:
            agent_error = str(e)
            mo.md(f"**Error:** {agent_error}")
    return


@app.cell
def _(mo):
    mo.md("""
    ---
    """)
    return


if __name__ == "__main__":
    app.run()
