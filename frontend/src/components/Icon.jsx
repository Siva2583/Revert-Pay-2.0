function Icon({ name, size = 20, className = "" }) {
  const icons = {
    grid: <><rect x="3" y="3" width="7" height="7" rx="1.5" /><rect x="14" y="3" width="7" height="7" rx="1.5" /><rect x="3" y="14" width="7" height="7" rx="1.5" /><rect x="14" y="14" width="7" height="7" rx="1.5" /></>,
    wallet: <><path d="M3 7.5A2.5 2.5 0 0 1 5.5 5H19a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H5.5A2.5 2.5 0 0 1 3 17.5v-10Z" /><path d="M3 8h16a2 2 0 0 1 2 2v3h-5a2.5 2.5 0 0 0 0 5h5" /><path d="M16 15.5h.01" /></>,
    plus: <path d="M12 5v14M5 12h14" />,
    arrows: <path d="M7 7h12l-3-3m3 3-3 3m1 7H5l3 3m-3-3 3-3" />,
    book: <><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v17H6.5A2.5 2.5 0 0 0 4 22V5.5Z" /><path d="M4 20V5.5M8 7h8m-8 4h6" /></>,
    logout: <><path d="m10 17 5-5-5-5m5 5H3" /><path d="M13 5h5a3 3 0 0 1 3 3v8a3 3 0 0 1-3 3h-5" /></>,
    search: <><circle cx="10.8" cy="10.8" r="6.8" /><path d="m16 16 5 5" /></>,
    shield: <><path d="m12 3 8 3v5c0 5-3.4 8.8-8 10-4.6-1.2-8-5-8-10V6l8-3Z" /><path d="m8.5 12 2.2 2.2 4.8-5" /></>,
    package: <><path d="m12 3 8 4.5v9L12 21l-8-4.5v-9L12 3Z" /><path d="m4 7.5 8 4.5 8-4.5M12 12v9" /></>,
    activity: <path d="M3 12h4l2-6 4 12 2-6h6" />,
    chevron: <path d="m9 18 6-6-6-6" />,
    chevronDown: <path d="m6 9 6 6 6-6" />,
    arrowRight: <path d="M5 12h14m-5-5 5 5-5 5" />,
    arrowUpRight: <path d="M7 17 17 7M7 7h10v10" />,
    arrowDownLeft: <path d="M17 7 7 17m10 0H7V7" />,
    close: <path d="m6 6 12 12M18 6 6 18" />,
    menu: <path d="M4 7h16M4 12h16M4 17h16" />,
    check: <path d="m5 12 4 4L19 6" />,
    checkCircle: <><circle cx="12" cy="12" r="9" /><path d="m8 12 2.7 2.7L16.5 9" /></>,
    alert: <><path d="M10.3 4.1 2.8 17a2 2 0 0 0 1.7 3h15a2 2 0 0 0 1.7-3L13.7 4.1a2 2 0 0 0-3.4 0Z" /><path d="M12 9v4m0 3h.01" /></>,
    alertCircle: <><circle cx="12" cy="12" r="9" /><path d="M12 8v5m0 3h.01" /></>,
    info: <><circle cx="12" cy="12" r="9" /><path d="M12 11v6m0-10h.01" /></>,
    inbox: <><path d="M4 5h16l1 10v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4L4 5Z" /><path d="M3 15h5l2 2h4l2-2h5" /></>,
    refresh: <><path d="M20 7v5h-5" /><path d="M18.5 16a8 8 0 1 1 1.3-8.7L20 12" /></>,
    user: <><circle cx="12" cy="8" r="4" /><path d="M4 21a8 8 0 0 1 16 0" /></>,
    users: <><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8" /></>,
    lock: <><rect x="4" y="10" width="16" height="11" rx="2" /><path d="M8 10V7a4 4 0 0 1 8 0v3m-4 5v2" /></>,
    clock: <><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></>,
    calendar: <><rect x="3" y="5" width="18" height="16" rx="2" /><path d="M16 3v4M8 3v4M3 10h18" /></>,
    eye: <><path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z" /><circle cx="12" cy="12" r="2.5" /></>,
    eyeOff: <><path d="m3 3 18 18M10.6 6.1A10.8 10.8 0 0 1 12 6c6.5 0 10 6 10 6a17 17 0 0 1-2.1 2.8M6.3 6.3C3.4 8.2 2 12 2 12s3.5 6 10 6a10 10 0 0 0 4.1-.8M10 10a2.8 2.8 0 0 0 4 4" /></>,
    filter: <path d="M4 5h16l-6 7v6l-4 2v-8L4 5Z" />,
    copy: <><rect x="8" y="8" width="12" height="12" rx="2" /><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2" /></>,
  };

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      className={className}
    >
      {icons[name] || icons.info}
    </svg>
  );
}

export default Icon;
