import React, { useState, useEffect, useRef } from "react";
import { sendMessage } from "../lib/api";

const generateSessionId = () => {
    return "session-" + Math.random().toString(36).substr(2, 9);
};

export default function ChatInterface() {
    const [sessionId] = useState(generateSessionId());
    const [messages, setMessages] = useState([
        { role: "ai", content: "Hello! I am your RAG AI assistant. Ask me anything about your documents." }
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = { role: "user", content: input };
        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        setLoading(true);

        try {
            const data = await sendMessage(sessionId, userMessage.content);
            const aiMessage = {
                role: "ai",
                content: data.answer,
                sources: data.sources,
            };
            setMessages((prev) => [...prev, aiMessage]);
        } catch (error) {
            setMessages((prev) => [
                ...prev,
                { role: "ai", content: "Sorry, something went wrong. Please try again." }
            ]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-screen max-w-4xl mx-auto p-4 bg-gray-50 shadow-xl rounded-lg overflow-hidden">
            <header className="bg-blue-600 text-white p-4 rounded-t-lg shadow-md">
                <h1 className="text-xl font-bold">RAG AI Agent</h1>
                <p className="text-xs text-blue-200">Session ID: {sessionId}</p>
            </header>

            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-white">
                {messages.map((msg, index) => (
                    <div
                        key={index}
                        className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                    >
                        <div
                            className={`max-w-[80%] p-3 rounded-2xl shadow-sm ${msg.role === "user"
                                ? "bg-blue-500 text-white rounded-tr-none"
                                : "bg-gray-100 text-gray-800 rounded-tl-none border border-gray-200"
                                }`}
                        >
                            <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>

                            {msg.sources && msg.sources.length > 0 && (
                                <div className="mt-2 pt-2 border-t border-gray-300 text-xs text-gray-500">
                                    <p className="font-semibold mb-1">Sources:</p>
                                    <ul className="list-disc list-inside space-y-1">
                                        {msg.sources.map((src, i) => (
                                            <li key={i} className="truncate" title={src}>
                                                {src}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex justify-start">
                        <div className="bg-gray-100 p-3 rounded-2xl rounded-tl-none border border-gray-200">
                            <div className="flex space-x-2">
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
                            </div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <form onSubmit={handleSend} className="p-4 bg-white border-t border-gray-200 flex gap-2">
                <UploadButton />
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type your message..."
                    className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                    disabled={loading}
                />
                <button
                    type="submit"
                    disabled={loading}
                    className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                    Send
                </button>
            </form>
        </div>
    );
}

import { uploadDocument } from "../lib/api";

function UploadButton() {
    const [uploading, setUploading] = useState(false);
    const fileInputRef = useRef(null);

    const handleFileChange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setUploading(true);
        try {
            await uploadDocument(file);
            alert("File uploaded and ingested successfully!");
        } catch (error) {
            alert("Failed to upload file.");
        } finally {
            setUploading(false);
            if (fileInputRef.current) fileInputRef.current.value = "";
        }
    };

    return (
        <div className="flex items-center">
            <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                className="hidden"
                accept=".txt,.pdf,.md"
            />
            <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading}
                className="p-3 text-gray-500 hover:text-blue-600 hover:bg-gray-100 rounded-lg transition-colors"
                title="Upload Document"
            >
                {uploading ? (
                    <div className="w-6 h-6 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
                ) : (
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M18.375 12.739l-7.693 7.693a4.5 4.5 0 01-6.364-6.364l10.94-10.94A3 3 0 1119.5 7.372L8.552 18.32m.009-.01l-.01.01m5.71-5.71a9 9 0 11-12.728 12.728A9 9 0 0110 3.868" />
                    </svg>
                )}
            </button>
        </div>
    );
}
