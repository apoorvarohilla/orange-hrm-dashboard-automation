import { useState, useCallback } from "react";
import AutomationForm, { type FormData } from "@/components/AutomationForm";
import StatusPanel, { type LogEntry } from "@/components/StatusPanel";
import EmployeeTable, { type Employee } from "@/components/EmployeeTable";
import { Bot, Download } from "lucide-react";

const API_BASE_URL = "http://localhost:9000";

const Index = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [createdEmployee, setCreatedEmployee] = useState<FormData | null>(null);

  const addLog = useCallback((message: string, type: LogEntry["type"] = "info") => {
    const timestamp = new Date().toLocaleTimeString("en-US", { hour12: false });
    setLogs((prev) => [...prev, { message, type, timestamp }]);
  }, []);

  const runAutomation = useCallback(
    async (data: FormData) => {
      setIsRunning(true);
      setLogs([]);
      setEmployees([]);
      setCreatedEmployee(null);

      try {
        addLog("Connecting to automation backend...", "info");
        
        const response = await fetch(`${API_BASE_URL}/api/run`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            username: data.username,
            password: data.password,
            firstName: data.firstName,
            lastName: data.lastName,
            employeeId: data.employeeId,
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();

        // Add backend logs to UI
        if (result.logs && Array.isArray(result.logs)) {
          for (const logMessage of result.logs) {
            // Determine log type based on message content
            let logType: LogEntry["type"] = "info";
            if (logMessage.includes("✓") || logMessage.includes("successful")) {
              logType = "success";
            } else if (logMessage.includes("✗") || logMessage.includes("ERROR") || logMessage.includes("error")) {
              logType = "error";
            } else if (logMessage.includes("Warning") || logMessage.includes("warning")) {
              logType = "warning";
            }
            addLog(logMessage, logType);
          }
        }

        if (result.status === "success") {
          addLog("Automation completed successfully!", "success");
          
          if (result.employees && Array.isArray(result.employees)) {
            setEmployees(result.employees);
          }

          if (result.createdEmployee) {
            setCreatedEmployee(result.createdEmployee);
          }
        } else {
          addLog("Automation failed. Check logs for details.", "error");
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : "Unknown error occurred";
        addLog(`Connection error: ${errorMessage}`, "error");
        addLog("Make sure the backend is running on http://localhost:9000", "warning");
        console.error("Automation error:", error);
      } finally {
        setIsRunning(false);
      }
    },
    [addLog]
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
      link.download = `employees_${new Date().toISOString().split('T')[0]}.csv`;
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
