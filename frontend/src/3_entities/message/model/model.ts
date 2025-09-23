import { components } from "@/4_shared/api/types";

export type Message  = components['schemas']['ChatMessage'];

export type ChatRequest = components['schemas']['ChatRequest']

export type ChatResponse = components['schemas']['ChatResponse']

export type PaginatedChatList = components['schemas']['PaginatedChatMessage']

export interface PaginatedChatListParams{
    chatId: number
    page: number;
    page_size: number
}