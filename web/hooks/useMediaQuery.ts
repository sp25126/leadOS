import { useEffect, useState } from "react";
export function useMediaQuery(query: string) {
  const [match, setMatch] = useState(false);
  useEffect(() => {
    const m = window.matchMedia(query);
    setMatch(m.matches);
    const listener = (e: MediaQueryListEvent) => setMatch(e.matches);
    m.addEventListener("change", listener);
    return () => m.removeEventListener("change", listener);
  }, [query]);
  return match;
}
