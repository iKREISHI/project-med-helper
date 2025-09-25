"use client";
import { ChatCloud } from "@/4_shared/chat-cloud";
import { Box, Flex, Spinner } from "@radix-ui/themes";
import styles from "./page.module.css";
import { ResizableTextarea } from "@/4_shared";
import { useEffect, useRef, useState } from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github.css";
import { useMessage } from "@/2_features/message/useMessage";
import { sendMessage } from "@/3_entities/message/api/addNewMessage";
import { useParams } from "next/navigation";

interface ChatMessage {
  id: number;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
  isThinking?: boolean; 
}

export default function ChatBot() {
  const { data, loading, error, refetch } = useMessage({
    page: 1,
    page_size: 50
  });
  
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const urlParams = useParams();
  const chatId:string = urlParams.slug
  const usedChatID = parseInt(chatId)

  // Загрузка сообщений из API
  useEffect(() => {
    if (data && data.results) {
      setMessages(data.results);
    }
  }, [data]);

  function formatDate(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleString("ru-RU", {
    day: "2-digit",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  });
}

  // Обработка отправки сообщения
  const handleMessage = async (messageContent: string) => {
    if (!messageContent.trim()) return;

    // Создаем временное сообщение пользователя
    const tempUserMessage: ChatMessage = {
      id: Date.now(), // временный ID
      role: "user",
      content: messageContent,
      created_at: new Date().toISOString()
    };

    // Создаем индикатор "Думаю"
    const thinkingMessage: ChatMessage = {
      id: Date.now() + 1, // временный ID
      role: "assistant",
      content: "Думаю...",
      created_at: new Date().toISOString(),
      isThinking: true
    };

    // Добавляем оба сообщения в список
    setMessages(prev => [...prev, tempUserMessage, thinkingMessage]);
    setIsSending(true);

    try {
      // Отправляем сообщение на сервер
      const response = await sendMessage(usedChatID, messageContent);
      
      // Удаляем индикатор "Думаю" и добавляем реальный ответ
      setMessages(prev => {
        const withoutThinking = prev.filter(msg => !msg.isThinking);
        return [...withoutThinking, response];
      });

      // Обновляем список сообщений с сервера (опционально)
      await refetch();

    } catch (err) {
      console.error('Ошибка отправки сообщения:', err);
      
      // Удаляем индикатор "Думаю" в случае ошибки
      setMessages(prev => prev.filter(msg => !msg.isThinking));
      
      // Можно показать сообщение об ошибке
      const errorMessage: ChatMessage = {
        id: Date.now() + 2,
        role: "assistant",
        content: "Извините, произошла ошибка. Попробуйте еще раз.",
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev.filter(msg => !msg.isThinking), errorMessage]);
    } finally {
      setIsSending(false);
    }
  };

  // Автопрокрутка к последнему сообщению
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  if (loading) {
    return (
      <Flex direction="column" justify="center" align="center" style={{ height: '100vh' }}>
        <div>Загрузка сообщений...</div>
      </Flex>
    );
  }

  if (error) {
    return (
      <Flex direction="column" justify="center" align="center" style={{ height: '100vh' }}>
        <div>Ошибка: {error.message}</div>
      </Flex>
    );
  }

  return (
    <Flex direction="column" style={{ height: '100vh' }}>
      <Box flexGrow="1" className={styles.ChatContainer} p={{ initial: "2", lg: "3" }}>
        <div className={styles.MessagesList}>
          {messages.length === 0 ? (
            <div className={styles.NoMessages}>
              Нет сообщений. Начните диалог!
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={
                  msg.role === 'user' ? styles.UserMessage : styles.BotMessage
                }
              >
                <ChatCloud isSending={msg.role === 'user'} time={formatDate(msg.created_at)}>
                  {msg.isThinking ? (
                    <Flex align="center" gap="2">
                      <Spinner size="2" />
                      <span>Думаю...</span>
                    </Flex>
                  ) : (
                    <Markdown
                      remarkPlugins={[remarkGfm]}
                      rehypePlugins={[rehypeHighlight]}
                    >
                      {msg.content}
                    </Markdown>
                  )}
                </ChatCloud>
              </div>
            ))
          )}
          <div ref={messagesEndRef}></div>
        </div>
      </Box>
      <div className={styles.InputWrapper}>
        <ResizableTextarea onSend={handleMessage} />
      </div>
    </Flex>
  );
}