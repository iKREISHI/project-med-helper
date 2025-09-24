import { components } from "@/4_shared/api/types";

export type Dialog = components['schemas']['Dialog']

export type PaginatedDialogList = components['schemas']['PaginatedDialogList']

export type DialogCreate = components['schemas']['DialogCreate']

export interface PaginatedDialogListParams{
    page: number;
    page_size: number;
}