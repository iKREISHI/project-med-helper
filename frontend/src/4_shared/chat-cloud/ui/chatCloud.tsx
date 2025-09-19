import React from "react";
import styles from './chatCloud.module.css'
import Markdown from "react-markdown";

interface ChatCloudProps {
    isSending: boolean;
    children: React.ReactNode
}


export function ChatCloud({ isSending = false, children }: ChatCloudProps) {
    return (
        <div className={ isSending? styles.Root : styles.RootSender}>
            {children}
        </div>
    )
}