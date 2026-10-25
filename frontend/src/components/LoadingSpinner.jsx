export function Spinner({ size = 20, label = "Loading" }) {
  return (
    <span
      className="spinner"
      style={{ width: size, height: size }}
      role="status"
      aria-label={label}
    />
  );
}

export function Skeleton({ className = "", width, height }) {
  return (
    <span
      className={`skeleton ${className}`.trim()}
      style={{ width, height }}
      aria-hidden="true"
    />
  );
}

export function MetricsSkeleton({ count = 4 }) {
  return (
    <div className="metrics-grid" aria-hidden="true">
      {Array.from({ length: count }, (_, index) => (
        <div className="metric-card" key={index}>
          <Skeleton width="42%" height={12} />
          <Skeleton width="70%" height={28} />
          <Skeleton width="52%" height={11} />
        </div>
      ))}
    </div>
  );
}

export function TableSkeleton({ rows = 5 }) {
  return (
    <div className="table-skeleton" role="status" aria-label="Loading records">
      <div className="skeleton-table-head">
        <Skeleton width="18%" />
        <Skeleton width="22%" />
        <Skeleton width="24%" />
        <Skeleton width="16%" />
      </div>
      {Array.from({ length: rows }, (_, index) => (
        <div className="skeleton-table-row" key={index}>
          <Skeleton width="72%" />
          <Skeleton width="62%" />
          <Skeleton width="80%" />
          <Skeleton width="68%" />
        </div>
      ))}
    </div>
  );
}

export function PageSkeleton({ metrics = 4, rows = 4 }) {
  return (
    <div className="page-stack" aria-busy="true">
      <span className="sr-only">Loading page content</span>
      <div className="skeleton-heading" aria-hidden="true">
        <div>
          <Skeleton width={150} height={12} />
          <Skeleton width={280} height={28} />
        </div>
        <Skeleton width={110} height={40} />
      </div>
      <MetricsSkeleton count={metrics} />
      <div className="surface-card">
        <TableSkeleton rows={rows} />
      </div>
    </div>
  );
}

export function EscrowListSkeleton() {
  return (
    <div className="page-stack" aria-busy="true">
      <span className="sr-only">Loading escrow records</span>
      <MetricsSkeleton count={4} />
      {Array.from({ length: 3 }, (_, index) => (
        <div className="escrow-card escrow-skeleton" key={index} aria-hidden="true">
          <div className="escrow-card-header">
            <div>
              <Skeleton width={100} height={11} />
              <Skeleton width={220} height={24} />
            </div>
            <Skeleton width={110} height={28} />
          </div>
          <div className="escrow-skeleton-body">
            <Skeleton width="22%" height={34} />
            <Skeleton width="28%" height={34} />
            <Skeleton width="24%" height={34} />
          </div>
          <Skeleton width="100%" height={52} />
        </div>
      ))}
    </div>
  );
}
