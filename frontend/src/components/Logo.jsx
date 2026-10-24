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
      <rect width="100" height="100" rx="26" fill="#151B17" />
      <rect x="1" y="1" width="98" height="98" rx="25" stroke="#FFFFFF" strokeOpacity="0.1" />
      <path
        d="M31 74V26h19c13 0 21 7 21 17s-8 17-21 17H31"
        stroke="#A9CDB7"
        strokeWidth="10"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path d="M49 60 69 77" stroke="#E2C699" strokeWidth="10" strokeLinecap="round" />
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
        style={{ color: light ? "#f5f1e8" : "#1d231f" }}
      >
        RevertPay
      </span>
    </div>
  );
}

export default Logo;
export { LogoMark, LogoMarkCompact };
