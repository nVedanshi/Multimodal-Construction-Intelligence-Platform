export default function Button({ children, variant = "primary", disabled, onClick, className }) {
  return (
    <button
      className={`btn btn-${variant} ${className || ""}`}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
