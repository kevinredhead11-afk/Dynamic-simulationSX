"""
Pulsed-Flow Model for Nd/Dy Separation in Mixer-Settler Cascade
Based on Wichterlová & Rod (1999)
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class CascadeConfig:
    """Configuration for mixer-settler cascade"""
    n_extraction: int = 10
    n_scrub: int = 10
    n_strip: int = 5

    # Volumes (ml) - per stage
    V_total: float = 600.0
    V_mixer: float = 200.0
    V_settler_x: float = 200.0
    V_settler_y: float = 200.0

    # Equilibrium
    D_Nd: float = 0.0031
    D_Dy: float = 0.5959

    # Stage efficiency
    E: float = 0.95

    # Model parameters
    z: float = 1.0  # ideal mixers in settler
    phi_x: float = 0.2  # aqueous phase holdup

    # Time step (calculated from residence time)
    dt: float = 2.5  # minutes

    # Elements
    elements: List[str] = None

    def __post_init__(self):
        if self.elements is None:
            self.elements = ['Nd', 'Dy']
        self.n_stages = self.n_extraction + self.n_scrub + self.n_strip


class PulsedFlowCascade:
    """Pulsed-flow model for countercurrent mixer-settler cascade"""

    def __init__(self, config: CascadeConfig):
        self.config = config
        self.n_stages = config.n_stages
        self.n_elements = len(config.elements)

        # Distribution coefficients
        self.D = np.array([config.D_Nd, config.D_Dy])

        # Initialize concentration arrays [stages, elements]
        self.x_aqueous = np.zeros((self.n_stages, self.n_elements))  # aqueous conc (g/L)
        self.y_organic = np.zeros((self.n_stages, self.n_elements))   # organic conc (g/L)

        # Flowrates (ml/min) per section
        self.Qx_ext = 5.0
        self.Qx_scrub = 8.4  # 70% of 12
        self.Qx_strip = 12.0
        self.Qy = 32.5  # organic flowrate (all sections)

    def _get_volumes_section(self, section: str) -> Tuple[float, float]:
        """Get aqueous and organic volumes for a section"""
        V_x = self.config.V_settler_x
        V_y = self.config.V_settler_y

        # Mixer volumes proportional to flowrates
        if section == 'extraction':
            Qx_total = self.Qx_ext
        elif section == 'scrub':
            Qx_total = self.Qx_scrub
        else:  # strip
            Qx_total = self.Qx_strip

        Qy_total = self.Qy
        Qx_mixer = self.config.V_mixer * Qx_total / (Qx_total + Qy_total)
        Qy_mixer = self.config.V_mixer * Qy_total / (Qx_total + Qy_total)

        V_x_total = V_x + Qx_mixer
        V_y_total = V_y + Qy_mixer

        return V_x_total, V_y_total

    def _get_flowrates_section(self, section: str) -> Tuple[float, float]:
        """Get flowrates for a section"""
        if section == 'extraction':
            return self.Qx_ext, self.Qy
        elif section == 'scrub':
            return self.Qx_scrub, self.Qy
        else:  # strip
            return self.Qx_strip, self.Qy

    def _pulsed_flow_step(self, stage: int, x_out_prev: np.ndarray,
                         y_in_next: np.ndarray, section: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Single pulsed-flow step for one stage
        Returns: x_out (aqueous outlet), y_out (organic outlet)
        """
        Qx, Qy = self._get_flowrates_section(section)
        V_x, V_y = self._get_volumes_section(section)

        # Current concentrations in stage
        x_current = self.x_aqueous[stage].copy()
        y_current = self.y_organic[stage].copy()

        # Step 1: Pulsed flow in/out
        # Mixing (Eqs. 4a,b from paper)
        wx = V_x - 0.5 * Qx * self.config.dt
        wy = V_y - 0.5 * Qy * self.config.dt
        Wx = V_x + 0.5 * Qx * self.config.dt
        Wy = V_y + 0.5 * Qy * self.config.dt

        # Mixed concentrations
        x_tilde = (wx * x_current + 0.5 * Qx * self.config.dt * x_out_prev) / Wx
        y_tilde = (wy * y_current + 0.5 * Qy * self.config.dt * y_in_next) / Wy

        # Step 2: Mass transfer with efficiency (Eq. 7a,b)
        # Equilibrium concentrations (linear: m = D)
        x_star = (Wx * x_tilde + self.D * Wy * y_tilde) / (Wx + self.D * Wy)
        y_star = self.D * x_star

        # Model efficiency (Eq. 9 - simplified for linear case)
        E_model = self.config.E / (1.0 + (1.0 - self.config.E) *
                                   (wx * Qx * self.config.dt / (self.D * Wy * (Wx + self.D * Wy)) +
                                    wy * Qy * self.config.dt / (Wx * (Wx + self.D * Wy))))

        # Outlet concentrations
        x_out = (1.0 - E_model) * x_tilde + E_model * x_star
        y_out = (1.0 - E_model) * y_tilde + E_model * y_star

        return x_out, y_out

    def step_dynamic(self, dt: float = None):
        """
        One dynamic simulation step
        Cascade order: Strip (0-4) -> Scrub (5-14) -> Extraction (15-24)
        Countercurrent: organic flows up, aqueous flows down
        """
        if dt is not None:
            self.config.dt = dt

        # Temporary storage for new concentrations
        x_new = np.zeros_like(self.x_aqueous)
        y_new = np.zeros_like(self.y_organic)

        # Process from bottom to top (strip -> scrub -> extraction)
        # Stage numbering: 0-4 strip, 5-14 scrub, 15-24 extraction

        for stage in range(self.n_stages):
            if stage < self.config.n_strip:
                section = 'strip'
                stage_idx = stage
            elif stage < self.config.n_strip + self.config.n_scrub:
                section = 'scrub'
                stage_idx = stage - self.config.n_strip
            else:
                section = 'extraction'
                stage_idx = stage - self.config.n_strip - self.config.n_scrub

            # Inlet streams
            if stage == 0:
                # Bottom of strip: no inlet from below
                x_in = np.zeros(self.n_elements)
                y_in = self.y_organic[stage + 1] if stage < self.n_stages - 1 else np.zeros(self.n_elements)
            elif stage == self.n_stages - 1:
                # Top of extraction: feed inlet
                x_in = self.x_aqueous[stage - 1]
                y_in = np.zeros(self.n_elements)
            else:
                x_in = self.x_aqueous[stage - 1]
                y_in = self.y_organic[stage + 1] if stage < self.n_stages - 1 else np.zeros(self.n_elements)

            # Apply pulsed-flow
            x_out, y_out = self._pulsed_flow_step(stage, x_in, y_in, section)

            x_new[stage] = x_out
            y_new[stage] = y_out

        self.x_aqueous = x_new
        self.y_organic = y_new

    def set_initial_steady_state(self, x_init: np.ndarray, y_init: np.ndarray):
        """Set initial conditions from steady-state"""
        self.x_aqueous = x_init.copy()
        self.y_organic = y_init.copy()

    def set_flowrates(self, Qx_ext: float, Qx_scrub: float, Qx_strip: float, Qy: float):
        """Update flowrates"""
        self.Qx_ext = Qx_ext
        self.Qx_scrub = Qx_scrub
        self.Qx_strip = Qx_strip
        self.Qy = Qy

    def get_aqueous_profile(self) -> np.ndarray:
        """Return aqueous concentration profile"""
        return self.x_aqueous.copy()

    def get_organic_profile(self) -> np.ndarray:
        """Return organic concentration profile"""
        return self.y_organic.copy()

    def get_distribution_percent(self) -> np.ndarray:
        """Return % distribution in aqueous phase"""
        total = self.x_aqueous + self.y_organic * self.D[:, np.newaxis]
        # Avoid division by zero
        with np.errstate(divide='ignore', invalid='ignore'):
            pct = 100.0 * self.x_aqueous / total.T
            pct = np.where(total.T > 1e-10, pct, 0.0)
        return pct.T
