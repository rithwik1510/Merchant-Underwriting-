"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import {
  Building2,
  CheckCircle2,
  Landmark,
  Loader2,
  MessageSquareLock,
  ShieldCheck,
  UserRound,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useMandateFlow, MandateStep } from "@/hooks/useMandateFlow";
import { resetPhase4Demo } from "@/lib/api/offers";
import { ApiError } from "@/lib/api/client";

interface MandateWizardProps {
  runId: number;
  onReset?: () => void;
}

const STEPS = [
  { label: "Start", icon: UserRound },
  { label: "Bank", icon: Building2 },
  { label: "OTP", icon: MessageSquareLock },
  { label: "Verify", icon: ShieldCheck },
  { label: "UMRN", icon: Landmark },
];

const BANKS = [
  "State Bank of India",
  "HDFC Bank",
  "ICICI Bank",
  "Axis Bank",
  "Kotak Mahindra Bank",
  "Yes Bank",
  "Punjab National Bank",
  "Bank of Baroda",
];

function StepRail({ currentStep }: { currentStep: MandateStep }) {
  return (
    <div className="grid grid-cols-1 gap-3 lg:grid-cols-5">
      {STEPS.map((step, index) => {
        const Icon = step.icon;
        const active = index === currentStep;
        const done = index < currentStep;

        return (
          <div
            key={step.label}
            className={cn(
              "rounded-2xl border p-4 transition-all lg:min-h-[96px]",
              done
                ? "border-go-200 bg-go-50"
                : active
                ? "border-go-300 bg-white shadow-card"
                : "border-ink-100 bg-surface-50"
            )}
          >
            <div className="flex items-center gap-3">
              <div
                className={cn(
                  "flex h-10 w-10 items-center justify-center rounded-2xl border",
                  done
                    ? "border-go-200 bg-white text-go-600"
                    : active
                    ? "border-go-200 bg-go-50 text-go-600"
                    : "border-ink-200 bg-white text-ink-400"
                )}
              >
                {done ? <CheckCircle2 className="h-4 w-4" /> : <Icon className="h-4 w-4" />}
              </div>
              <div className="min-w-0">
                <div className="text-xs font-semibold uppercase tracking-[0.18em] text-ink-400">
                  Step {index + 1}
                </div>
                <div className="text-sm font-semibold text-ink-900">{step.label}</div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function FieldLabel({ children }: { children: React.ReactNode }) {
  return <label className="mb-1.5 block text-xs font-medium text-ink-500">{children}</label>;
}

function TextInput({
  value,
  onChange,
  placeholder,
  mono = false,
  maxLength,
  type = "text",
}: {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  mono?: boolean;
  maxLength?: number;
  type?: string;
}) {
  return (
    <input
      type={type}
      value={value}
      onChange={(event) => onChange(event.target.value)}
      placeholder={placeholder}
      maxLength={maxLength}
      className={cn(
        "w-full rounded-xl border border-ink-200 bg-white px-3 py-2.5 text-sm text-ink-900 placeholder:text-ink-300 focus:border-go-500 focus:outline-none",
        mono && "font-mono"
      )}
    />
  );
}

function SubmitButton({
  label,
  loading,
  variant = "primary",
}: {
  label: string;
  loading: boolean;
  variant?: "primary" | "success";
}) {
  return (
    <button
      type="submit"
      disabled={loading}
      className={cn(
        "flex w-full items-center justify-center gap-2 rounded-xl py-3 text-sm font-semibold transition-all disabled:opacity-70",
        variant === "success" ? "bg-go-600 text-white hover:bg-go-700" : "bg-ink-900 text-white hover:bg-ink-800"
      )}
    >
      {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
      {loading ? "Processing..." : label}
    </button>
  );
}

function Step0({ flow }: { flow: ReturnType<typeof useMandateFlow> }) {
  const [holderName, setHolderName] = useState("");
  const [mobile, setMobile] = useState("+91");

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    flow.doStart({ account_holder_name: holderName, mobile_number: mobile });
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <p className="text-sm text-ink-500">Start the mandate session using the account holder and mobile number that will receive the OTP.</p>
      <div>
        <FieldLabel>Account holder name</FieldLabel>
        <TextInput value={holderName} onChange={setHolderName} placeholder="Full name as per bank records" />
      </div>
      <div>
        <FieldLabel>Mobile number</FieldLabel>
        <TextInput value={mobile} onChange={setMobile} placeholder="+91XXXXXXXXXX" mono />
      </div>
      <SubmitButton label="Initiate mandate" loading={flow.isLoading} />
    </form>
  );
}

function Step1({ flow }: { flow: ReturnType<typeof useMandateFlow> }) {
  const [bank, setBank] = useState("");
  const [account, setAccount] = useState("");
  const [ifsc, setIfsc] = useState("");

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    flow.doSelectBank({ bank_name: bank, account_number: account, ifsc_code: ifsc });
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="rounded-2xl border border-ink-100 bg-surface-50 p-4 text-sm text-ink-600">
        Account holder <span className="font-semibold text-ink-900">{flow.session?.account_holder_name}</span>
      </div>
      <div>
        <FieldLabel>Bank name</FieldLabel>
        <select
          value={bank}
          onChange={(event) => setBank(event.target.value)}
          className="w-full rounded-xl border border-ink-200 bg-white px-3 py-2.5 text-sm text-ink-900 focus:border-go-500 focus:outline-none"
        >
          <option value="">Select bank...</option>
          {BANKS.map((bankName) => (
            <option key={bankName} value={bankName}>
              {bankName}
            </option>
          ))}
        </select>
      </div>
      <div>
        <FieldLabel>Account number</FieldLabel>
        <TextInput value={account} onChange={setAccount} placeholder="XXXXXXXXXXXX" mono />
      </div>
      <div>
        <FieldLabel>IFSC code</FieldLabel>
        <TextInput value={ifsc} onChange={setIfsc} placeholder="SBIN0000001" mono />
      </div>
      <SubmitButton label="Save bank details" loading={flow.isLoading} />
    </form>
  );
}

function Step2({ flow }: { flow: ReturnType<typeof useMandateFlow> }) {
  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    flow.doSendOtp();
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="rounded-2xl border border-ink-100 bg-surface-50 p-4">
        {[
          ["Bank", flow.session?.bank_name],
          ["Account", flow.session?.account_number_masked],
          ["IFSC", flow.session?.ifsc_masked],
          ["Mobile", flow.session?.mobile_number_masked],
        ].map(([label, value]) => (
          <div key={label} className="flex justify-between border-b border-ink-100 py-2 text-sm last:border-b-0">
            <span className="text-ink-500">{label}</span>
            <span className="font-mono text-ink-800">{value ?? "-"}</span>
          </div>
        ))}
      </div>
      <p className="text-sm text-ink-500">Send an OTP to the masked mobile number to continue the mock NACH process.</p>
      <SubmitButton label="Send OTP" loading={flow.isLoading} />
    </form>
  );
}

function Step3({ flow }: { flow: ReturnType<typeof useMandateFlow> }) {
  const [otp, setOtp] = useState("");

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    flow.doVerifyOtp(otp);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {flow.session?.demo_otp ? (
        <div className="rounded-2xl border border-go-200 bg-go-50 px-4 py-4">
          <div className="text-xs font-semibold uppercase tracking-[0.18em] text-go-700">Demo OTP</div>
          <div className="mt-2 font-mono text-3xl font-bold tracking-[0.28em] text-go-800">
            {flow.session.demo_otp}
          </div>
        </div>
      ) : null}
      <div>
        <FieldLabel>Enter OTP ({flow.session?.remaining_attempts ?? 3} attempts remaining)</FieldLabel>
        <input
          type="text"
          value={otp}
          onChange={(event) => setOtp(event.target.value)}
          maxLength={6}
          placeholder="000000"
          className="w-full rounded-2xl border border-ink-200 bg-white px-4 py-3 text-center font-mono text-2xl font-bold tracking-[0.35em] text-ink-900 placeholder:text-ink-300 focus:border-go-500 focus:outline-none"
        />
      </div>
      <SubmitButton label="Verify OTP" loading={flow.isLoading} />
    </form>
  );
}

function Step4({
  flow,
  runId,
  onReset,
}: {
  flow: ReturnType<typeof useMandateFlow>;
  runId: number;
  onReset?: () => void;
}) {
  const router = useRouter();

  async function handleReset() {
    flow.setError(null);
    try {
      await resetPhase4Demo(runId);
      router.refresh();
      onReset?.();
    } catch (error) {
      flow.setError(error instanceof ApiError ? error.detail : "Unable to reset demo flow");
    }
  }

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    flow.doComplete();
  }

  if (flow.session?.umrn) {
    return (
      <div className="space-y-5 text-center">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full border border-go-200 bg-go-50">
          <CheckCircle2 className="h-7 w-7 text-go-600" />
        </div>
        <div>
          <div className="text-2xl font-bold tracking-tight text-ink-900">Mandate registered</div>
          <div className="mt-1 text-sm text-ink-500">The mock NACH flow completed successfully.</div>
        </div>
        <div className="rounded-2xl border border-ink-100 bg-surface-50 p-4 text-left">
          <div className="flex justify-between py-2 text-sm">
            <span className="text-ink-500">UMRN</span>
            <span className="font-mono text-go-700">{flow.session.umrn}</span>
          </div>
          <div className="flex justify-between py-2 text-sm">
            <span className="text-ink-500">Reference</span>
            <span className="font-mono text-ink-700">{flow.session.mandate_reference}</span>
          </div>
        </div>
        <button
          type="button"
          onClick={handleReset}
          className="w-full rounded-xl border border-ink-200 bg-white py-3 text-sm font-semibold text-ink-700 transition-colors hover:border-go-300 hover:text-go-700"
        >
          Reset demo flow
        </button>
      </div>
    );
  }

  if (flow.session?.mandate_status === "failed") {
    return (
      <div className="space-y-4">
        <div className="rounded-2xl border border-risk-200 bg-risk-50 p-4 text-sm text-risk-700">
          {flow.session.failure_reason ?? "The mandate flow failed."}
        </div>
        <button
          type="button"
          onClick={handleReset}
          className="w-full rounded-xl border border-ink-200 bg-white py-3 text-sm font-semibold text-ink-700 transition-colors hover:border-go-300 hover:text-go-700"
        >
          Reset and try again
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <p className="text-sm text-ink-500">OTP is verified. Complete the mandate to generate UMRN and lock the mandate record.</p>
      <SubmitButton label="Complete and generate UMRN" loading={flow.isLoading} variant="success" />
    </form>
  );
}

const STEP_COMPONENTS: Record<0 | 1 | 2 | 3, ({ flow }: { flow: ReturnType<typeof useMandateFlow> }) => JSX.Element> = {
  0: Step0,
  1: Step1,
  2: Step2,
  3: Step3,
};

export function MandateWizard({ runId, onReset }: MandateWizardProps) {
  const flow = useMandateFlow(runId);

  useEffect(() => {
    flow.initFromExisting();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [runId]);

  const StepComponent = flow.step === 4 ? Step0 : STEP_COMPONENTS[flow.step];

  return (
    <div className="space-y-5">
      <StepRail currentStep={flow.step} />

      <div className="panel-card min-h-[300px] p-6">
        <AnimatePresence mode="wait">
          <motion.div
            key={flow.step}
            initial={{ opacity: 0, x: 24 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -24 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
          >
            {flow.step === 4 ? <Step4 flow={flow} runId={runId} onReset={onReset} /> : <StepComponent flow={flow} />}
          </motion.div>
        </AnimatePresence>
      </div>

      {flow.error ? (
        <div className="rounded-2xl border border-risk-200 bg-risk-50 px-4 py-3 text-sm text-risk-700">
          {flow.error}
        </div>
      ) : null}
    </div>
  );
}
