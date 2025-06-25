import { useState } from "react";
import { calculatePercentile } from "../services/percentileApi";

export default function TestApiConnection() {
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);

  const handleTest = async () => {
    setError(null);
    setResponse(null);
    try {
      const testData = {
        weight: 5.35,
        height: 56,
        date_birth: "2025-03-25",
        sex: "female",
        date_measurement: "2025-06-22",
      };

      const result = await calculatePercentile(testData);
      console.log("API response:", result);
      setResponse(result);
    } catch (err) {
      console.error("API error:", err.message);
      setError(err.message);
    }
  };

  return (
    <div className="p-6">
      <button
        onClick={handleTest}
        className="bg-blue-600 text-white px-4 py-2 rounded"
      >
        Test API Connection
      </button>

      {response && (
        <pre className="mt-4 bg-gray-100 p-2 rounded text-sm">
          {JSON.stringify(response, null, 2)}
        </pre>
      )}

      {error && (
        <div className="mt-4 text-red-600 font-semibold">Error: {error}</div>
      )}
    </div>
  );
}
