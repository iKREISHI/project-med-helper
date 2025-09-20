'use client'

import { ChatCloud } from "@/4_shared/chat-cloud";
import { Box, Flex, ScrollArea } from "@radix-ui/themes";
import styles from "./page.module.css";
import { ResizableTextarea } from "@/4_shared";
import { useEffect, useRef, useState } from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github.css";


interface KeyValue<V = any> {
    isSending: boolean;
    message: string
}

const markdown = `
# Заголовок
**Жирный текст**
*Курсив*
- Список
[Ссылка](https://example.com)

аааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааа
\`\`\`ts
function autism() {
  console.log("hello, autism");
}
\`\`\`
`;


let messagesInit: KeyValue[] = [
    { isSending: true, message: "Привет, а аутизм лечится?" },
    { isSending: false, message: markdown },
    { isSending: true, message: "А, ясно" },
    { isSending: true, message: "Привет, а аутизм лечится?" },
    { isSending: false, message: "Привет, нет, а что?" },
    { isSending: true, message: "А, ясно" },
    { isSending: true, message: "Привет, а аутизм лечится?" },
    { isSending: false, message: "Привет, нет, а что?" },
    { isSending: true, message: "А, ясно" },
    { isSending: true, message: "Привет, а аутизм лечится?" },
    { isSending: false, message: "Привет, нет, а что?" },
    { isSending: true, message: "А, ясно" },
    { isSending: true, message: "Привет, а аутизм лечится?" },
    { isSending: false, message: "Привет, нет, а что?" },
    { isSending: true, message: "А, ясно" },
    { isSending: true, message: "Привет, а аутизм лечится?" },
    { isSending: false, message: "Привет, нет, а что?" },
    { isSending: true, message: "А, ясно" },
    { isSending: true, message: "Привет, а аутизм лечится?" },
    { isSending: false, message: "Привет, нет, а что?" },
    { isSending: true, message: "А, ясно" },
];

export default function ChatBot() {

    const [messages, setMessages] = useState<KeyValue[]>(messagesInit)
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const handleMessage = (messageU: string) => {
        const userMessage:KeyValue = {
            isSending: true,
            message: messageU
        } 
        setMessages(prev => [...prev, userMessage])
    }

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    },[messages]);

    return (
        <Flex direction='column'>
        <div>
            <div className={styles.ChatContainer}>
                <div className={styles.MessagesList}>
                    {messages.map((msg, index) => (
                        <div
                            key={index}
                            className={msg.isSending ? styles.UserMessage : styles.BotMessage}
                        >
                            <ChatCloud isSending={msg.isSending}>

                                <Markdown
                                    remarkPlugins={[remarkGfm]}
                                    rehypePlugins={[rehypeHighlight]}
                                >{msg.message}</Markdown>
                            </ChatCloud>
                        </div>
                    ))}
                    <div ref={messagesEndRef}></div>
                </div>
            </div>
        </div>
        <div className={styles.InputWrapper}>
            <ResizableTextarea
            onSend={handleMessage}
            />
        </div>            
        </Flex>
    );
}
