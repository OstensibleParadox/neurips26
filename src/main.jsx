import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import PipelineTracker from "../pipeline_tracker.jsx";

// shim window.storage → localStorage (mirrors Claude artifact API)
window.storage = {
  get: (key) => Promise.resolve({ value: localStorage.getItem(key) }),
  set: (key, val) => { localStorage.setItem(key, val); return Promise.resolve(); },
  delete: (key) => { localStorage.removeItem(key); return Promise.resolve(); },
};

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <PipelineTracker />
  </StrictMode>
);
