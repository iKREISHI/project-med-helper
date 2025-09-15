import { ChatCloud } from "@/4_shared/chat-cloud";
import { Box, Flex, ScrollArea } from "@radix-ui/themes";
import styles from "./page.module.css";



interface KeyValue<V = any> {
   isSending: boolean;
   message:string 
}
let messages:KeyValue[] = [
   {isSending: true, message:"Привет, а аутизм лечится?"},
   {isSending: false, message:"Привет, нет, а что?"},
   {isSending: true, message:"А, ясно"},
   {isSending: true, message:"Привет, а аутизм лечится?"},
   {isSending: false, message:"Привет, нет, а что?"},
   {isSending: true, message:"А, ясно"},
   {isSending: true, message:"Привет, а аутизм лечится?"},
   {isSending: false, message:"Привет, нет, а что?"},
   {isSending: true, message:"А, ясно"},
   {isSending: true, message:"Привет, а аутизм лечится?"},
   {isSending: false, message:"Привет, нет, а что?"},
   {isSending: true, message:"А, ясно"},
   {isSending: true, message:"Привет, а аутизм лечится?"},
   {isSending: false, message:"Привет, нет, а что?"},
   {isSending: true, message:"А, ясно"},
   {isSending: true, message:"Привет, а аутизм лечится?"},
   {isSending: false, message:"Привет, нет, а что?"},
   {isSending: true, message:"А, ясно"},
   {isSending: true, message:"Привет, а аутизм лечится?"},
   {isSending: false, message:"Привет, нет, а что?"},
   {isSending: true, message:"А, ясно"},
]; 


export default function ChatBot() {
   return (
      <Box width='100vw' height='100vh' p="4">
         <Flex
            direction='column'
            height='100%'
            gap="4"
         >  
            <ScrollArea 
                type="auto" 
                style={{ 
                    height: 'calc(100vh - 120px)', // Вычитаем высоту заголовка и паддингов
                    flex: 1 
                }}
            >
                <Flex
                    direction='column'
                    gap='3'
                    p="2"
                    className={styles.ChatContainer}
                >
                    {messages.map((msg, index) =>
                        <div
                            key={index}
                            className={msg.isSending ? styles.UserMessage : styles.BotMessage}
                        >
                            <ChatCloud isSending={msg.isSending}>
                                <p>{msg.message}</p>
                            </ChatCloud>
                        </div>
                    )}
                </Flex>
            </ScrollArea>

            <div style={{ 
                padding: '10px', 
                borderTop: '1px solid var(--gray-5)',
                background: 'var(--color-background)'
            }}>
            </div>
         </Flex>
      </Box>
   );
}