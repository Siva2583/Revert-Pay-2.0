function LogoMark({ size = 40 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      role="img"
      aria-label="RevertPay"
    >
      <rect width="100" height="100" rx="24" fill="#123B31" />
      <path
        d="M27 35a27 27 0 0 1 44-8l5 6"
        stroke="#75E2BF"
        strokeWidth="7"
        strokeLinecap="round"
      />
      <path d="m77 20-1 13-13-1" stroke="#75E2BF" strokeWidth="7" strokeLinecap="round" strokeLinejoin="round" />
      <path
        d="M73 65a27 27 0 0 1-44 8l-5-6"
        stroke="#F4F8F5"
        strokeWidth="7"
        strokeLinecap="round"
      />
      <path d="m23 80 1-13 13 1" stroke="#F4F8F5" strokeWidth="7" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="50" cy="50" r="8" fill="#75E2BF" />
      <circle cx="50" cy="50" r="3" fill="#123B31" />
    </svg>
  );
}

function LogoMarkCompact({ size = 24 }) {
  return <LogoMark size={size} />;
}

function Logo({
  size = 40,
  variant = "mark",
  withWordmark = false,
  light = false,
}) {
  const Mark = variant === "compact" ? LogoMarkCompact : LogoMark;

  if (!withWordmark) {
    return <Mark size={size} />;
  }

  return (
    <div className="logo-lockup">
      <Mark size={size} />
      <span
        className="logo-wordmark"
        style={{ color: light ? "#ffffff" : "#18231f" }}
      >
        RevertPay
      </span>
    </div>
  );
}

export default Logo;
export { LogoMark, LogoMarkCompact };
