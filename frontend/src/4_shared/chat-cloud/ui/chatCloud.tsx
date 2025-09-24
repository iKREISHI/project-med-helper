import React from "react";
import styles from "./chatCloud.module.css";
import { time } from "console";

interface ChatCloudProps {
  isSending: boolean;
  children: React.ReactNode;
  time: string
}

export function ChatCloud({ isSending = false, children, time }: ChatCloudProps) {
  return (
    <div
      className={`${styles.Sender} ${
        isSending ? styles.Root : styles.RootSender
      }`}
    >
      <div className={styles.Content}>{children}</div>
      <div className={styles.Time}>{time}</div>
    </div>
  );
}
