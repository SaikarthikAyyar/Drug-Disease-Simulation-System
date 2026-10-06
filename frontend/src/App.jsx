import { useState} from 'react'
import "./App.css"

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8001"

// Aspirin — a convenient default so the page is testable in one click.
const Example_SMILES = "CC(=O)Oc1ccccc1C(=O)O"

const DESCRIPTOR_LABELS = {
  molecular_weight: "Molecular Weight",
  logp: "LogP",
  h_bond_donors: "H-Bond Donors",
  h_bond_acceptors: "H-Bond Acceptors",
  tpsa: "TPSA",
  rotatable_bonds: "Rotatable Bonds",
  aromatic_rings: "Aromatic Rings",
};

export default function App() {
  const [smiles, setSmiles] = useState(Example_SMILES);
  const [results, setResults] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResults(null);

    try {
      const response = await fetch(`${API_URL}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json"}, body: JSON.stringify({ smiles})
      });

      if (!response.ok) {
        // The API returns a readable message; fall back if the shape is unexpected.
        const body = await response.json().catch(() => ({}));
        const detail = body.detail;
        throw new Error(
          typeof detail === "string" ? detail : "Molecule could not be proceessed."
        );
      }
      setResults(await response.json());
    } catch (err) {
      // A failed fetch usually means the free-tier service is still waking up.
      setError(
        err instanceof TypeError
          ? "The API is not responding. Please wait and try again later."
          : err.message
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page">
      <h1>Drug Disease Simulation System</h1>
      <p className="subtitle">Enter a molecule's SMILES notation to predict its properties.</p>

      <form onSubmit={handleSubmit}>
        <label htmlFor="smiles">SMILES</label>
        <input
          id="smiles"
          value={smiles}
          onChange={(event) => setSmiles(event.target.value)}
          placeholder={Example_SMILES}
          autoComplete="off"
        />
        <button type="submit" disabled={loading || !smiles.trim()}>{loading ? "Analyzing..." : "Analyze"}</button>
      </form>

      {error && <p className="error">{error}</p>}

      {results && (
        <section className="results">
          <h2>Descriptors</h2>
          <p className="canonical">Canonical SMILES: <code>{results.canonical_smiles}</code></p>
          <table>
            <tbody>
              {Object.entries(results.descriptors).map(([key, value]) => (
                <tr key={key}>
                  <th scope="row">{DESCRIPTOR_LABELS[key] ?? key}</th>
                  <td>{Number(value).toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="model-note">Model: {results.model}</p>
        </section>
      )}
    </main>
  );
}