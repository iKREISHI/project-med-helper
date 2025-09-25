"use client";
import React, { useEffect, useRef, useState } from "react";
import { Flex, Button, Box, Spinner } from "@radix-ui/themes";
import { ChatCloud } from "@/4_shared/chat-cloud";
import styles from "./page.module.css";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github.css";
import { useMessage } from "@/2_features/message/useMessage";
import { sendMessage } from "@/3_entities/message/api/addNewMessage";
import { useParams } from "next/navigation";
import { checkValidate } from "@/3_entities/checkDocument/api/checkValidate";
import type { DocumentValidationResponse } from "@/3_entities/checkDocument/model/model"; // путь подставь реальный, если нужно

interface ChatMessage {
  id: number;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
  isThinking?: boolean;
}

interface ChatBotWindowProps {
  documentId?: number | null;
}

export default function ChatBotWindow({ documentId }: ChatBotWindowProps) {
  // (оставил загрузку сообщений — возможно нужно для истории)
  const { data, loading, error, refetch } = useMessage({
    page: 1,
    page_size: 50,
  });

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [validating, setValidating] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const urlParams = useParams();
  const chatId: string | undefined = (urlParams as any)?.slug;
  const usedChatID = chatId ? parseInt(chatId) : undefined;

  useEffect(() => {
    if (data && data.results) {
      setMessages(data.results as ChatMessage[]);
    }
  }, [data]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // отправка обычного сообщения (оставил как есть)
  const handleMessage = async (messageContent: string) => {
    if (!messageContent.trim()) return;

    const tempUserMessage: ChatMessage = {
      id: Date.now(),
      role: "user",
      content: messageContent,
      created_at: new Date().toISOString(),
    };

    const thinkingMessage: ChatMessage = {
      id: Date.now() + 1,
      role: "assistant",
      content: "Думаю...",
      created_at: new Date().toISOString(),
      isThinking: true,
    };

    setMessages((prev) => [...prev, tempUserMessage, thinkingMessage]);
    setIsSending(true);

    try {
      const response = usedChatID ? await sendMessage(usedChatID, messageContent) : null;

      setMessages((prev) => {
        const withoutThinking = prev.filter((m) => !m.isThinking);
        return response ? [...withoutThinking, response as ChatMessage] : withoutThinking;
      });

      await refetch();
    } catch (err) {
      console.error("Ошибка отправки сообщения:", err);
      setMessages((prev) => prev.filter((m) => !m.isThinking));
      const errorMessage: ChatMessage = {
        id: Date.now() + 2,
        role: "assistant",
        content: "Извините, произошла ошибка. Попробуйте ещё раз.",
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsSending(false);
    }
  };

  // --- НОВОЕ: handleValidate выводит ТОЛЬКО recommendations ---
  const handleValidate = async () => {
    if (!documentId) {
      // Лучше показать пользователю, но пока вывод в консоль
      console.warn("documentId not provided — сохраните документ перед проверкой.");
      const warnMsg: ChatMessage = {
        id: Date.now(),
        role: "assistant",
        content: "Сначала сохраните документ, затем нажмите «Проверить».",
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, warnMsg]);
      return;
    }

    setValidating(true);
    try {
      const validationResult: DocumentValidationResponse | null = await checkValidate(documentId);

      if (!validationResult) {
        const emptyMsg: ChatMessage = {
          id: Date.now(),
          role: "assistant",
          content: "Проверка завершилась, но результат пустой.",
          created_at: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, emptyMsg]);
        return;
      }

      // Берём только recommendations (по описанию типа — string)
      const recommendations = validationResult.recommendations?.toString()?.trim();

      const content = recommendations && recommendations.length > 0
        ? recommendations
        : "Рекомендаций не найдено.";

      const validationMessage: ChatMessage = {
        id: Date.now(),
        role: "assistant",
        content, // это будет отрендерено через Markdown
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, validationMessage]);
    } catch (err) {
      console.error("Ошибка проверки документа:", err);
      const errMsg: ChatMessage = {
        id: Date.now(),
        role: "assistant",
        content: "Ошибка при выполнении проверки документа. Попробуйте позже.",
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setValidating(false);
    }
  };

  if (loading) {
    return (
      <Flex direction="column" justify="center" align="center" style={{ height: "100vh" }}>
        <div>Загрузка сообщений...</div>
      </Flex>
    );
  }

  if (error) {
    return (
      <Flex direction="column" justify="center" align="center" style={{ height: "100vh" }}>
        <div>Ошибка: {(error as Error).message}</div>
      </Flex>
    );
  }

  // показываем только ответы модели
  const assistantMessages = messages.filter((m) => m.role === "assistant");

  return (
    <Flex direction="column" style={{ height: "100vh" }}>
      <Flex align="center" justify="space-between" style={{ padding: "12px" }}>
        <div style={{ fontWeight: 600 }}>Чат-бот</div>
        <Button
          size="2"
          variant="outline"
          onClick={handleValidate}
          disabled={!documentId || validating}
        >
          {validating ? <Spinner size="1" /> : "Проверить"}
        </Button>
      </Flex>

      <Box flexGrow="1" className={styles.ChatContainer} p={{ initial: "2", lg: "3" }}>
  <div ref={messagesEndRef} className={styles.MessagesScroll}>
    <div className={styles.MessagesList}>
      {assistantMessages.length === 0 ? (
        <div className={styles.NoMessages}>Нет ответов модели.</div>
      ) : (
        assistantMessages.map(msg => (
          <div key={msg.id} className={styles.BotMessage}>
            <ChatCloud isSending={false} time={new Date(msg.created_at).toLocaleTimeString()}>
              <Markdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeHighlight]}>
                {msg.content}
              </Markdown>
            </ChatCloud>
          </div>
        ))
      )}
      <div ref={messagesEndRef} />
    </div>
  </div>
</Box>

      {/* Ввод пользователя (опционально) */}
      <div className={styles.InputWrapper}>
        <ResizableInput onSend={(text) => handleMessage(text)} disabled={isSending} />
      </div>
    </Flex>
  );
}

/* Простейший input - можно заменить на свой компонент */
function ResizableInput({ onSend, disabled }: { onSend: (text: string) => void; disabled?: boolean }) {
  const [value, setValue] = useState("");
  return (
    <div style={{ width: "100%", maxWidth: 800, display: "flex", gap: 8 }}>
    </div>
  );
}
