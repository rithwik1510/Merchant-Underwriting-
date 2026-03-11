"use client";

import { useEffect, useState } from "react";
import { Loader2, RefreshCw, Save, ShieldCheck } from "lucide-react";
import { ApiError } from "@/lib/api/client";
import { probeLlmProvider } from "@/lib/api/communications";
import { getLlmSettings, updateLlmSettings } from "@/lib/api/settings";
import { LlmSettings } from "@/lib/types/settings";
import { cn } from "@/lib/utils";

type Provider = "lmstudio" | "claude";

export function LlmSettingsForm() {
  const [settings, setSettings] = useState<LlmSettings | null>(null);
  const [provider, setProvider] = useState<Provider>("lmstudio");
  const [lmstudioBaseUrl, setLmstudioBaseUrl] = useState("http://127.0.0.1:1234");
  const [lmstudioModel, setLmstudioModel] = useState("qwen/qwen3-8b");
  const [claudeModel, setClaudeModel] = useState("claude-sonnet-4-6");
  const [claudeBaseUrl, setClaudeBaseUrl] = useState("https://api.anthropic.com/v1");
  const [claudeApiKey, setClaudeApiKey] = useState("");
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [probing, setProbing] = useState(false);
  const [probeResult, setProbeResult] = useState<{ ok: boolean; status: string; model: string; latency_ms: number | null; error_detail: string | null } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const response = await getLlmSettings();
        setSettings(response);
        setProvider(response.provider);
        setLmstudioBaseUrl(response.lmstudio_base_url);
        setLmstudioModel(response.lmstudio_model);
        setClaudeModel(response.claude_model);
        setClaudeBaseUrl(response.claude_base_url);
      } catch (err) {
        setError(err instanceof ApiError ? err.detail : "Could not load LLM settings");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  async function handleSave() {
    setSaving(true);
    setError(null);
    setSuccess(null);
    try {
      const updated = await updateLlmSettings({
        provider,
        lmstudio_base_url: lmstudioBaseUrl,
        lmstudio_model: lmstudioModel,
        claude_model: claudeModel,
        claude_base_url: claudeBaseUrl,
        claude_api_key: claudeApiKey || undefined,
      });
      setSettings(updated);
      setProvider(updated.provider);
      setSuccess("Provider settings saved to backend environment.")
      setClaudeApiKey("");
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Could not save LLM settings");
    } finally {
      setSaving(false);
    }
  }

  async function handleProbe() {
    setProbing(true);
    setError(null);
    setSuccess(null);
    try {
      const result = await probeLlmProvider({
        provider,
        api_key_override: provider === "claude" ? claudeApiKey || undefined : undefined,
        model_override: provider === "claude" ? claudeModel : lmstudioModel,
      });
      setProbeResult(result);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Provider probe failed");
    } finally {
      setProbing(false);
    }
  }

  if (loading) {
    return (
      <div className="panel-card flex items-center gap-3 p-5 text-sm text-ink-500">
        <Loader2 className="h-4 w-4 animate-spin text-go-600" />
        Loading provider settings...
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="panel-card p-5">
        <div className="grid gap-4 lg:grid-cols-2">
          <ProviderButton
            title="LM Studio"
            description="Use your local model for explanations and WhatsApp drafts."
            active={provider === "lmstudio"}
            onClick={() => setProvider("lmstudio")}
          />
          <ProviderButton
            title="Claude"
            description="Use Anthropic Claude through the backend API key."
            active={provider === "claude"}
            onClick={() => setProvider("claude")}
          />
        </div>
      </div>

      <div className="panel-card p-5">
        <div className="mb-4 flex items-center gap-2 text-sm font-semibold text-ink-900">
          <ShieldCheck className="h-4 w-4 text-go-600" />
          Active provider configuration
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          <label className="space-y-2 text-sm text-ink-600">
            <span className="font-medium text-ink-900">LM Studio base URL</span>
            <input
              value={lmstudioBaseUrl}
              onChange={(event) => setLmstudioBaseUrl(event.target.value)}
              className="w-full rounded-2xl border border-ink-200 bg-white px-4 py-3 text-sm text-ink-900 focus:border-go-400 focus:outline-none"
            />
          </label>
          <label className="space-y-2 text-sm text-ink-600">
            <span className="font-medium text-ink-900">LM Studio model</span>
            <input
              value={lmstudioModel}
              onChange={(event) => setLmstudioModel(event.target.value)}
              className="w-full rounded-2xl border border-ink-200 bg-white px-4 py-3 text-sm text-ink-900 focus:border-go-400 focus:outline-none"
            />
          </label>
          <label className="space-y-2 text-sm text-ink-600">
            <span className="font-medium text-ink-900">Claude model</span>
            <input
              value={claudeModel}
              onChange={(event) => setClaudeModel(event.target.value)}
              className="w-full rounded-2xl border border-ink-200 bg-white px-4 py-3 text-sm text-ink-900 focus:border-go-400 focus:outline-none"
            />
          </label>
          <label className="space-y-2 text-sm text-ink-600">
            <span className="font-medium text-ink-900">Claude base URL</span>
            <input
              value={claudeBaseUrl}
              onChange={(event) => setClaudeBaseUrl(event.target.value)}
              className="w-full rounded-2xl border border-ink-200 bg-white px-4 py-3 text-sm text-ink-900 focus:border-go-400 focus:outline-none"
            />
          </label>
        </div>

        <label className="mt-4 block space-y-2 text-sm text-ink-600">
          <span className="font-medium text-ink-900">Claude API key</span>
          <input
            type="password"
            value={claudeApiKey}
            onChange={(event) => setClaudeApiKey(event.target.value)}
            placeholder={settings?.claude_api_key_configured ? `Stored key: ${settings.claude_api_key_masked}` : "sk-ant-..."}
            className="w-full rounded-2xl border border-ink-200 bg-white px-4 py-3 text-sm text-ink-900 placeholder:text-ink-400 focus:border-go-400 focus:outline-none"
          />
          <div className="text-xs text-ink-400">
            Saved to the backend environment. Leave blank to keep the existing stored key.
          </div>
        </label>

        <div className="mt-5 flex flex-wrap gap-3">
          <button onClick={handleSave} disabled={saving} className="btn-primary">
            {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
            Save settings
          </button>
          <button onClick={handleProbe} disabled={probing} className="btn-outline">
            {probing ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
            Probe active provider
          </button>
        </div>
      </div>

      {probeResult ? (
        <div className="panel-card p-5">
          <div className="flex flex-wrap items-center gap-2">
            <span
              className={cn(
                "status-pill",
                probeResult.ok ? "border-go-200 bg-go-50 text-go-700" : "border-risk-200 bg-risk-50 text-risk-700"
              )}
            >
              {probeResult.status}
            </span>
            <span className="status-pill border-ink-200 bg-white text-ink-500">{probeResult.model}</span>
            {probeResult.latency_ms != null ? (
              <span className="status-pill border-ink-200 bg-white text-ink-500">
                {probeResult.latency_ms} ms
              </span>
            ) : null}
          </div>
          {probeResult.error_detail ? (
            <div className="mt-3 text-sm text-ink-500">{probeResult.error_detail}</div>
          ) : null}
        </div>
      ) : null}

      {success ? (
        <div className="rounded-2xl border border-go-200 bg-go-50 px-4 py-3 text-sm text-go-700">{success}</div>
      ) : null}
      {error ? (
        <div className="rounded-2xl border border-risk-200 bg-risk-50 px-4 py-3 text-sm text-risk-700">{error}</div>
      ) : null}
    </div>
  );
}

function ProviderButton({
  title,
  description,
  active,
  onClick,
}: {
  title: string;
  description: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "rounded-2xl border px-4 py-4 text-left transition-all",
        active ? "border-go-300 bg-go-50 shadow-card" : "border-ink-100 bg-white hover:border-go-200"
      )}
    >
      <div className="text-sm font-semibold text-ink-900">{title}</div>
      <div className="mt-1 text-sm text-ink-500">{description}</div>
    </button>
  );
}
