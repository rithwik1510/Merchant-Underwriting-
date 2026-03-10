export interface OfferAcceptanceRequest {
  accepted_product_type: string;
  accepted_by_name: string;
  accepted_phone: string;
  accepted_via: string;
  acceptance_notes?: string;
}

export interface OfferAcceptanceResponse {
  id: number;
  run_id: number;
  accepted_product_type: string;
  accepted_by_name: string;
  accepted_phone: string;
  accepted_via: string;
  accepted_at: string;
  acceptance_notes: string | null;
  mandate_can_start: boolean;
}

export interface Phase4ResetResponse {
  run_id: number;
  reset: boolean;
}
