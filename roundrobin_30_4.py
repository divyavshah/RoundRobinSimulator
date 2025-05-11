import tkinter as tk
from tkinter import ttk
from collections import defaultdict
from collections import deque
import random

class EnhancedRoundRobinSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Round Robin Scheduler")
        
        # Window configuration
        self.root.geometry("1100x850")
        self.root.configure(bg='#121212')
        self.root.grid_rowconfigure(0, weight=1)  # Row for Input and Timeline
        self.root.grid_rowconfigure(1, weight=2)  # Row for Visual + Stats
        self.root.grid_rowconfigure(2, weight=1) 
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Process data
        self.processes = []
        self.burst_times = []
        self.arrival_times = []
        self.time_quantum = 0
        self.simulation_running = False
        self.after_id = None
        self.speed = tk.IntVar(value=800)  # Animation speed in ms

        # Statistics tracking
        self.waiting_times = defaultdict(int)
        self.turnaround_times = defaultdict(int)
        self.response_times = {}
        self.first_run = set()
        self.completion_times = []
        self.gantt_chart = []

        # Visualization parameters
        self.block_width = 70
        self.block_height = 50
        self.block_gap = 5
        self.x_offset = 20
        self.y_offset = 50
        self.current_row = 0
        self.max_row_width = 900

        # Color scheme with diverse colors
        self.process_colors = [
            '#e6194b', '#3cb44b', '#ffe119', '#f58231',
            '#46f0f0', '#f032e6', '#bcf60c', '#fabebe',
            '#fffac8', '#aaffc3', '#ffd8b1'
        ]

        # Create all frames
        self.create_input_frame()
        self.create_execution_frame()
        self.create_visualization_frame()
        self.create_statistics_frame()
        self.create_time_usage_frame()

    def create_input_frame(self):
        input_frame = tk.LabelFrame(self.root, text="Process Input", padx=10, pady=10, 
                                  bg='#1E1E1E', fg='#FFFFFF', font=('Consolas', 10, 'bold'))
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky='new')
        input_frame.configure(height=150)  # Set height explicitly  # Prevent expansion based on content

        # Process input
        tk.Label(input_frame, text="Process Names (comma separated):", 
                bg='#1E1E1E', fg='#FFFFFF', font=('Consolas', 9)).grid(row=0, column=0, sticky='w')
        self.process_entry = tk.Entry(input_frame, width=30, bg='#2D2D2D', fg='#FFFFFF',
                                    insertbackground='white', font=('Consolas', 9))
        self.process_entry.grid(row=0, column=1, padx=5, pady=5)

        # Arrival time input
        tk.Label(input_frame, text="Arrival Times (comma separated):", 
                bg='#1E1E1E', fg='#FFFFFF', font=('Consolas', 9)).grid(row=1, column=0, sticky='w')
        self.arrival_entry = tk.Entry(input_frame, width=30, bg='#2D2D2D', fg='#FFFFFF',
                                    insertbackground='white', font=('Consolas', 9))
        self.arrival_entry.grid(row=1, column=1, padx=5, pady=5)

         # Burst time input
        tk.Label(input_frame, text="Burst Times (comma separated):", 
                bg='#1E1E1E', fg='#FFFFFF', font=('Consolas', 9)).grid(row=2, column=0, sticky='w')
        self.burst_entry = tk.Entry(input_frame, width=30, bg='#2D2D2D', fg='#FFFFFF',
                                  insertbackground='white', font=('Consolas', 9))
        self.burst_entry.grid(row=2, column=1, padx=5, pady=5)

        # Quantum input
        tk.Label(input_frame, text="Time Quantum:", 
                bg='#1E1E1E', fg='#FFFFFF', font=('Consolas', 9)).grid(row=3, column=0, sticky='w')
        self.quantum_entry = tk.Entry(input_frame, width=30, bg='#2D2D2D', fg='#FFFFFF',
                                     insertbackground='white', font=('Consolas', 9))
        self.quantum_entry.grid(row=3, column=1, padx=5, pady=5)

        # Control buttons
        button_frame = tk.Frame(input_frame, bg='#1E1E1E')
        button_frame.grid(row=4, column=0, columnspan=2, pady=(5,0))
        
        self.start_btn = tk.Button(button_frame, text="Start", command=self.start_simulation,
                                 bg='#2D2D2D', fg='#FFFFFF', activebackground='#3D3D3D',
                                 activeforeground='#FFFFFF', font=('Consolas', 9, 'bold'))
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.pause_btn = tk.Button(button_frame, text="Pause", state=tk.DISABLED, command=self.toggle_pause,
                                  bg='#2D2D2D', fg='#FFFFFF', activebackground='#3D3D3D',
                                  activeforeground='#FFFFFF', font=('Consolas', 9, 'bold'))
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        
        self.reset_btn = tk.Button(button_frame, text="Reset", command=self.reset_simulation,
                                  bg='#2D2D2D', fg='#FFFFFF', activebackground='#3D3D3D',
                                  activeforeground='#FFFFFF', font=('Consolas', 9, 'bold'))
        self.reset_btn.pack(side=tk.LEFT, padx=5)


        # Speed control
        speed_frame = tk.Frame(input_frame, bg='#1E1E1E')
        speed_frame.grid(row=4, column=2, columnspan=2, sticky='n', padx=5)
        tk.Label(speed_frame, text="Animation Speed:", bg='#1E1E1E', fg='#FFFFFF',
                font=('Consolas', 9)).pack(side=tk.LEFT)
        ttk.Scale(speed_frame, from_=100, to=2000, variable=self.speed, orient=tk.HORIZONTAL,
                 command=lambda _: None).pack(side=tk.LEFT, padx=5)

    def create_execution_frame(self):
        exec_frame = tk.LabelFrame(self.root, text="Execution Timeline", padx=10, pady=10,
                                 bg='#1E1E1E', fg='#FFFFFF', font=('Consolas', 10, 'bold'))
        exec_frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
        exec_frame.configure(height=230)
        exec_frame.grid_propagate(False)

        self.timeline_text = tk.Text(exec_frame, width=50, height=15, wrap=tk.WORD,
                                    bg='#2D2D2D', fg='#FFFFFF', insertbackground='white',
                                    font=('Consolas', 10))
        self.timeline_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(exec_frame, command=self.timeline_text.yview,
                                bg='#1E1E1E', troughcolor='#2D2D2D', activebackground='#3D3D3D')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.timeline_text.config(yscrollcommand=scrollbar.set)

    def create_visualization_frame(self):
        vis_frame = tk.LabelFrame(self.root, text="Process Visualization", padx=10, pady=10,
                                bg='#1E1E1E', fg='#FFFFFF', font=('Consolas', 10, 'bold'))
        vis_frame.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

        # Current process display
        self.current_process = tk.StringVar(value="Ready")
        tk.Label(vis_frame, text="Currently Running:", 
                bg='#1E1E1E', fg='#FFFFFF', font=('Consolas', 10)).pack(anchor='w')
        tk.Label(vis_frame, textvariable=self.current_process, 
                bg='#1E1E1E', fg='#4ECDC4', font=('Consolas', 12, 'bold')).pack(anchor='w')

        self.canvas = tk.Canvas(vis_frame, bg='#1E1E1E',highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def create_statistics_frame(self):
        stats_frame = tk.LabelFrame(self.root, text="Process Statistics", padx=10, pady=10,
                                  bg='#1E1E1E', fg='#FFFFFF', font=('Consolas', 10, 'bold'))
        stats_frame.grid(row=1, column=1, padx=10, pady=10, sticky='nsew')

        self.stats_text = tk.Text(stats_frame, width=40, height=10, state=tk.DISABLED,
                                 bg='#2D2D2D', fg='#FFFFFF', font=('Consolas', 10))
        self.stats_text.pack(side=tk.LEFT,fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(stats_frame, command=self.stats_text.yview,
                                bg='#1E1E1E', troughcolor='#2D2D2D', activebackground='#3D3D3D')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.stats_text.config(yscrollcommand=scrollbar.set)

    def create_time_usage_frame(self):
        time_frame = tk.LabelFrame(self.root, text="Time Usage by Process", padx=10, pady=10,
                                 bg='#1E1E1E', fg='#FFFFFF', font=('Consolas', 10, 'bold'))
        time_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')

        self.time_canvas = tk.Canvas(time_frame, bg='#1E1E1E',height=250, highlightthickness=0)
        self.time_canvas.pack(fill=tk.BOTH, expand=True)

    def get_process_color(self, process_name):
        return self.process_color_map.get(process_name, '#FFFFFF')  # Default to white if not found


    def start_simulation(self):
        try:
            processes = [p.strip() for p in self.process_entry.get().split(',')]
            bursts = [int(b.strip()) for b in self.burst_entry.get().split(',')]
            quantum = int(self.quantum_entry.get())
            arrivals = [int(a.strip()) for a in self.arrival_entry.get().split(',')]
            if len(arrivals) != len(processes):
                raise ValueError("Arrival times count doesn't match process count")

            
            if len(processes) != len(bursts):
                raise ValueError("Process count doesn't match burst times count")
            if quantum <= 0:
                raise ValueError("Quantum must be positive")
                
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {str(e)}")
            return

        # Initialize simulation state
        self.processes = processes
        self.burst_times = bursts.copy()
        self.arrival_times = arrivals.copy()
        self.time_quantum = quantum
        self.remaining_times = bursts.copy()
        self.time = 0
        self.completion_times = [0] * len(processes)
        self.first_run = set()
        self.gantt_chart = []

        random.shuffle(self.process_colors)
        self.process_color_map = {}
        for idx, process in enumerate(self.processes):
            self.process_color_map[process] = self.process_colors[idx % len(self.process_colors)]
        
        # Reset statistics
        self.waiting_times = defaultdict(int)
        self.turnaround_times = defaultdict(int)
        self.response_times = {}
        
        # Clear displays
        self.timeline_text.config(state=tk.NORMAL)
        self.timeline_text.delete(1.0, tk.END)
        self.timeline_text.config(state=tk.DISABLED)
        self.canvas.delete("all")
        self.time_canvas.delete("all")
        self.update_stats()
        
        # Initialize queue based on arrival times
        self.queue = deque(sorted(
            [i for i in range(len(processes)) if arrivals[i] == 0],
            key=lambda x: arrivals[x]
        ))

        
        # Enable/disable buttons
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL, text="Pause")
        self.simulation_running = True
        
        # Start the simulation
        self.log_timeline(">>> Simulation started")
        self.log_timeline(f">>> Time quantum: {quantum}")
        self.run_simulation_step()


    def run_simulation_step(self):
        if not self.simulation_running:
            return

    # Check for new arrivals if using arrival times
    
        new_arrivals = [
            i for i in range(len(self.processes))
            if self.arrival_times[i] == self.time
            and i not in self.queue
            and self.remaining_times[i] > 0
        ]
        for new in new_arrivals:
            self.queue.append(new)
            self.log_timeline(f">>> Time {self.time}: {self.processes[new]} arrived")

        if not self.queue:
        # Check if all processes are done
            if all(t == 0 for t in self.remaining_times):
                self.finish_simulation()
                return
            else:
                self.time += 1
                self.after_id = self.root.after(self.speed.get(), self.run_simulation_step)
                return

        process_idx = self.queue.popleft()
        process_name = self.processes[process_idx]
        remaining = self.remaining_times[process_idx]

    # Track first run for response time
        if process_name not in self.response_times:
            self.response_times[process_name] = self.time

    # Determine execution duration
        exec_time = min(self.time_quantum, remaining)
        start_time = self.time
        end_time = start_time + exec_time

    # Update timeline
        self.log_timeline(f">>> Time {start_time}-{end_time}: {process_name} executes for {exec_time} units")
        self.current_process.set(f"{process_name} ({start_time}-{end_time})")

    # Draw process block
        self.draw_process_block(process_name, start_time, end_time, process_idx)

    # Record for time usage visualization
        self.gantt_chart.append((process_name, start_time, end_time))

    # Update process state
        self.remaining_times[process_idx] -= exec_time
        self.time = end_time

    # Update waiting times only for processes in queue
        for idx in list(self.queue):
           if self.remaining_times[idx] > 0 and self.arrival_times[idx] <= self.time:
                self.waiting_times[self.processes[idx]] += exec_time

    # Check for new arrivals after execution
        new_arrivals = [
            i for i in range(len(self.processes))
            if self.arrival_times[i] > start_time and self.arrival_times[i] <= self.time
            and i not in self.queue
            and self.remaining_times[i] > 0
            ]
        for new in new_arrivals:
            self.queue.append(new)
            self.log_timeline(f">>> Time {self.time}: {self.processes[new]} arrived")


    # Requeue if not finished
        if self.remaining_times[process_idx] > 0:
            self.queue.append(process_idx)
            status = "requeued"
        else:
            self.completion_times[process_idx] = self.time
            status = "completed"

        self.log_timeline(f">>> Time {end_time}: {process_name} {status}")

    # Update time usage visualization
        self.update_time_usage()

    # Schedule next step
        self.after_id = self.root.after(self.speed.get(), self.run_simulation_step)

    
    def draw_process_block(self, process, start, end, process_idx):
        color = self.get_process_color(process)

        
        # Check if we need new row
        if self.x_offset + self.block_width > self.max_row_width:
            self.x_offset = 20
            self.y_offset += self.block_height + 10
            self.current_row += 1
        
        # Draw the block
        x1, y1 = self.x_offset, self.y_offset
        x2, y2 = x1 + self.block_width, y1 + self.block_height
        
        # Create block with outline
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='#333333', width=1)
        self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text=process, fill='black', 
                               font=('Consolas', 9, 'bold'))
        self.canvas.create_text((x1+x2)/2, y2-10, text=f"{start}-{end}", fill='black',
                              font=('Consolas', 7))
        
        self.x_offset += self.block_width + self.block_gap

    def update_time_usage(self):
        self.time_canvas.delete("all")
        
        if not self.gantt_chart:
            return
            
        # Calculate total time
        total_time = max(end for _, _, end in self.gantt_chart)
        if total_time == 0:
            return
            
        # Calculate scale
        canvas_width = self.time_canvas.winfo_width() - 40
        scale = canvas_width / total_time if total_time > 0 else 1
        
        # Draw time scale
        self.time_canvas.create_line(20, 30, 20 + canvas_width, 30, fill='#FFFFFF', width=2)
        for t in range(0, total_time + 1, max(1, total_time // 10)):
            x = 20 + t * scale
            self.time_canvas.create_line(x, 25, x, 35, fill='#FFFFFF')
            self.time_canvas.create_text(x, 45, text=str(t), fill='#FFFFFF', font=('Consolas', 8))
        
        # Draw process bars
        y_start = 60
        bar_height = 20
        process_rows = {}
        current_row = 0
        
        for process, start, end in self.gantt_chart:
            if process not in process_rows:
                process_rows[process] = current_row
                current_row += 1
                
            y = y_start + process_rows[process] * (bar_height + 5)
            x1 = 20 + start * scale
            x2 = 20 + end * scale
            
            color = self.get_process_color(process)

            self.time_canvas.create_rectangle(x1, y, x2, y + bar_height, fill=color, outline='#333333')
            self.time_canvas.create_text((x1+x2)/2, y + bar_height/2, text=process, 
                                        fill='black', font=('Consolas', 8))
        
        # Draw legend
        legend_y = y_start + len(process_rows) * (bar_height + 5) + 20
        for i, process in enumerate(process_rows.keys()):
            color = self.get_process_color(process)

            self.time_canvas.create_rectangle(20 + i * 120, legend_y, 20 + i * 120 + 20, legend_y + 20, 
                                            fill=color, outline='#333333')
            self.time_canvas.create_text(20 + i * 120 + 30, legend_y + 10, text=process, 
                                       fill='#FFFFFF', font=('Consolas', 8), anchor='w')

    def log_timeline(self, message):
        self.timeline_text.config(state=tk.NORMAL)
        self.timeline_text.insert(tk.END, message + "\n")
        self.timeline_text.see(tk.END)
        self.timeline_text.config(state=tk.DISABLED)

    def toggle_pause(self):
        if self.simulation_running:
            self.simulation_running = False
            self.pause_btn.config(text="Resume")
            if self.after_id:
                self.root.after_cancel(self.after_id)
            self.log_timeline(">>> Simulation paused")
        else:
            self.simulation_running = True
            self.pause_btn.config(text="Pause")
            self.log_timeline(">>> Simulation resumed")
            self.run_simulation_step()

    def finish_simulation(self):
        self.simulation_running = False
        self.current_process.set("Simulation Complete")
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        
        # Calculate final statistics
        for i, name in enumerate(self.processes):
           self.turnaround_times[name] = self.completion_times[i] - self.arrival_times[i]
        
        self.log_timeline(">>> Simulation completed")
        self.update_stats()
        self.update_time_usage()

    def update_stats(self):
        stats = ["Process Statistics:\n"]
        stats.append(f"{'Process':<10}{'Arrival':<10}{'Burst':<8}{'Completion':<12}{'Turnaround':<12}{'Waiting':<8}")
        stats.append("-"*60)

        total_tt = 0
        total_wt = 0

        for i, name in enumerate(self.processes):
            arrival = self.arrival_times[i]

            burst = self.burst_times[i]
            completion = self.completion_times[i]
            turnaround = completion - arrival
            waiting = turnaround - burst
        
            total_tt += turnaround
            total_wt += waiting

            stats.append(f"{name:<10}{arrival:<10}{burst:<8}{completion:<12}{turnaround:<12}{waiting:<8}")

        if self.processes:
            avg_tt = total_tt / len(self.processes)
            avg_wt = total_wt / len(self.processes)
            stats.append("\nAverage Turnaround Time: {:.2f}".format(avg_tt))
            stats.append("Average Waiting Time: {:.2f}".format(avg_wt))

        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, "\n".join(stats))
        self.stats_text.config(state=tk.DISABLED)


    def reset_simulation(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        
        self.simulation_running = False
        self.current_process.set("Ready")
        
        # Clear all displays
        self.timeline_text.config(state=tk.NORMAL)
        self.timeline_text.delete(1.0, tk.END)
        self.timeline_text.config(state=tk.DISABLED)
        
        self.canvas.delete("all")
        self.time_canvas.delete("all")
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.config(state=tk.DISABLED)
        
        # Reset buttons
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED, text="Pause")
        
        # Reset visualization parameters
        self.x_offset = 20
        self.y_offset = 50
        self.current_row = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedRoundRobinSimulator(root)
    root.mainloop()
