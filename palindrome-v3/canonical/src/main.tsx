import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import "./index.css"
import App from "./App.tsx"

/* Four routes, one page.
 *
 *   /      v3 — composed from verified mirror-pairs
 *   /dev   v3 — the URL it was shared under, kept working
 *   /v1    v1 — the search, which is what v3 has to be compared against
 *   /v2    v2 — placing whole attested sentences
 *
 * `App` covers all three: they arrive as the same Shape, so the grid, the
 * camera and clicking a word to find its mirror do not care which one they
 * are drawing. Which route is which is decided in App.tsx. */
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
