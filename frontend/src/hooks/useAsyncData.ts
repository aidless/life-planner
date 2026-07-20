/**
 * useAsyncData — 统一处理 loading / error / data 三状态的 hook
 *
 * 替代各页面散落的 useState(loading) + try/catch 模式。
 * 自动提取后端 ApiResponse.error 信息。
 */

import { useCallback, useEffect, useState } from "react";

export interface AsyncDataState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  reload: () => Promise<void>;
  setData: (data: T | null) => void;
}

export function useAsyncData<T>(
  fetcher: () => Promise<T>,
  deps: unknown[] = [],
): AsyncDataState<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetcher();
      setData(result);
    } catch (err: any) {
      const msg = err?.userMessage || err?.message || "加载失败，请稍后重试";
      setError(msg);
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => {
    load();
  }, [load]);

  return { data, loading, error, reload: load, setData };
}