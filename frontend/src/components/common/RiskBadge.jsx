export default function RiskBadge({ level, decision }) {
  const value = decision || level || "";
  const key = String(value).toUpperCase().replace(/\s+/g, "-");
  const className = `risk-badge risk-${key}`;
  return <span className={className}>{value}</span>;
}
