import { useState } from "react";
import { Loader2, Play } from "lucide-react";

interface AutomationFormProps {
  onSubmit: (data: FormData) => void;
  isRunning: boolean;
}

export interface FormData {
  username: string;
  password: string;
  firstName: string;
  lastName: string;
  employeeId: string;
}

const AutomationForm = ({ onSubmit, isRunning }: AutomationFormProps) => {
  const [form, setForm] = useState<FormData>({
    username: "",
    password: "",
    firstName: "",
    lastName: "",
    employeeId: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isRunning) onSubmit(form);
  };

  const isValid =
    form.username.trim() &&
    form.password.trim() &&
    form.firstName.trim() &&
    form.lastName.trim() &&
    form.employeeId.trim();

  return (
    <div className="rounded-lg border border-border bg-card p-6">
      <h2 className="mb-5 text-lg font-semibold text-foreground">
        Automation Parameters
      </h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <fieldset className="space-y-4" disabled={isRunning}>
          <div className="grid grid-cols-2 gap-4">
            <InputField
              label="Username"
              name="username"
              value={form.username}
              onChange={handleChange}
              placeholder="Admin"
            />
            <InputField
              label="Password"
              name="password"
              type="password"
              value={form.password}
              onChange={handleChange}
              placeholder="••••••••"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <InputField
              label="First Name"
              name="firstName"
              value={form.firstName}
              onChange={handleChange}
              placeholder="John"
            />
            <InputField
              label="Last Name"
              name="lastName"
              value={form.lastName}
              onChange={handleChange}
              placeholder="Doe"
            />
          </div>
          <InputField
            label="Employee ID"
            name="employeeId"
            value={form.employeeId}
            onChange={handleChange}
            placeholder="EMP-0042"
          />
        </fieldset>

        <button
          type="submit"
          disabled={isRunning || !isValid}
          className="mt-2 flex w-full items-center justify-center gap-2 rounded-md bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isRunning ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Running…
            </>
          ) : (
            <>
              <Play className="h-4 w-4" />
              Trigger Automation
            </>
          )}
        </button>
      </form>
    </div>
  );
};

const InputField = ({
  label,
  name,
  value,
  onChange,
  type = "text",
  placeholder,
}: {
  label: string;
  name: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  type?: string;
  placeholder?: string;
}) => (
  <div className="space-y-1.5">
    <label htmlFor={name} className="block text-xs font-medium text-muted-foreground">
      {label}
    </label>
    <input
      id={name}
      name={name}
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      className="w-full rounded-md border border-border bg-secondary px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
    />
  </div>
);

export default AutomationForm;