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
      <rect width="100" height="100" rx="24" fill="#0A0D0B" />
      <rect
        x="1"
        y="1"
        width="98"
        height="98"
        rx="23"
        stroke="#343B35"
      />
      <path
        d="M46 23H35L23 35v30l12 12h11"
        stroke="#00C833"
        strokeWidth="7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M54 23h11l12 12v30L65 77H54"
        stroke="#F5F5F0"
        strokeWidth="7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="m50 36 14 14-14 14-14-14 14-14Z"
        fill="#0A0D0B"
        stroke="#C9A227"
        strokeWidth="6"
        strokeLinejoin="round"
      />
      <path
        d="M43 50h14"
        stroke="#C9A227"
        strokeWidth="4"
        strokeLinecap="round"
      />
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
        style={{ color: light ? "#F5F5F0" : "#E9EDE9" }}
      >
        RevertPay
      </span>
    </div>
  );
}

export default Logo;
export { LogoMark, LogoMarkCompact };
