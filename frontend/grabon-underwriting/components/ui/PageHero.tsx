import { cn } from "@/lib/utils";

interface PageHeroProps {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: React.ReactNode;
  meta?: React.ReactNode;
  className?: string;
}

export function PageHero({
  eyebrow,
  title,
  description,
  actions,
  meta,
  className,
}: PageHeroProps) {
  return (
    <div className={cn("rounded-3xl border border-ink-200 bg-ink-50 p-6 md:p-7 border-l-[3px] border-l-go-600", className)}>
      <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
        <div className="space-y-3">
          {eyebrow ? (
            <div className="status-pill border-go-200 bg-go-100 text-go-700">
              {eyebrow}
            </div>
          ) : null}
          <div>
            <h1 className="max-w-3xl text-balance text-3xl font-bold tracking-tight text-ink-900 md:text-4xl">
              {title}
            </h1>
            {description ? (
              <p className="mt-2 max-w-3xl text-sm leading-6 text-ink-500 md:text-base">
                {description}
              </p>
            ) : null}
          </div>
          {meta ? <div className="flex flex-wrap gap-2">{meta}</div> : null}
        </div>
        {actions ? <div className="flex flex-wrap items-center gap-3">{actions}</div> : null}
      </div>
    </div>
  );
}
