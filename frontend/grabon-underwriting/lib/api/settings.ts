import { apiFetch } from "./client";
import { LlmSettings, LlmSettingsUpdateRequest } from "../types/settings";

export const getLlmSettings = () => apiFetch<LlmSettings>("/llm/settings");

export const updateLlmSettings = (body: LlmSettingsUpdateRequest) =>
  apiFetch<LlmSettings>("/llm/settings", {
    method: "PUT",
    body: JSON.stringify(body),
  });
