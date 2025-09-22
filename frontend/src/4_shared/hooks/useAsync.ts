"use client";
import { useState } from "react";

interface AsyncProps {
  loading: boolean;
  error: string | null;
  success: boolean;
}

export function useAsync(asyncFunc: () => Promise<void>) {
  const [state, setState] = useState<AsyncProps>({
    loading: false,
    error: null,
    success: false,
  });

  const run = async () => {
    setState({ loading: true, error: null, success: false });

    try {
      await asyncFunc();
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