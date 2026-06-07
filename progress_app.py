import streamlit as st
from datetime import datetime, timezone, timedelta
import time

# ── Config ──────────────────────────────────────────────────────────────────
START_DT = datetime(2026, 6, 5, 17, 0, 0,
                    tzinfo=timezone(timedelta(hours=5, minutes=30)))  # 5 PM IST
DURATION  = timedelta(days=30)
END_DT    = START_DT + DURATION

st.set_page_config(page_title="30-Day Progress", page_icon="⏳", layout="centered")

# ── Styles ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .main-card {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    border-radius: 24px;
    padding: 48px 40px 40px;
    text-align: center;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    margin-top: 20px;
  }
  .title {
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #a78bfa;
    margin-bottom: 4px;
  }
  .big-pct {
    font-size: 5.5rem;
    font-weight: 900;
    line-height: 1;
    background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 16px 0 8px;
  }
  .pct-label {
    font-size: 1.1rem;
    color: #94a3b8;
    margin-bottom: 32px;
    letter-spacing: 0.05em;
  }

  /* Progress bar track */
  .bar-track {
    background: rgba(255,255,255,0.08);
    border-radius: 999px;
    height: 22px;
    width: 100%;
    overflow: hidden;
    margin-bottom: 32px;
    box-shadow: inset 0 2px 6px rgba(0,0,0,0.4);
  }
  .bar-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #7c3aed, #3b82f6, #10b981);
    transition: width 0.4s ease;
    box-shadow: 0 0 14px rgba(124,58,237,0.6);
  }

  /* Stats row */
  .stats-row {
    display: flex;
    justify-content: space-between;
    gap: 16px;
    margin-top: 8px;
  }
  .stat-box {
    flex: 1;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 16px 12px;
  }
  .stat-label {
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 6px;
  }
  .stat-value {
    font-size: 1rem;
    font-weight: 700;
    color: #e2e8f0;
  }
  .stat-sub {
    font-size: 0.75rem;
    color: #94a3b8;
    margin-top: 2px;
  }

  .done-banner {
    font-size: 2rem;
    font-weight: 800;
    color: #34d399;
    margin-bottom: 8px;
  }
  .not-started {
    font-size: 1.1rem;
    color: #f59e0b;
    margin-bottom: 8px;
  }
</style>
""", unsafe_allow_html=True)


def fmt_duration(td: timedelta) -> tuple[str, str]:
    """Returns (value_str, unit_str) for the remaining/elapsed display."""
    total_secs = int(abs(td.total_seconds()))
    days    = total_secs // 86400
    hours   = (total_secs % 86400) // 3600
    minutes = (total_secs % 3600)  // 60
    secs    = total_secs % 60
    return f"{days}d {hours:02d}h {minutes:02d}m {secs:02d}s", ""


def render():
    now     = datetime.now(tz=timezone.utc).astimezone(timezone(timedelta(hours=5, minutes=30)))
    elapsed = now - START_DT
    total   = DURATION

    if now < START_DT:
        # Not started yet
        time_to_start, _ = fmt_duration(START_DT - now)
        pct = 0.0
        status = "not_started"
    elif now >= END_DT:
        pct = 100.0
        status = "done"
        elapsed = DURATION
    else:
        pct = min((elapsed.total_seconds() / total.total_seconds()) * 100, 100.0)
        status = "running"

    elapsed_str, _ = fmt_duration(elapsed if status != "not_started" else timedelta(0))
    remaining_td   = max(END_DT - now, timedelta(0))
    remaining_str, _ = fmt_duration(remaining_td)

    # ── Card ─────────────────────────────────────────────────────────────────
    bar_width = min(pct, 100.0)

    if status == "not_started":
        big_display = f"""
          <div class="not-started">⏳ Countdown to start</div>
          <div style="font-size:1.4rem;font-weight:700;color:#f59e0b;">{time_to_start}</div>
        """
        pct_display = ""
    elif status == "done":
        big_display = '<div class="done-banner">🎉 100.000% Complete!</div>'
        pct_display = ""
    else:
        big_display = f'<div class="big-pct">{pct:.4f}%</div>'
        pct_display = '<div class="pct-label">of 30-day goal</div>'

    # Elapsed days/hours for stat
    el_secs = elapsed.total_seconds()
    el_days = el_secs / 86400

    html = f"""
    <div class="main-card">
      <div class="title">⏱ 30-Day Progress Tracker</div>
      {big_display}
      {pct_display}

      <div class="bar-track">
        <div class="bar-fill" style="width:{bar_width:.4f}%"></div>
      </div>

      <div class="stats-row">
        <div class="stat-box">
          <div class="stat-label">Elapsed</div>
          <div class="stat-value">{el_days:.4f} days</div>
          <div class="stat-sub">{elapsed_str}</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">Remaining</div>
          <div class="stat-value">{(30 - el_days):.4f} days</div>
          <div class="stat-sub">{remaining_str}</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">Progress</div>
          <div class="stat-value">{pct:.4f}%</div>
          <div class="stat-sub">of 30 days</div>
        </div>
      </div>

      <div style="margin-top:24px;font-size:0.72rem;color:#475569;letter-spacing:0.05em;">
        Started: 5 Jun 2026, 5:00 PM IST &nbsp;·&nbsp; Ends: 5 Jul 2026, 5:00 PM IST
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    return status


status = render()

# Auto-refresh every second while running
if status == "running":
    time.sleep(1)
    st.rerun()
elif status == "not_started":
    time.sleep(1)
    st.rerun()
