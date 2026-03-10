export type MandateStatus =
  | "initiated"
  | "bank_selected"
  | "otp_sent"
  | "otp_verified"
  | "umrn_generated"
  | "completed"
  | "failed";

export interface MandateSession {
  id: number;
  run_id: number;
  acceptance_id: number;
  accepted_product_type: string;
  mandate_status: MandateStatus;
  account_holder_name: string;
  bank_name: string | null;
  account_number_masked: string | null;
  ifsc_masked: string | null;
  mobile_number_masked: string;
  otp_attempt_count: number;
  remaining_attempts: number;
  umrn: string | null;
  mandate_reference: string | null;
  failure_reason: string | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
  demo_otp: string | null;
}
