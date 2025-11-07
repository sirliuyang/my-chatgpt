interface Props {
    role: "user" | "assistant";
    content: string;
}

export default function ChatBubble({role, content}: Props) {
    return (
        <div className={`mb-4 ${role === "user" ? "text-right" : "text-left"}`}>
            <div
                className={`inline-block p-3 rounded-lg ${
                    role === "user" ? "bg-blue-500 text-white" : "bg-gray-200 text-black"
                }`}
            >
                {content}
            </div>
        </div>
    );
}