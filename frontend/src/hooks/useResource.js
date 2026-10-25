import { useCallback, useEffect, useRef, useState } from "react";

export default function useResource(loader) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const controllerRef = useRef(null);
  const requestIdRef = useRef(0);
  const mountedRef = useRef(false);

  const load = useCallback(async () => {
    const requestId = ++requestIdRef.current;
    controllerRef.current?.abort();

    const controller = new AbortController();
    controllerRef.current = controller;

    try {
      const result = await loader(controller.signal);

      if (requestId !== requestIdRef.current) return null;

      setData(result);
      setError("");
      return result;
    } catch (loadError) {
      if (
        loadError.name === "AbortError" ||
        requestId !== requestIdRef.current
      ) {
        return null;
      }

      setError(loadError.message || "Unable to load this information.");
      return null;
    } finally {
      if (requestId === requestIdRef.current) {
        setLoading(false);
        setRefreshing(false);
      }
    }
  }, [loader]);

  useEffect(() => {
    let active = true;
    mountedRef.current = true;

    queueMicrotask(() => {
      if (active) load();
    });

    return () => {
      active = false;
      mountedRef.current = false;
      requestIdRef.current += 1;
      controllerRef.current?.abort();
    };
  }, [load]);

  const refresh = useCallback(async () => {
    if (!mountedRef.current) return null;

    setRefreshing(true);
    return load();
  }, [load]);

  return {
    data,
    loading,
    refreshing,
    error,
    refresh,
  };
}
