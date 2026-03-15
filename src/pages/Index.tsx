import { useState, useCallback, useRef } from "react";
import AutomationForm, { type FormData } from "@/components/AutomationForm";
import StatusPanel, { type LogEntry } from "@/components/StatusPanel";
import EmployeeTable, { type Employee } from "@/components/EmployeeTable";
import { Bot, Download } from "lucide-react";

const API_BASE_URL = "";

const Index = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [createdEmployee, setCreatedEmployee] = useState<FormData | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const addLog = useCallback((message: string, type: LogEntry["type"] = "info") => {
    const timestamp = new Date().toLocaleTimeString("en-US", { hour12: false });
    setLogs((prev) => [...prev, { message, type, timestamp }]);
  }, []);

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  const runAutomation = useCallback(
    async (data: FormData) => {
      setIsRunning(true);
      setLogs([]);
      setEmployees([]);
      setCreatedEmployee(null);
      stopPolling();

      try {
        addLog("Connecting to automation backend...", "info");

        // Step 1: Start the job — backend returns immediately with a jobId
        const startRes = await fetch(`${API_BASE_URL}/api/run`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            username: data.username,
            password: data.password,
            firstName: data.firstName,
            lastName: data.lastName,
            employeeId: data.employeeId,
          }),
        });

        if (!startRes.ok) {
          const err = await startRes.json().catch(() => ({}));
          throw new Error(err.error ?? `HTTP ${startRes.status}: ${startRes.statusText}`);
        }

        const { jobId } = await startRes.json();
        addLog(`Job started (ID: ${jobId})`, "info");

        // Step 2: Poll /api/status/:jobId every 2 seconds for live logs + result
        let lastLogCount = 0;

        pollRef.current = setInterval(async () => {
          try {
            const statusRes = await fetch(`${API_BASE_URL}/api/status/${jobId}`);
            if (!statusRes.ok) return;

            const job = await statusRes.json();

            // Append only NEW logs since last poll
            const newLogs: string[] = job.logs.slice(lastLogCount);
            lastLogCount = job.logs.length;

            for (const msg of newLogs) {
              const type: LogEntry["type"] =
                msg.includes("✓") || msg.includes("successful") || msg.includes("success")
                  ? "success"
                  : msg.includes("✗") || msg.includes("ERROR") || msg.includes("error") || msg.includes("failed")
                  ? "error"
                  : msg.includes("Warning") || msg.includes("warning")
                  ? "warning"
                  : "info";
              addLog(msg, type);
            }

            if (job.state === "done") {
              stopPolling();
              setEmployees(job.employees ?? []);
              setCreatedEmployee(job.createdEmployee ?? null);
              addLog("Automation completed successfully!", "success");
              setIsRunning(false);
            } else if (job.state === "error") {
              stopPolling();
              addLog(`Automation failed: ${job.error ?? "Unknown error"}`, "error");
              setIsRunning(false);
            }
          } catch (pollErr) {
            // Network hiccup during poll — don't abort, just skip this tick
            console.warn("Poll error:", pollErr);
          }
        }, 2000);
      } catch (error) {
        stopPolling();
        const errorMessage = error instanceof Error ? error.message : "Unknown error occurred";
        addLog(`Connection error: ${errorMessage}`, "error");
        addLog("Make sure the backend is running on http://localhost:9000", "warning");
        console.error("Automation error:", error);
        setIsRunning(false);
      }
    },
    [addLog, stopPolling]
  );

  const handleExportCSV = useCallback(async () => {
    try {
      addLog("Preparing CSV export...", "info");
      const response = await fetch(`${API_BASE_URL}/api/export-csv`);

      if (!response.ok) {
        throw new Error("Failed to export CSV");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `employees_${new Date().toISOString().split("T")[0]}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      addLog("CSV exported successfully!", "success");
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      addLog(`Export failed: ${errorMessage}`, "error");
    }
  }, [addLog]);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <Bot className="h-5 w-5 text-primary" />
            <h1 className="text-base font-semibold text-foreground">
              OrangeHRM Automation Dashboard
            </h1>
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="mx-auto max-w-6xl px-6 py-8">
        <div className="grid gap-6 lg:grid-cols-[380px_1fr]">
          {/* Left: Form */}
          <div className="space-y-6">
            <AutomationForm onSubmit={runAutomation} isRunning={isRunning} />

            {/* Created Employee Info */}
            {createdEmployee && (
              <div className="rounded-lg border border-green-200 bg-green-50 p-4">
                <h3 className="mb-3 text-sm font-semibold text-green-900">
                  ✓ Employee Created
                </h3>
                <div className="space-y-2 text-sm text-green-800">
                  <p><strong>First Name:</strong> {createdEmployee.firstName}</p>
                  <p><strong>Last Name:</strong> {createdEmployee.lastName}</p>
                  <p><strong>Employee ID:</strong> {createdEmployee.employeeId}</p>
                </div>
              </div>
            )}

            {/* Export Button */}
            {employees.length > 0 && (
              <button
                onClick={handleExportCSV}
                className="flex w-full items-center justify-center gap-2 rounded-md bg-green-600 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-green-700"
              >
                <Download className="h-4 w-4" />
                Export as CSV
              </button>
            )}
          </div>

          {/* Right: Status + Table */}
          <div className="space-y-6">
            <StatusPanel logs={logs} isRunning={isRunning} />
            {employees.length > 0 && <EmployeeTable employees={employees} />}
          </div>
        </div>
      </main>
    </div>
  );
};

export default Index;