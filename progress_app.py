import streamlit as st
from datetime import datetime, timezone, timedelta, date, time as dtime
import time
import json
import os

# ── Config ──────────────────────────────────────────────────────────────────
IST = timezone(timedelta(hours=5, minutes=30))
DEFAULT_START_DT = datetime(2026, 6, 12, 22, 0, 0, tzinfo=IST)  # 10 PM IST
DURATION = timedelta(days=30)
STATE_FILE = os.path.join(os.path.dirname(__file__), ".progress_state.json")


def load_start_dt() -> datetime:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                data = json.load(f)
            ts = data.get("start_ts")
            if ts:
                return datetime.fromtimestamp(ts, tz=IST)
        except Exception:
            pass
    return DEFAULT_START_DT


def save_start_dt(dt: datetime):
    with open(STATE_FILE, "w") as f:
        json.dump({"start_ts": dt.timestamp()}, f)


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


def fmt_duration(td: timedelta) -> str:
    total_secs = int(abs(td.total_seconds()))
    days    = total_secs // 86400
    hours   = (total_secs % 86400) // 3600
    minutes = (total_secs % 3600)  // 60
    secs    = total_secs % 60
    return f"{days}d {hours:02d}h {minutes:02d}m {secs:02d}s"


def render(start_dt: datetime):
    end_dt  = start_dt + DURATION
    now     = datetime.now(tz=IST)
    elapsed = now - start_dt

    if now < start_dt:
        time_to_start = fmt_duration(start_dt - now)
        pct = 0.0
        status = "not_started"
    elif now >= end_dt:
        pct = 100.0
        status = "done"
        elapsed = DURATION
    else:
        pct = min((elapsed.total_seconds() / DURATION.total_seconds()) * 100, 100.0)
        status = "running"

    elapsed_str   = fmt_duration(elapsed if status != "not_started" else timedelta(0))
    remaining_td  = max(end_dt - now, timedelta(0))
    remaining_str = fmt_duration(remaining_td)
    bar_width     = min(pct, 100.0)

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
        big_display = f'<div class="big-pct">{pct:.3f}%</div>'
        pct_display = '<div class="pct-label">of 30-day goal</div>'

    el_days       = elapsed.total_seconds() / 86400
    started_label = start_dt.strftime("%-d %b %Y, %-I:%M %p IST")
    ended_label   = end_dt.strftime("%-d %b %Y, %-I:%M %p IST")

    html = f"""
    <div class="main-card">
      <div class="title">⏱ 30-Day Progress Tracker</div>
      {big_display}
      {pct_display}

      <div class="bar-track">
        <div class="bar-fill" style="width:{bar_width:.3f}%"></div>
      </div>

      <div class="stats-row">
        <div class="stat-box">
          <div class="stat-label">Elapsed</div>
          <div class="stat-value">{el_days:.3f} days</div>
          <div class="stat-sub">{elapsed_str}</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">Remaining</div>
          <div class="stat-value">{max(30 - el_days, 0):.3f} days</div>
          <div class="stat-sub">{remaining_str}</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">Progress</div>
          <div class="stat-value">{pct:.3f}%</div>
          <div class="stat-sub">of 30 days</div>
        </div>
      </div>

      <div style="margin-top:24px;font-size:0.72rem;color:#475569;letter-spacing:0.05em;">
        Started: {started_label} &nbsp;·&nbsp; Ends: {ended_label}
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    return status


# ── Main ─────────────────────────────────────────────────────────────────────
start_dt = load_start_dt()
status = render(start_dt)

# ── Start time picker ─────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("⚙️ Set custom start date & time (IST)"):
    col1, col2 = st.columns(2)
    with col1:
        picked_date = st.date_input("Start date", value=start_dt.date())
    with col2:
        picked_time = st.time_input("Start time (IST)", value=start_dt.time())

    if st.button("✅ Apply", type="primary"):
        new_start = datetime(
            picked_date.year, picked_date.month, picked_date.day,
            picked_time.hour, picked_time.minute, 0,
            tzinfo=IST,
        )
        save_start_dt(new_start)
        st.rerun()

# Auto-refresh every second while active
if status in ("running", "not_started"):
    time.sleep(1)
    st.rerun()
