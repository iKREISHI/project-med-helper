'use client'

import { useEffect, useState } from "react"
import { getDocuments, PatchedDocumentInstance } from "@/3_entities/documents"

interface UseDocumentsResult {
  data: PatchedDocumentInstance[] | null
  last: PatchedDocumentInstance | null
  loading: boolean
  error: Error | null
}

export function useDocuments(): UseDocumentsResult {
  const [data, setData] = useState<PatchedDocumentInstance[] | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    setLoading(true)
    getDocuments({ page: 1, page_size: 10 })
      .then((res) => {
        setData(res.results)
      })
      .catch((err: unknown) => {
        if (err instanceof Error) {
          setError(err)
        } else {
          setError(new Error("Unknown error"))
        }
      })
      .finally(() => setLoading(false))
  }, [])

  return { 
    data, 
    last: data?.[data.length - 1] ?? null, 
    loading, 
    error 
  }
}
