"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { motion } from "framer-motion";
import { CheckCircle2, CreditCard, Landmark, Loader2, Shield } from "lucide-react";
import { acceptOffer } from "@/lib/api/offers";
import { OfferAcceptanceResponse } from "@/lib/types/offers";
import { UnderwritingRun } from "@/lib/types/underwriting";
import { ApiError } from "@/lib/api/client";
import { formatDate } from "@/lib/utils/formatters";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { MandateWizard } from "@/components/mandate/MandateWizard";

interface AcceptanceFormProps {
  run: UnderwritingRun;
  existing?: OfferAcceptanceResponse | null;
  inline?: boolean;
}

const VIA_OPTIONS = [
  { value: "whatsapp", label: "WhatsApp" },
  { value: "email", label: "Email" },
  { value: "in_person", label: "In person" },
  { value: "phone_call", label: "Phone call" },
];

export function AcceptanceForm({ run, existing, inline = false }: AcceptanceFormProps) {
  const router = useRouter();
  const [showMandateModal, setShowMandateModal] = useState(false);
  const [product, setProduct] = useState<"credit" | "insurance">("credit");
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("+91");
  const [via, setVia] = useState("whatsapp");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<OfferAcceptanceResponse | null>(existing ?? null);

  const creditEligible = run.credit_offer?.offer_status === "eligible";
  const insuranceEligible = run.insurance_offer?.offer_status === "eligible";

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!name.trim() || phone === "+91") {
      setError("Name and phone number are required");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await acceptOffer(run.run_id, {
        accepted_product_type: product,
        accepted_by_name: name,
        accepted_phone: phone,
        accepted_via: via,
        acceptance_notes: notes || undefined,
      });
      setResult(response);
      router.refresh();
      if (inline && response.mandate_can_start) {
        setShowMandateModal(true);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Acceptance failed");
    } finally {
      setLoading(false);
    }
  }

  if (result) {
    return (
      <>
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          className="space-y-4 rounded-[28px] border border-go-200 bg-go-50 p-6 text-center"
        >
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full border border-go-200 bg-white">
            <CheckCircle2 className="h-6 w-6 text-go-600" />
          </div>
          <div>
            <div className="text-2xl font-bold tracking-tight text-ink-900">Offer accepted</div>
            <div className="mt-2 text-sm text-ink-500">
              {result.accepted_product_type.replace(/_/g, " ")} | {result.accepted_by_name} | {formatDate(result.accepted_at)}
            </div>
          </div>
          <div className="text-xs text-ink-500">
            Acceptance ID <span className="font-mono">{result.id}</span>
          </div>
          {result.mandate_can_start ? (
            inline ? (
              <button
                type="button"
                onClick={() => setShowMandateModal(true)}
                className="flex w-full items-center justify-center gap-2 rounded-2xl border border-go-200 bg-white px-4 py-3 text-sm font-medium text-go-700 transition-colors hover:border-go-300"
              >
                <Landmark className="h-4 w-4" />
                Continue to mandate setup
              </button>
            ) : (
              <Link href={`/runs/${run.run_id}/mandate`} className="btn-primary mx-auto">
                Proceed to NACH mandate
              </Link>
            )
          ) : null}
        </motion.div>

        {inline ? (
          <Dialog open={showMandateModal} onOpenChange={setShowMandateModal}>
            <DialogContent className="max-h-[92vh] w-[min(72rem,calc(100vw-3rem))] max-w-[calc(100vw-3rem)] sm:max-w-6xl overflow-y-auto rounded-[28px] border border-ink-100 bg-white p-0 shadow-[0_30px_80px_rgba(15,23,42,0.18)]">
              <DialogHeader className="border-b border-ink-100 px-6 py-5">
                <DialogTitle className="text-xl font-semibold text-ink-900">
                  Complete mandate setup
                </DialogTitle>
                <DialogDescription className="mt-1 text-sm text-ink-500">
                  Acceptance is recorded. Finish the bank, OTP, and UMRN flow now.
                </DialogDescription>
              </DialogHeader>
              <div className="px-6 py-6">
                <MandateWizard
                  runId={run.run_id}
                  onReset={() => {
                    setShowMandateModal(false);
                    setResult(null);
                  }}
                />
              </div>
            </DialogContent>
          </Dialog>
        ) : null}
      </>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div>
        <label className="mb-3 block text-xs font-semibold uppercase tracking-[0.18em] text-ink-400">
          Product to accept
        </label>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {[
            {
              value: "credit" as const,
              label: "GrabCredit",
              caption: creditEligible ? "Eligible" : "Not offered",
              eligible: creditEligible,
              icon: CreditCard,
            },
            {
              value: "insurance" as const,
              label: "GrabInsurance",
              caption: insuranceEligible ? "Eligible" : "Not offered",
              eligible: insuranceEligible,
              icon: Shield,
            },
          ].map((item) => {
            const Icon = item.icon;
            const active = item.eligible && product === item.value;
            return (
              <button
                key={item.value}
                type="button"
                onClick={() => item.eligible && setProduct(item.value)}
                disabled={!item.eligible}
                className={`rounded-[24px] border p-4 text-left transition-all ${
                  active
                    ? "border-go-300 bg-go-50 shadow-card"
                    : item.eligible
                    ? "border-ink-100 bg-white"
                    : "border-ink-100 bg-surface-50 opacity-50"
                }`}
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`flex h-10 w-10 items-center justify-center rounded-2xl border ${
                      active ? "border-go-200 bg-white text-go-600" : "border-ink-200 bg-surface-100 text-ink-500"
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-ink-900">{item.label}</div>
                    <div className="text-sm text-ink-500">{item.caption}</div>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label className="mb-1.5 block text-xs font-medium text-ink-500">Accepted by</label>
          <input
            required
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="Merchant contact name"
            className="w-full rounded-xl border border-ink-200 bg-white px-3 py-2.5 text-sm text-ink-900 placeholder:text-ink-300 focus:border-go-500 focus:outline-none"
          />
        </div>
        <div>
          <label className="mb-1.5 block text-xs font-medium text-ink-500">Phone number</label>
          <input
            required
            type="tel"
            value={phone}
            onChange={(event) => setPhone(event.target.value)}
            placeholder="+91XXXXXXXXXX"
            className="w-full rounded-xl border border-ink-200 bg-white px-3 py-2.5 font-mono text-sm text-ink-900 placeholder:text-ink-300 focus:border-go-500 focus:outline-none"
          />
        </div>
      </div>

      <div>
        <label className="mb-1.5 block text-xs font-medium text-ink-500">Accepted via</label>
        <select
          value={via}
          onChange={(event) => setVia(event.target.value)}
          className="w-full rounded-xl border border-ink-200 bg-white px-3 py-2.5 text-sm text-ink-900 focus:border-go-500 focus:outline-none"
        >
          {VIA_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="mb-1.5 block text-xs font-medium text-ink-500">Notes</label>
        <textarea
          value={notes}
          onChange={(event) => setNotes(event.target.value)}
          rows={3}
          placeholder="Optional notes for ops review"
          className="w-full resize-none rounded-xl border border-ink-200 bg-white px-3 py-2.5 text-sm text-ink-900 placeholder:text-ink-300 focus:border-go-500 focus:outline-none"
        />
      </div>

      {error ? <p className="text-xs text-risk-600">{error}</p> : null}

      <button type="submit" disabled={loading} className="btn-primary w-full justify-center">
        {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle2 className="h-4 w-4" />}
        Confirm acceptance
      </button>
    </form>
  );
}
