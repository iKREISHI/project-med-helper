import { ChatCloud } from "@/4_shared/chat-cloud";

export default function ChatBot(){
    return (
        <div>
            <h1>Тут будет чат!</h1>
            <ChatCloud isSending={true}>
                <p>Тест</p>
            </ChatCloud>
            <br></br>
            <ChatCloud isSending={false}>
                <p>Привет, получается, это тест?</p>
            </ChatCloud>
        </div>
    )
}