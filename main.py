import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import socket
import subprocess
import platform
import threading
import urllib.request
import urllib.parse
import uuid
from datetime import datetime


BG = "#0b1220"
PANEL = "#111c2e"
CARD = "#17243a"
BLUE = "#3b82f6"
CYAN = "#38bdf8"
WHITE = "#f1f5f9"
MUTED = "#94a3b8"
GREEN = "#22c55e"
RED = "#ef4444"

COMMON_PORTS = [
    20, 21, 22, 23, 25, 53, 80,
    110, 143, 443, 445, 3306, 3389, 8080
]


class NetworkTracker:

    def __init__(self, root):
        self.root = root
        self.root.title("Network Tracker | Dashboard")
        self.root.geometry("1150x780")
        self.root.minsize(950, 680)
        self.root.configure(bg=BG)

        self.busy = False
        self.create_ui()

    def create_ui(self):

        # Main header
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=28, pady=(22, 12))

        tk.Label(
            header,
            text="NETWORK TRACKER",
            font=("Segoe UI", 23, "bold"),
            bg=BG,
            fg=WHITE
        ).pack(side="left")

        tk.Label(
            header,
            text="NETWORK DIAGNOSTICS",
            font=("Segoe UI", 9, "bold"),
            bg=BG,
            fg=CYAN
        ).pack(side="right", pady=10)

        tk.Label(
            self.root,
            text="Monitor, analyse and troubleshoot your network.",
            font=("Segoe UI", 11),
            bg=BG,
            fg=MUTED
        ).pack(anchor="w", padx=30)

        # Target input panel
        target_panel = tk.Frame(
            self.root,
            bg=PANEL,
            highlightbackground="#263750",
            highlightthickness=1
        )
        target_panel.pack(fill="x", padx=28, pady=20)

        tk.Label(
            target_panel,
            text="TARGET HOST / IP ADDRESS",
            font=("Segoe UI", 9, "bold"),
            bg=PANEL,
            fg=MUTED
        ).pack(anchor="w", padx=18, pady=(13, 5))

        input_row = tk.Frame(target_panel, bg=PANEL)
        input_row.pack(fill="x", padx=18, pady=(0, 15))

        self.target = tk.Entry(
            input_row,
            font=("Segoe UI", 12),
            bg="#0b1628",
            fg=WHITE,
            insertbackground=WHITE,
            relief="flat",
            bd=0
        )
        self.target.insert(0, "google.com")
        self.target.pack(side="left", fill="x", expand=True, ipady=11)

        self.target.bind(
            "<Return>",
            lambda event: self.dns_lookup()
        )

        tk.Button(
            input_row,
            text="DNS LOOKUP",
            command=self.dns_lookup,
            bg=BLUE,
            fg="white",
            activebackground="#2563eb",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=18,
            pady=9
        ).pack(side="left", padx=(12, 0))

        # Dashboard section
        tk.Label(
            self.root,
            text="NETWORK TOOLS",
            font=("Segoe UI", 13, "bold"),
            bg=BG,
            fg=WHITE
        ).pack(anchor="w", padx=30, pady=(0, 12))

        tools = tk.Frame(self.root, bg=BG)
        tools.pack(fill="x", padx=28)

        features = [
            ("PUBLIC IP", "Find your internet-facing IP address", self.public_ip),
            ("PRIVATE IP", "Find your local network IP address", self.private_ip),
            ("MAC ADDRESS", "View your device MAC address", self.mac_address),
            ("HOSTNAME", "Find your computer hostname", self.hostname),
            ("PING TEST", "Test connectivity and response time", self.ping_test),
            ("TRACEROUTE", "View the route to a destination", self.traceroute),
            ("PORT SCANNER", "Check common TCP ports", self.port_scanner),
            ("WEBSITE CHECK", "Check HTTP website availability", self.website_check),
            ("NETWORK DETAILS", "View network adapter information", self.network_details),
            ("DNS LOOKUP", "Resolve a domain into IP addresses", self.dns_lookup)
        ]

        for index, (name, description, action) in enumerate(features):
            row = index // 2
            column = index % 2

            card = tk.Frame(
                tools,
                bg=CARD,
                highlightbackground="#263750",
                highlightthickness=1
            )
            card.grid(
                row=row,
                column=column,
                sticky="ew",
                padx=6,
                pady=6
            )

            tools.grid_columnconfigure(column, weight=1)

            text_frame = tk.Frame(card, bg=CARD)
            text_frame.pack(
                side="left",
                fill="both",
                expand=True,
                padx=13,
                pady=11
            )

            tk.Label(
                text_frame,
                text=name,
                font=("Segoe UI", 10, "bold"),
                bg=CARD,
                fg=WHITE
            ).pack(anchor="w")

            tk.Label(
                text_frame,
                text=description,
                font=("Segoe UI", 8),
                bg=CARD,
                fg=MUTED,
                wraplength=230,
                justify="left"
            ).pack(anchor="w", pady=(3, 0))

            tk.Button(
                card,
                text="RUN",
                command=action,
                bg=BLUE,
                fg="white",
                activebackground="#2563eb",
                activeforeground="white",
                relief="flat",
                font=("Segoe UI", 8, "bold"),
                cursor="hand2",
                padx=12,
                pady=7
            ).pack(side="right", padx=12)

        # Results heading
        result_header = tk.Frame(self.root, bg=BG)
        result_header.pack(fill="x", padx=30, pady=(18, 7))

        tk.Label(
            result_header,
            text="RESULTS CONSOLE",
            font=("Segoe UI", 12, "bold"),
            bg=BG,
            fg=WHITE
        ).pack(side="left")

        self.status = tk.Label(
            result_header,
            text="● READY",
            font=("Segoe UI", 9, "bold"),
            bg=BG,
            fg=GREEN
        )
        self.status.pack(side="right")

        # Results panel
        output_frame = tk.Frame(
            self.root,
            bg="#060d18",
            highlightbackground="#263750",
            highlightthickness=1
        )
        output_frame.pack(
            fill="both",
            expand=True,
            padx=28,
            pady=(0, 10)
        )

        scrollbar = tk.Scrollbar(output_frame)
        scrollbar.pack(side="right", fill="y")

        self.output = tk.Text(
            output_frame,
            bg="#060d18",
            fg="#dbeafe",
            insertbackground=WHITE,
            font=("Consolas", 10),
            relief="flat",
            wrap="word",
            yscrollcommand=scrollbar.set,
            padx=14,
            pady=12
        )
        self.output.pack(fill="both", expand=True)

        scrollbar.config(command=self.output.yview)

        self.output.insert(
            "end",
            "Welcome to Network Tracker.\n"
            "Select a network tool above to begin testing.\n"
        )

        # Bottom actions
        bottom = tk.Frame(self.root, bg=BG)
        bottom.pack(fill="x", padx=28, pady=(0, 15))

        tk.Button(
            bottom,
            text="EXPORT REPORT",
            command=self.export_report,
            bg=GREEN,
            fg="#052e16",
            activebackground="#16a34a",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            padx=18,
            pady=9,
            cursor="hand2"
        ).pack(side="left")

        tk.Button(
            bottom,
            text="CLEAR RESULTS",
            command=self.clear_results,
            bg="#263750",
            fg=WHITE,
            activebackground="#334155",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            padx=18,
            pady=9,
            cursor="hand2"
        ).pack(side="left", padx=10)

        tk.Label(
            bottom,
            text="Python Network Diagnostics Tool",
            font=("Segoe UI", 8),
            bg=BG,
            fg=MUTED
        ).pack(side="right", pady=10)

    def get_target(self):
        value = self.target.get().strip()

        if not value:
            messagebox.showwarning(
                "Missing Target",
                "Please enter a domain or IP address."
            )
            return None

        return value

    def run_task(self, title, function):

        if self.busy:
            messagebox.showinfo(
                "Please Wait",
                "Another operation is currently running."
            )
            return

        self.busy = True
        self.status.config(text="● RUNNING", fg=CYAN)

        def worker():
            try:
                result = function()
            except Exception as error:
                result = f"Operation failed: {error}"

            self.root.after(
                0,
                lambda: self.finish_task(title, result)
            )

        threading.Thread(target=worker, daemon=True).start()

    def finish_task(self, title, result):
        self.output.insert(
            "end",
            f"\n{'=' * 55}\n"
            f"{title}\n"
            f"Time: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n"
            f"{'=' * 55}\n"
            f"{result}\n"
        )

        self.output.see("end")
        self.busy = False
        self.status.config(text="● COMPLETED", fg=GREEN)

    def public_ip(self):
        def task():
            with urllib.request.urlopen(
                "https://api.ipify.org",
                timeout=10
            ) as response:
                return "Public IP: " + response.read().decode()

        self.run_task("PUBLIC IP ADDRESS", task)

    def private_ip(self):
        def task():
            connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            try:
                connection.connect(("8.8.8.8", 80))
                address = connection.getsockname()[0]
            finally:
                connection.close()

            return "Private IP: " + address

        self.run_task("PRIVATE IP ADDRESS", task)

    def mac_address(self):
        def task():
            mac = uuid.getnode()

            formatted = ":".join(
                f"{(mac >> shift) & 255:02X}"
                for shift in range(40, -1, -8)
            )

            return "MAC Address: " + formatted

        self.run_task("MAC ADDRESS", task)

    def hostname(self):
        def task():
            return (
                "Hostname: " + socket.gethostname()
                + "\nComputer: " + platform.node()
                + "\nOperating System: " + platform.system()
            )

        self.run_task("HOSTNAME INFORMATION", task)

    def dns_lookup(self):
        target = self.get_target()

        if not target:
            return

        def task():
            addresses = socket.getaddrinfo(
                target,
                None,
                socket.AF_INET
            )

            unique = sorted({
                item[4][0] for item in addresses
            })

            return (
                f"Domain: {target}\n"
                "IPv4 Addresses:\n"
                + "\n".join(unique)
            )

        self.run_task("DNS LOOKUP", task)

    def ping_test(self):
        target = self.get_target()

        if not target:
            return

        def task():
            if platform.system().lower() == "windows":
                command = [
                    "ping", "-n", "4", "-w", "2000", target
                ]
            else:
                command = ["ping", "-c", "4", target]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=20
            )

            return result.stdout or result.stderr

        self.run_task("PING TEST", task)

    def traceroute(self):
        target = self.get_target()

        if not target:
            return

        def task():
            if platform.system().lower() == "windows":
                command = [
                    "tracert", "-d", "-h", "20", "-w", "1000", target
                ]
            else:
                command = ["traceroute", "-m", "20", target]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=65
            )

            return result.stdout or result.stderr

        self.run_task("TRACEROUTE", task)

    def port_scanner(self):
        target = self.get_target()

        if not target:
            return

        approved = messagebox.askyesno(
            "Permission Required",
            "Only scan systems you own or have permission to test.\n\n"
            "Are you authorized to scan this target?"
        )

        if not approved:
            return

        def task():
            ip = socket.gethostbyname(target)
            results = [f"Target: {target} ({ip})", ""]

            for port in COMMON_PORTS:
                connection = socket.socket(
                    socket.AF_INET,
                    socket.SOCK_STREAM
                )
                connection.settimeout(0.5)

                try:
                    status = connection.connect_ex((ip, port))
                    state = "OPEN" if status == 0 else "Closed / filtered"
                    results.append(f"Port {port}: {state}")
                finally:
                    connection.close()

            return "\n".join(results)

        self.run_task("AUTHORIZED PORT SCAN", task)

    def website_check(self):
        target = self.get_target()

        if not target:
            return

        def task():
            address = target

            if not address.startswith(("http://", "https://")):
                address = "https://" + address

            parsed = urllib.parse.urlparse(address)

            if not parsed.hostname:
                raise ValueError("Invalid website address.")

            request = urllib.request.Request(
                address,
                headers={"User-Agent": "NetworkTracker/1.0"},
                method="GET"
            )

            try:
                with urllib.request.urlopen(
                    request,
                    timeout=10
                ) as response:
                    return (
                        f"Website: {address}\n"
                        f"Status Code: {response.status}\n"
                        f"Result: Website responded successfully."
                    )
            except urllib.error.HTTPError as error:
                return (
                    f"Website: {address}\n"
                    f"HTTP Status: {error.code}\n"
                    f"Result: Website responded with an HTTP error."
                )

        self.run_task("WEBSITE CONNECTIVITY CHECK", task)

    def network_details(self):
        def task():
            if platform.system().lower() == "windows":
                command = ["ipconfig", "/all"]
            else:
                command = ["ip", "address"]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=15
            )

            return result.stdout or result.stderr

        self.run_task("NETWORK INTERFACE DETAILS", task)

    def export_report(self):
        content = self.output.get("1.0", "end")

        if not content.strip():
            messagebox.showinfo(
                "No Results",
                "There are no results to export."
            )
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile="Network_Tracker_Report.txt",
            filetypes=[("Text files", "*.txt")]
        )

        if filename:
            with open(filename, "w", encoding="utf-8") as file:
                file.write(content)

            messagebox.showinfo(
                "Export Successful",
                "Your report has been saved."
            )

    def clear_results(self):
        self.output.delete("1.0", "end")
        self.status.config(text="● READY", fg=GREEN)


if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkTracker(root)
    root.mainloop()
