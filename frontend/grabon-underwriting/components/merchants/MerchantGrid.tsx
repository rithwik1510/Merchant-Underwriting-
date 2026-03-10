import { MerchantSummary } from "@/lib/types/merchant";
import { MerchantCard } from "./MerchantCard";

interface MerchantGridProps {
  merchants: MerchantSummary[];
}

export function MerchantGrid({ merchants }: MerchantGridProps) {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
      {merchants.map((m, i) => (
        <MerchantCard key={m.merchant_id} merchant={m} index={i} />
      ))}
    </div>
  );
}
