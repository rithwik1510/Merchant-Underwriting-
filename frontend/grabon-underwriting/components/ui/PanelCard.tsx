import { cn } from "@/lib/utils";

interface PanelCardProps extends React.HTMLAttributes<HTMLDivElement> {
  subtle?: boolean;
}

export function PanelCard({
  className,
  subtle = false,
  ...props
}: PanelCardProps) {
  return (
    <div
      className={cn(subtle ? "panel-card-muted" : "panel-card", className)}
      {...props}
    />
  );
}
