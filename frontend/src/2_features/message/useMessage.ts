// features/message/useMessage.ts
import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { getAllMessages } from "@/3_entities/message/api/getAllMessages"
import { PaginatedChatList, PaginatedChatListParams } from "@/3_entities/message/model/model"

interface UseMessagesResult {
  data: PaginatedChatList | null
  loading: boolean
  error: Error | null
  refetch: () => Promise<void>
}

export function useMessage(params?: PaginatedChatListParams): UseMessagesResult {
  const [data, setData] = useState<PaginatedChatList | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<Error | null>(null)
  const urlParams = useParams();
  const chatId:string = urlParams.slug;

  const fetchMessages = async () => {
    if (typeof window === 'undefined') return;

    if (!chatId) {
      setLoading(false)
      return
    }

    setLoading(true)
    setError(null)
    
    const numericChatId = parseInt(chatId);
    
    if (isNaN(numericChatId)) {
      setError(new Error("Invalid chat ID"))
      setLoading(false)
      return
    }

    try {
      console.log(numericChatId ,typeof numericChatId);
      const response = await getAllMessages(numericChatId, params || { page: 1, page_size: 50 })
      setData(response)
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchMessages()
  }, [chatId, params?.page, params?.page_size])

  return { 
    data, 
    loading, 
    error, 
    refetch: fetchMessages 
  }
}