export default function Card({ children, header, tag }) {
  return (
    <div className="card">
      {header || tag ? (
        <div className="card-header">
          {header ? <h3>{header}</h3> : null}
          {tag ? <span className="tag">{tag}</span> : null}
        </div>
      ) : null}
      {children}
    </div>
  );
}
