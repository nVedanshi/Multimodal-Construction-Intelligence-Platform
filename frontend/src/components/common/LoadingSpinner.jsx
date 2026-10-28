export default function LoadingSpinner({ text = "Analyzing..." }) {
  return (
    <div className="loader">
      <div className="spinner"></div>
      {text}
    </div>
  );
}
