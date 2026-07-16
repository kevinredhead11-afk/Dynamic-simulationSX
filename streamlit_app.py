"""
Streamlit App: Nd/Dy Separation Dynamic Simulation
Pulsed-Flow Model with Interactive Flowrate Perturbations
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pulsed_flow_model import PulsedFlowCascade, CascadeConfig


@st.cache_resource
def init_cascade():
    """Initialize cascade configuration"""
    config = CascadeConfig(
        n_extraction=10,
        n_scrub=10,
        n_strip=5,
        D_Nd=0.0031,
        D_Dy=0.5959,
        E=0.95,
        elements=['Nd', 'Dy']
    )
    return PulsedFlowCascade(config)


def create_steady_state_profile():
    """Create approximate steady-state profile from paper data"""
    # Based on user's table data: Nd feed ~20.8, Dy feed ~2.68
    n_stages = 25
    x_ss = np.zeros((n_stages, 2))

    # Extraction stages: Nd high at bottom, decreases upward
    for i in range(10):
        x_ss[24-i, 0] = 20.8 - (i / 10) * 20.8 * 0.88  # Nd: decreases, 88% extracted
        x_ss[24-i, 1] = 0.0 + (i / 10) * 2.68 * 0.86    # Dy: increases, 86% extracted

    # Scrub stages: intermediate
    for i in range(10):
        x_ss[14+i, 0] = 20.8 * 0.5 - (i / 10) * 20.8 * 0.5
        x_ss[14+i, 1] = 2.68 * 0.5 + (i / 10) * 2.68 * 0.5

    # Strip stages: high concentration
    for i in range(5):
        x_ss[4-i, 0] = 20.8 * 0.7 - (i / 5) * 20.8 * 0.3
        x_ss[4-i, 1] = 2.68 * 0.7 + (i / 5) * 2.68 * 0.3

    y_ss = np.zeros((n_stages, 2))
    # Organic phase (inverse relationship)
    cascade_init = init_cascade()
    for i in range(n_stages):
        y_ss[i] = cascade_init.D * x_ss[i]

    return x_ss, y_ss


def simulate_with_perturbation(cascade, flowrates_schedule, total_time_min=120):
    """
    Simulate cascade with flowrate schedule
    flowrates_schedule: dict {time_min: {'Qx_ext': ..., 'Qy': ...}}
    """
    dt = cascade.config.dt
    n_steps = int(total_time_min / dt)

    # Initialize with steady-state
    x_ss, y_ss = create_steady_state_profile()
    cascade.set_initial_steady_state(x_ss, y_ss)

    # Current flowrates
    current_flows = {
        'Q_feed': 25.0,
        'Qx_ext': 25.0,
        'Qx_scrub': 8.4,
        'Qx_strip': 12.0,
        'Qy': 32.5
    }

    # Storage for time series
    time_array = np.arange(0, total_time_min, dt)
    x_profiles = np.zeros((len(time_array), cascade.n_stages, cascade.n_elements))
    y_profiles = np.zeros((len(time_array), cascade.n_stages, cascade.n_elements))

    # Run simulation
    for step, t in enumerate(time_array):
        # Check for flowrate changes
        for change_time in sorted(flowrates_schedule.keys()):
            if abs(t - change_time) < dt / 2:
                for key, val in flowrates_schedule[change_time].items():
                    current_flows[key] = val

        # Update cascade flowrates
        cascade.set_flowrates(
            current_flows['Q_feed'],
            current_flows['Qx_ext'],
            current_flows['Qx_scrub'],
            current_flows['Qx_strip'],
            current_flows['Qy']
        )

        # Simulate one step
        cascade.step_dynamic()

        # Store profiles
        x_profiles[step] = cascade.get_aqueous_profile()
        y_profiles[step] = cascade.get_organic_profile()

    return time_array, x_profiles, y_profiles


def plot_aqueous_distributions(x_profile, title_suffix=""):
    """Plot aqueous concentrations and % distribution"""
    n_stages = x_profile.shape[0]
    stages = np.arange(1, n_stages + 1)

    # Total concentration
    D = np.array([0.0031, 0.5959])
    y_profile = x_profile * D[:, np.newaxis]
    total = x_profile + y_profile

    # Percentage
    pct_nd = 100.0 * x_profile[:, 0] / np.where(total[:, 0] > 1e-6, total[:, 0], 1e-6)
    pct_dy = 100.0 * x_profile[:, 1] / np.where(total[:, 1] > 1e-6, total[:, 1], 1e-6)

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(f"Aqueous Distributions — Absolute {title_suffix}",
                        f"Aqueous Distributions — % of Total {title_suffix}"),
        specs=[[{'secondary_y': False}, {'secondary_y': False}]]
    )

    # Absolute
    fig.add_trace(
        go.Scatter(x=stages, y=x_profile[:, 0], mode='lines+markers',
                  name='Nd', line=dict(color='blue', width=2),
                  marker=dict(size=4)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=stages, y=x_profile[:, 1], mode='lines+markers',
                  name='Dy', line=dict(color='orange', width=2),
                  marker=dict(size=4)),
        row=1, col=1
    )

    # Percentage
    fig.add_trace(
        go.Scatter(x=stages, y=pct_nd, mode='lines+markers',
                  name='Nd%', line=dict(color='blue', width=2, dash='dash'),
                  marker=dict(size=4), showlegend=False),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=stages, y=pct_dy, mode='lines+markers',
                  name='Dy%', line=dict(color='orange', width=2, dash='dash'),
                  marker=dict(size=4), showlegend=False),
        row=1, col=2
    )

    fig.update_xaxes(title_text="Stage", row=1, col=1)
    fig.update_xaxes(title_text="Stage", row=1, col=2)
    fig.update_yaxes(title_text="Concentration (g/L)", row=1, col=1)
    fig.update_yaxes(title_text="Distribution (%)", row=1, col=2)

    fig.update_layout(height=500, hovermode='x unified', showlegend=True)

    return fig


# ============================================================================
# STREAMLIT APP
# ============================================================================

st.set_page_config(layout="wide", page_title="Nd/Dy Extraction Simulator")

st.title("🧪 Nd/Dy Separation - Pulsed-Flow Dynamic Simulator")
st.markdown("""
Based on **Wichterlová & Rod (1999)** — Dynamic behaviour of mixer-settler cascade.
Simulate how flowrate perturbations affect separation profiles in real-time.
""")

# Initialize cascade
cascade = init_cascade()

# ============================================================================
# SIDEBAR: Configuration
# ============================================================================

st.sidebar.header("⚙️ Configuration")
st.sidebar.markdown("### Cascade Parameters (Fixed)")
st.sidebar.info("""
- **Extraction stages:** 10
- **Scrub stages:** 10
- **Strip stages:** 5
- **D_Nd:** 0.0031 | D_Dy:** 0.5959
- **Stage efficiency (E):** 0.95
- **Holdup (φ_x):** 0.2
- **Volume/stage:** 600 ml
""")

# ============================================================================
# MAIN: Input Columns
# ============================================================================

st.markdown("---")
st.markdown("### 📊 Simulation Setup")

col1, col2, col3 = st.columns([1, 1, 1.2])

with col1:
    st.subheader("**Initial Flowrates**")
    st.markdown("(Baseline - Steady State)")

    Q_feed_1 = st.number_input(
        "Feed Aqueous (ml/min)",
        value=25.0, min_value=1.0, max_value=50.0, step=0.5,
        key="Q_feed_1"
    )

    Qx_strip_1 = st.number_input(
        "Strip Aqueous (ml/min)",
        value=12.0, min_value=0.1, max_value=30.0, step=0.5,
        key="Qx_strip_1"
    )

    Qy_1 = st.number_input(
        "Organic (ml/min) [all]",
        value=32.5, min_value=1.0, max_value=50.0, step=0.5,
        key="Qy_1"
    )

    st.info(f"**Scrub Aqueous:** {0.7 * Qx_strip_1:.2f} (70% of Strip)")
    st.info(f"**Extraction Aqueous:** {Q_feed_1:.2f} (Feed)")

with col2:
    st.subheader("**Perturbed Flowrates**")
    st.markdown("(New values - after t=10 min)")

    Q_feed_2 = st.number_input(
        "Feed Aqueous (ml/min)",
        value=25.0, min_value=1.0, max_value=50.0, step=0.5,
        key="Q_feed_2"
    )

    Qx_strip_2 = st.number_input(
        "Strip Aqueous (ml/min)",
        value=12.0, min_value=0.1, max_value=30.0, step=0.5,
        key="Qx_strip_2"
    )

    Qy_2 = st.number_input(
        "Organic (ml/min) [all]",
        value=32.5, min_value=1.0, max_value=50.0, step=0.5,
        key="Qy_2"
    )

    st.info(f"**Scrub Aqueous:** {0.7 * Qx_strip_2:.2f} (70% of Strip)")
    st.info(f"**Extraction Aqueous:** {Q_feed_2:.2f} (Feed)")

with col3:
    st.subheader("**Simulation Parameters**")

    t_pert = st.number_input(
        "Perturbation time (min)",
        value=10, min_value=1, max_value=50, step=1,
        help="When to apply new flowrates"
    )

    t_total = st.number_input(
        "Total simulation time (min)",
        value=120, min_value=30, max_value=300, step=10,
        help="How long to simulate after perturbation"
    )

    st.markdown("---")

    if st.button("▶️ RUN SIMULATION", use_container_width=True):
        st.session_state.run_simulation = True
    else:
        st.session_state.run_simulation = False

# ============================================================================
# SIMULATION
# ============================================================================

if st.session_state.run_simulation:
    st.markdown("---")
    st.markdown("### 📈 Simulation Results")

    with st.spinner("⏳ Running dynamic simulation..."):
        # Define flowrate schedule
        flowrates_schedule = {
            0.0: {
                'Q_feed': Q_feed_1,
                'Qx_ext': Q_feed_1,
                'Qx_scrub': 0.7 * Qx_strip_1,
                'Qx_strip': Qx_strip_1,
                'Qy': Qy_1
            },
            t_pert: {  # Perturbation point
                'Q_feed': Q_feed_2,
                'Qx_ext': Q_feed_2,
                'Qx_scrub': 0.7 * Qx_strip_2,
                'Qx_strip': Qx_strip_2,
                'Qy': Qy_2
            }
        }

        # Run simulation
        time_array, x_profiles, y_profiles = simulate_with_perturbation(
            cascade, flowrates_schedule, total_time_min=t_total
        )

    # Display results
    col_plot1, col_plot2 = st.columns(2)

    # Create frames for animation at key times
    key_times = [0, int(t_pert/cascade.config.dt), -1]  # start, perturb, end

    with col_plot1:
        st.markdown("#### 🔵 **Initial Steady-State** (t=0 min)")
        fig_init = plot_aqueous_distributions(x_profiles[0], "t=0 min")
        st.plotly_chart(fig_init, use_container_width=True)

    with col_plot2:
        st.markdown(f"#### 🟡 **After Perturbation** (t≈{t_total} min)")
        fig_final = plot_aqueous_distributions(x_profiles[-1], f"t={t_total} min")
        st.plotly_chart(fig_final, use_container_width=True)

    # Intermediate snapshots
    st.markdown("---")
    st.markdown("#### 📊 **Time Evolution Snapshots**")

    n_snapshots = min(5, len(x_profiles))
    snapshot_indices = np.linspace(0, len(x_profiles)-1, n_snapshots, dtype=int)

    cols_snap = st.columns(n_snapshots)
    for idx, col in zip(snapshot_indices, cols_snap):
        t_snap = time_array[idx]
        with col:
            st.markdown(f"**t = {t_snap:.1f} min**")
            x_snap = x_profiles[idx]
            n_stages = x_snap.shape[0]
            stages = np.arange(1, n_stages + 1)

            fig_mini = go.Figure()
            fig_mini.add_trace(go.Scatter(x=stages, y=x_snap[:, 0], name='Nd', line=dict(color='blue')))
            fig_mini.add_trace(go.Scatter(x=stages, y=x_snap[:, 1], name='Dy', line=dict(color='orange')))
            fig_mini.update_layout(height=300, showlegend=True, hovermode='x')
            fig_mini.update_xaxes(title="Stage")
            fig_mini.update_yaxes(title="Conc (g/L)")

            st.plotly_chart(fig_mini, use_container_width=True)

    # Summary metrics
    st.markdown("---")
    st.markdown("#### 📋 **Summary Metrics**")

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    # Initial SS
    x_init = x_profiles[0]
    # Final SS
    x_final = x_profiles[-1]

    with metric_col1:
        nd_init = x_init[:, 0].sum()
        st.metric("Nd (Ext)", f"{nd_init:.1f} g/L", "Initial Cascade")

    with metric_col2:
        dy_init = x_init[:, 1].sum()
        st.metric("Dy (Ext)", f"{dy_init:.1f} g/L", "Initial Cascade")

    with metric_col3:
        nd_final = x_final[:, 0].sum()
        delta_nd = nd_final - nd_init
        st.metric("Nd (Ext)", f"{nd_final:.1f} g/L", f"{delta_nd:+.1f} g/L", delta_color="inverse")

    with metric_col4:
        dy_final = x_final[:, 1].sum()
        delta_dy = dy_final - dy_init
        st.metric("Dy (Ext)", f"{dy_final:.1f} g/L", f"{delta_dy:+.1f} g/L", delta_color="inverse")

else:
    st.info("👈 **Set flowrates and click 'RUN SIMULATION' to start**")
