import Icon from "./Icon";
import { formatStatus } from "../utils/formatters";

export default function EscrowFilters({
  search,
  onSearchChange,
  status,
  onStatusChange,
  statuses,
  resultCount,
  totalCount,
  searchLabel = "Search escrows",
}) {
  return (
    <div className="list-toolbar">
      <div className="search-control">
        <Icon name="search" size={17} />
        <input
          type="search"
          value={search}
          onChange={(event) => onSearchChange(event.target.value)}
          placeholder="Search by item, person, or escrow ID"
          aria-label={searchLabel}
        />
      </div>
      <label className="filter-control">
        <Icon name="filter" size={16} />
        <span className="sr-only">Filter escrows by status</span>
        <select value={status} onChange={(event) => onStatusChange(event.target.value)}>
          <option value="ALL">All statuses</option>
          {statuses.map((item) => (
            <option value={item} key={item}>{formatStatus(item)}</option>
          ))}
        </select>
      </label>
      <span className="list-result-count" aria-live="polite">
        {resultCount} of {totalCount}
      </span>
    </div>
  );
}
