export default function ErrorMessage({ message, onRetry }) {
  return (
    <div className="alert alert-error">
      <strong>Error:</strong> {message}
      {onRetry ? (
        <Button variant="outline" className="btn-sm" onClick={onRetry} style={{ marginLeft: 12 }}>
          Retry
        </Button>
      ) : null}
    </div>
  );
}
