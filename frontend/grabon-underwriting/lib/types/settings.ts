export interface LlmSettings {
  provider: "lmstudio" | "claude";
  lmstudio_base_url: string;
  lmstudio_model: string;
  claude_model: string;
  claude_base_url: string;
  claude_api_key_configured: boolean;
  claude_api_key_masked: string | null;
}

export interface LlmSettingsUpdateRequest {
  provider: "lmstudio" | "claude";
  lmstudio_base_url?: string;
  lmstudio_model?: string;
  claude_model?: string;
  claude_base_url?: string;
  claude_api_key?: string;
}
