export interface Employee {
  id: string;
  firstName: string;
  lastName: string;
  status: string;
}

interface EmployeeTableProps {
  employees: Employee[];
}

const EmployeeTable = ({ employees }: EmployeeTableProps) => {
  if (employees.length === 0) return null;

  return (
    <div className="rounded-lg border border-border bg-card">
      <div className="border-b border-border px-4 py-3">
        <h2 className="text-sm font-semibold text-foreground">
          Extracted Employee Data ({employees.length} total)
        </h2>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left font-mono text-xs">
          <thead>
            <tr className="border-b border-border text-muted-foreground">
              <th className="px-4 py-2.5 font-medium">#</th>
              <th className="px-4 py-2.5 font-medium">Employee ID</th>
              <th className="px-4 py-2.5 font-medium">First Name</th>
              <th className="px-4 py-2.5 font-medium">Last Name</th>
              <th className="px-4 py-2.5 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {employees.map((emp, i) => (
              <tr
                key={emp.id}
                className="border-b border-border last:border-0 transition-colors hover:bg-muted/40"
              >
                <td className="px-4 py-2.5 text-muted-foreground">{i + 1}</td>
                <td className="px-4 py-2.5 text-foreground font-semibold">{emp.id}</td>
                <td className="px-4 py-2.5 text-foreground">{emp.firstName}</td>
                <td className="px-4 py-2.5 text-foreground">{emp.lastName}</td>
                <td className="px-4 py-2.5">
                  <span className="inline-flex rounded-full bg-green-100 px-2 py-0.5 text-[10px] font-medium text-green-800">
                    {emp.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default EmployeeTable;
