# Hardware Environment & Peripherals

Hegemonikón's performance and UX are influenced by the client hardware used to access the Production Core (Debian Host). Standardizing and optimizing these peripherals is part of the "Zero Design" stability effort.

## 1. Verified Client Configuration

The following hardware has been verified as a stable RDP client for the Hegemonikón environment (Debian 13 Host).

- **Model**: iiyama STYLE-15FH112-N-UCFXB
- **Processor**: Intel Processor N100 (4 Cores / 4 Threads)
- **Memory**: 8GB - 16GB DDR4/DDR5
- **Display**: 15.6-inch Full HD (1920 x 1080) / Non-glare
- **Networking**: Wi-Fi 6E (supports high-speed, low-latency RDP over Tailscale)
- **OS**: Windows 11

## 2. Visual Optimization (DPI Scaling)

For the 15.6" Full HD form factor, standard 100% scaling makes text too small for extended development, while 125% scaling (DPI 120) can feel slightly cluttered.

- **Optimal Setting**: **DPI 118** (approx. 123% scaling).
- **Impact**: Provides a balance between readability and workspace area.
- **Implementation (Host-side)**:

  ```bash
  xfconf-query -c xsettings -p /Xft/DPI -s 118
  ```

## 3. Sub-monitor Selection Criteria (N100 Series)

When expanding the workspace for the iiyama STYLE-15FH112 series (or similar N100/Alder Lake-N laptops), consider the following constraints:

### 3.1. Connection Ports

- **Primary**: HDMI (Output). This is the most reliable path for external displays.
- **Secondary (USB-C)**: Note that basic N100 models often have "Data Only" USB-C ports. Verify **DisplayPort Alt Mode** support before purchasing a USB-C single-cable monitor. If not supported, a monitor with HDMI input is mandatory.

### 3.2. Resolution & Load

- **Recommended**: **1920 x 1080 (Full HD)** or **2560 x 1440 (WQHD)**.
- **Note on 4K**: While the N100 technically supports 4K@60Hz, driving a 4K display alongside a 1080p laptop screen can strain the Intel UHD Graphics during CPU-intensive AI workflows or high-refresh RDP sessions.
- **Scaling Symmetry**: Using a second 1080p monitor simplifies scaling, as both screens can share similar DPI settings (96 or 120).

### 3.3. Portability

- **Mobile Monitors**: 15.6" portable monitors (FHD) are a perfect match for the STYLE series, fitting into the same carry case and often powering via USB-A/C from the laptop (though a dedicated power brick is recommended for stability).

### 3.4. Recommended External Monitors (verified/benchmarked)

For the Intel N100 series (GPU-limited), the following configurations provide the best UX/performance ratio:

| Class | Recommendation | Why |
| :--- | :--- | :--- |
| **Standard** | **24" FHD (1920x1080) IPS** | Best balance. Sharp enough, low GPU load, matching aspect ratio. |
| **Productivity** | **34" WQHD Ultra-wide** | Allows side-by-side IDE and FileMaker. GPU load is higher but manageable for 2D. |
| **Tablet Hybrid** | **OPPO Pad 3 (Matte)** | Excellent for AI Chat/SNS sidecar (e.g., via O-Connect/Syncthing). |

*Avoid 4K monitors on N100 unless only using the external screen with the laptop lid closed.*

---

### Verification

- Hardware Profile Verified: 2026-02-04
- Optimal DPI for 15.6" FHD: 118 (User Feedback: "GOOD")
- GPU Performance (N100): Confirmed stable driving internal FHD + external FHD for development workloads.
