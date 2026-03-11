import { LlmSettingsForm } from "@/components/settings/LlmSettingsForm";

export const dynamic = "force-dynamic";

export default function SettingsPage() {
  return (
    <div className="space-y-6 px-6 py-6">
      <div>
        <div className="text-sm font-semibold uppercase tracking-[0.18em] text-go-600">
          Provider control
        </div>
        <h1 className="mt-2 text-3xl font-bold tracking-tight text-ink-900">LLM Settings</h1>
        <p className="mt-2 max-w-2xl text-sm text-ink-500">
          Switch between LM Studio and Claude, store the Claude API key in the backend environment,
          and probe the active provider before generating explanations or WhatsApp drafts.
        </p>
      </div>

      <LlmSettingsForm />
    </div>
  );
}
