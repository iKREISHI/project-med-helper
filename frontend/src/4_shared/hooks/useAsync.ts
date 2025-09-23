"use client";
import { useState } from "react";

interface AsyncProps {
  loading: boolean;
  error: string | null;
  success: boolean;
}

type AsyncFunc<T extends any[]> = (...args: T) => Promise<void>;

export function useAsync<T extends any[]>(asyncFunc: AsyncFunc<T>) {
  const [state, setState] = useState<AsyncProps>({
    loading: false,
    error: null,
    success: false,
  });

  const run = async (...args: T) => {
    setState({ loading: true, error: null, success: false });

    try {
      await asyncFunc(...args);
      setState({ loading: false, error: null, success: true });
    } catch (e: any) {
      setState({
        loading: false,
        error: e.message || "An error has occurred",
        success: false,
      });
      console.log("Error:", e.message);
    }
  };

  return {
    loading: state.loading,
    error: state.error,
    success: state.success,
    run,
  };
}
