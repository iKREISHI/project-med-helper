'use client'

// features/dialogs/model/useDialogs.ts
import { useEffect, useState } from "react"
import { getAllDialogs } from "@/3_entities/dialogs"
import { PaginatedDialogList, PaginatedDialogListParams } from "@/3_entities/dialogs"

interface UseDialogsResult {
  data: PaginatedDialogList | null
  loading: boolean
  error: Error | null
}

export function useDialogs(params: PaginatedDialogListParams): UseDialogsResult {
  const [data, setData] = useState<PaginatedDialogList | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    setLoading(true)
    getAllDialogs(params)
      .then((res) => setData(res))
      .catch((err: unknown) => {
        if (err instanceof Error) {
          setError(err)
        } else {
          setError(new Error("Unknown error"))
        }
      })
      .finally(() => setLoading(false))
  }, [params])

  return { data, loading, error }
}
