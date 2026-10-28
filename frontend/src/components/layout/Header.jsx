export default function Header({ title, modeLabel }) {
  return (
    <header className="header">
      <h1>{title}</h1>
      <div className="status">
        {modeLabel ? (
          <>
            <span className="mode-tag {modeLabel}">{modeLabel}</span>
          </>
        ) : null}
      </div>
    </header>
  );
}
