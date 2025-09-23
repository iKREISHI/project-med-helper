// lib/api/chat-api.ts
import { GET } from "@/4_shared/api/client";
import { PaginatedChatList, PaginatedChatListParams } from "../model/model";

export const getAllMessages = async (chatId: number, params: PaginatedChatListParams): Promise<PaginatedChatList> => {
    const { data, error } = await GET('/api/v0/chat/dialogs/{id}/message', {
        params: {
            path: {
                id: chatId
            },
            query: params
        }
    });
    
    if (error) {
        throw new Error('Failed to fetch messages');
    }
    
    if (!data) {
        throw new Error('No data received from server');
    }
    
    return data as PaginatedChatList;
}