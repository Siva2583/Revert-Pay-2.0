import { useCallback, useEffect, useRef, useState } from "react";

export default function useAsyncAction() {
  const [pending, setPending] = useState(null);
  const pendingRef = useRef(null);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;

    return () => {
      mountedRef.current = false;
    };
  }, []);

  const run = useCallback(async (key, operation) => {
    if (pendingRef.current !== null) return null;

    pendingRef.current = key;

    if (mountedRef.current) {
      setPending(key);
    }

    try {
      return await operation();
    } finally {
      pendingRef.current = null;

      if (mountedRef.current) {
        setPending(null);
      }
    }
  }, []);

  return { pending, run };
}
