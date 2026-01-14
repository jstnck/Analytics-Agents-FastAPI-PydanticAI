interface LogoProps {
  variant?: "full" | "icon" | "wordmark";
  size?: "sm" | "md" | "lg";
  className?: string;
}

export const Logo = ({ variant = "full", size = "md", className }: LogoProps) => {
  const sizes = {
    sm: { icon: 28, text: "text-lg", sub: "text-[9px]" },
    md: { icon: 40, text: "text-2xl", sub: "text-xs" },
    lg: { icon: 56, text: "text-4xl", sub: "text-sm" },
  };
  const currentSize = sizes[size];

  const IconMark = () => (
    <div className="relative float-animation" style={{ width: currentSize.icon, height: currentSize.icon }}>
      <svg viewBox="0 0 48 48" fill="none" className="w-full h-full">
        <defs>
          <linearGradient id="ballGradientFun" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="hsl(18 90% 60%)" />
            <stop offset="100%" stopColor="hsl(35 90% 55%)" />
          </linearGradient>
          <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="hsl(0 0% 100%)" stopOpacity="0.9" />
            <stop offset="100%" stopColor="hsl(0 0% 100%)" stopOpacity="0.7" />
          </linearGradient>
        </defs>
        <circle cx="24" cy="24" r="22" fill="url(#ballGradientFun)" />
        <path d="M24 2 L24 46" stroke="url(#lineGradient)" strokeWidth="2" strokeLinecap="round" />
        <path d="M2 24 L46 24" stroke="url(#lineGradient)" strokeWidth="2" strokeLinecap="round" />
        <path d="M6 12 Q24 20 42 12" stroke="url(#lineGradient)" strokeWidth="2" strokeLinecap="round" fill="none" />
        <path d="M6 36 Q24 28 42 36" stroke="url(#lineGradient)" strokeWidth="2" strokeLinecap="round" fill="none" />
        <circle cx="32" cy="16" r="4" fill="hsl(165 70% 45%)" />
        <circle cx="32" cy="16" r="2" fill="white" />
      </svg>
    </div>
  );

  if (variant === "icon") return <IconMark />;
  if (variant === "wordmark") return (
    <div className={`flex flex-col ${className || ""}`}>
      <span className={`font-display font-bold tracking-tight text-foreground ${currentSize.text}`}>HOOPTICS</span>
      <span className={`font-medium tracking-[0.3em] text-primary uppercase ${currentSize.sub}`}>Analytics</span>
    </div>
  );

  return (
    <div className={`flex items-center gap-3 ${className || ""}`}>
      <IconMark />
      <div className="flex flex-col">
        <span className={`font-display font-bold tracking-tight text-foreground leading-none ${currentSize.text}`}>HOOPTICS</span>
        <span className={`font-medium tracking-[0.25em] text-primary uppercase ${currentSize.sub}`}>Analytics</span>
      </div>
    </div>
  );
};
