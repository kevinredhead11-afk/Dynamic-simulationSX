# Nd/Dy Separation — Pulsed-Flow Dynamic Simulator

Interactive simulation of rare earth element (Nd/Dy) separation using mixer-settler cascades with the pulsed-flow model from **Wichterlová & Rod (1999)**.

## Features

- **Pulsed-Flow Model**: Discretized simulation of continuous extraction in countercurrent cascades
- **Dynamic Perturbations**: Apply flowrate changes and observe transient behavior
- **Interactive Dashboard**: Real-time visualization with Streamlit
- **Real-time Profiles**: Watch how concentration profiles evolve as system reaches new steady-state

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit app:

```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

### Quick Start

1. **Initial Flowrates** (left column): Set baseline flowrates for extraction, scrub, and strip sections
2. **Perturbed Flowrates** (center column): Define new flowrates to apply at t=10 min
3. **Simulation Parameters** (right column): Set perturbation time and total simulation duration
4. **Click "RUN SIMULATION"**: Watch the cascade respond to the disturbance

## Model Details

### Cascade Topology

```
Feed (Nd/Dy) → Extraction (10 stages) 
            ↓
           Scrub (10 stages) ← Reflux (70% of strip acuoso)
            ↓
            Strip (5 stages)
            ↓
        (Products)
```

### Key Parameters

| Parameter | Value | Note |
|-----------|-------|------|
| **D_Nd** | 0.0031 | Distribution coefficient |
| **D_Dy** | 0.5959 | Distribution coefficient |
| **β_Dy,Nd** | ~192 | Separation factor |
| **E** | 0.95 | Stage efficiency |
| **φ_x** | 0.2 | Aqueous phase holdup |
| **Volume/stage** | 600 ml | 1/3 mixer, 2/3 settler |

### Pulsed-Flow Model Algorithm

Each stage discretizes continuous extraction as:

1. **Pulsed flow**: Small volumes `Q·Δt` enter/exit mixer
2. **Mixing**: Inlet pulse mixes with stage holdup
3. **Batch mass transfer**: Approach to equilibrium with efficiency `E`

See `pulsed_flow_model.py` for implementation.

## References

- **Wichterlová, J., & Rod, V. (1999)**  
  "Dynamic behaviour of the mixer-settler cascade. Extractive separation of the rare earths"  
  *Journal of Chemical Engineering Sciences*, 54(16), 4041-4051

## Files

- `pulsed_flow_model.py`: Core pulsed-flow model and cascade simulation
- `app.py`: Streamlit web interface
- `requirements.txt`: Python dependencies
- `README.md`: This file

## Author

Generated as part of Dynamic Simulation project for Nd/Dy extraction modeling.
