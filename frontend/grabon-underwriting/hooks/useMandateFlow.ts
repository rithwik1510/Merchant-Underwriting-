"use client";

import { useState, useCallback } from "react";
import { MandateSession } from "@/lib/types/mandates";
import {
  startMandate,
  selectBank,
  sendOtp,
  verifyOtp,
  completeMandate,
  getMandateStatus,
} from "@/lib/api/mandates";
import { ApiError } from "@/lib/api/client";

export type MandateStep = 0 | 1 | 2 | 3 | 4;

const STATUS_TO_STEP: Record<string, MandateStep> = {
  initiated: 1,
  bank_selected: 2,
  otp_sent: 3,
  otp_verified: 4,
  umrn_generated: 4,
  completed: 4,
  failed: 3,
};

export function useMandateFlow(runId: number | string) {
  const [step, setStep] = useState<MandateStep>(0);
  const [session, setSession] = useState<MandateSession | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleApi = useCallback(
    async (fn: () => Promise<MandateSession>) => {
      setIsLoading(true);
      setError(null);
      try {
        const result = await fn();
        setSession(result);
        const nextStep = STATUS_TO_STEP[result.mandate_status];
        if (nextStep !== undefined) setStep(nextStep);
        return result;
      } catch (e) {
        const msg = e instanceof ApiError ? e.detail : "Something went wrong";
        setError(msg);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const initFromExisting = useCallback(async () => {
    try {
      const existing = await getMandateStatus(runId);
      setSession(existing);
      const step = STATUS_TO_STEP[existing.mandate_status] ?? 4;
      setStep(step);
    } catch {
      // no existing mandate — stay at step 0
    }
  }, [runId]);

  const doStart = (body: { account_holder_name: string; mobile_number: string }) =>
    handleApi(() => startMandate(runId, body));

  const doSelectBank = (body: {
    bank_name: string;
    account_number: string;
    ifsc_code: string;
  }) => handleApi(() => selectBank(runId, body));

  const doSendOtp = () => handleApi(() => sendOtp(runId));

  const doVerifyOtp = (otp: string) =>
    handleApi(() => verifyOtp(runId, { otp }));

  const doComplete = () => handleApi(() => completeMandate(runId));

  return {
    step,
    session,
    isLoading,
    error,
    setError,
    initFromExisting,
    doStart,
    doSelectBank,
    doSendOtp,
    doVerifyOtp,
    doComplete,
  };
}
