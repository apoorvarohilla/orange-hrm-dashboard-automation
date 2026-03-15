import { useEffect, useRef } from "react";
import { Terminal } from "lucide-react";

export interface LogEntry {
  message: string;
  type: "info" | "success" | "error" | "warning";
  timestamp: string;
}

interface StatusPanelProps {
  logs: LogEntry[];
  isRunning: boolean;
}

const typeColors: Record<LogEntry["type"], string> = {
  info: "text-muted-foreground",
  success: "text-green-600 dark:text-green-400",
  error: "text-red-600 dark:text-red-400",
  warning: "text-yellow-600 dark:text-yellow-400",
};

const StatusPanel = ({ logs, isRunning }: StatusPanelProps) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="flex h-full flex-col rounded-lg border border-border bg-card">
      <div className="flex items-center gap-2 border-b border-border px-4 py-3">
        <Terminal className="h-4 w-4 text-muted-foreground" />
        <h2 className="text-sm font-semibold text-foreground">Status</h2>
        {isRunning && (
          <span className="ml-auto inline-flex items-center gap-1.5 text-xs text-primary">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-primary" />
            Running
          </span>
        )}
      </div>
      <div
        ref={scrollRef}
        className="min-h-[280px] flex-1 overflow-y-auto p-4 font-mono text-xs leading-relaxed"
      >
        {logs.length === 0 ? (
          <p className="text-muted-foreground">Waiting for automation to start…</p>
        ) : (
          logs.map((log, i) => (
            <div key={`${log.timestamp}-${i}`} className="py-0.5">
              <span className="text-muted-foreground/60">[{log.timestamp}]</span>{" "}
              <span className={typeColors[log.type]}>{log.message}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default StatusPanel;