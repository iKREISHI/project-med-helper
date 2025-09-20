import React from "react";
import styles from "./chatCloud.module.css";

interface ChatCloudProps {
  isSending: boolean;
  children: React.ReactNode;
}

export function ChatCloud({ isSending = false, children }: ChatCloudProps) {
  return (
    <div
      className={`${styles.Sender} ${
        isSending ? styles.Root : styles.RootSender
      }`}
    >
      {children}
    </div>
  );
}
