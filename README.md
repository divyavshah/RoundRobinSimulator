# 🌀 Round Robin Scheduling Simulator

This project is a fully interactive, GUI-based **Round Robin CPU Scheduling Simulator** built using Python and Tkinter. It visually demonstrates how the Round Robin algorithm works in real-time, making it ideal for learning, teaching, and presenting operating system concepts.

## 🎯 Key Features

- ✅ **Real-Time Gantt Chart Animation**  
  Watch how processes execute in cycles based on the time quantum with dynamic, color-coded blocks.

- 📋 **Dynamic Timeline Logging**  
  Logs process arrival, execution, re-queuing, and completion with timestamps.

- 🧠 **Automatic Statistics Calculation**  
  Displays turnaround time, waiting time, completion time, and averages in a clean summary panel.

- 📊 **Time Usage Visualization**  
  A separate graph shows how much CPU time each process received and when.

- 🕹️ **Speed Control Slider**  
  Adjust animation speed to match your pace for learning or presenting.

- 🔄 **Pause, Resume, and Reset Controls**  
  Flexible simulation management to explain steps clearly or test multiple scenarios.

- 🧾 **Support for Non-Zero Arrival Times**  
  Unlike many simulators, this tool dynamically handles processes arriving at different times.

- 🎨 **Dark Themed, User-Friendly Interface**  
  Designed for both clarity and aesthetics, with focus on ease of understanding.

---

## 💡 How It Works

1. Enter process names, arrival times, burst times, and a time quantum.
2. Click **Start** to begin the simulation.
3. Watch as the algorithm runs step-by-step:
   - Timeline logs get updated
   - Gantt chart is animated live
   - Statistics and usage charts are updated automatically
4. Pause or resume anytime. Reset to try different inputs.

---

## 📦 Requirements

- Python 3.6+
- Tkinter (usually pre-installed with Python)

To install missing dependencies:

```bash
pip install tk
