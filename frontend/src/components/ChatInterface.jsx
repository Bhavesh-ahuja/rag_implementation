import React, { useState, useEffect, useRef } from "react";
import ReactMarkdown from 'react-markdown';
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
        } catch {
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
            <header className="bg-blue-600 text-white p-4 rounded-t-lg shadow-md flex justify-between items-center">
                <div>
                    <h1 className="text-xl font-bold">RAG AI Agent</h1>
                    <p className="text-xs text-blue-200">Session ID: {sessionId}</p>
                </div>
                <FileList />
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
                            <div className={`prose ${msg.role === "user" ? "prose-invert" : ""} max-w-none text-sm leading-relaxed break-words`}>
                                <ReactMarkdown>{msg.content}</ReactMarkdown>
                            </div>

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

import { uploadDocument, getFiles, deleteFile } from "../lib/api";

// Create a context or event bus for file updates would be better, 
// strictly for this simple app, we can just use a global event or re-fetch in FileList component intermittently or trigger via prop.
// To keep it simple without major refactor:
// We will emit a custom event when upload is done.

function FileList() {
    const [files, setFiles] = useState([]);

    // fetchFiles moved to useEffect to satisfy linter
    // We also need access to it in handleDelete, so actually we should useCallback.
    // Let's use useCallback instead which is cleaner.
    const fetchFiles = React.useCallback(async () => {
        try {
            const data = await getFiles();
            console.log("Fetched files:", data); // Debugging
            setFiles(data.files || []);
        } catch (e) {
            console.error(e);
        }
    }, []);

    const handleDelete = async (filename) => {
        if (window.confirm(`Are you sure you want to delete "${filename}"?`)) {
            try {
                // Optimistically remove or show loading could be here, but simple alert is fine for now
                await deleteFile(filename);
                // Dispatch/refresh logic is in useEffect
                fetchFiles();
                alert("File deleted.");
            } catch (e) {
                console.error(e);
                alert("Failed to delete file. It may have already been removed.");
            }
        }
    };


    useEffect(() => {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        fetchFiles();
        window.addEventListener("fileUploaded", fetchFiles);
        return () => window.removeEventListener("fileUploaded", fetchFiles);
    }, [fetchFiles]);


    return (
        <div className="text-right">
            <p className="text-xs font-semibold text-blue-100 uppercase tracking-wider mb-1">Active Documents:</p>
            {files.length === 0 ? (
                <span className="text-xs bg-red-500 text-white px-2 py-1 rounded shadow-sm">No Files Uploaded</span>
            ) : (
                <div className="flex flex-col items-end gap-1">
                    {files.map((f, i) => (
                        <div key={i} className="flex items-center gap-1 bg-white px-2 py-1 rounded shadow-sm max-w-[200px]">
                            <span className="text-xs text-blue-800 font-medium truncate flex-1" title={f}>
                                📄 {f}
                            </span>
                            <button
                                onClick={() => handleDelete(f)}
                                className="text-gray-400 hover:text-red-500 transition-colors p-0.5 rounded-full hover:bg-red-50"
                                title="Remove File"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-3 h-3">
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}

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
            // Dispatch event to update list
            window.dispatchEvent(new Event("fileUploaded"));
            window.dispatchEvent(new Event("fileUploaded"));
        } catch (error) {
            alert(`Failed to upload file: ${error.message}`);
        } finally {
            setUploading(false);
            if (fileInputRef.current) fileInputRef.current.value = "";
        }
    };
    // ... rest of UploadButton (unchanged)
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
