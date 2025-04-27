"use client";

import React, { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import FileUploader from "./FileUploader";
import OptionsPanel, { PluginDetail } from "./OptionsPanel";
import { askQuestion, askAgent, getUploadedFiles } from "../utils/api";

interface Message {
  role: "user" | "ai";
  content: string;
}

const ChatBox = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [userInput, setUserInput] = useState("");
  const [model, setModel] = useState("openai");
  const [useCOT, setUseCOT] = useState(false);
  const [useRAG, setUseRAG] = useState(false);
  const [pluginDetail, setPluginDetail] = useState<PluginDetail[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);

  const aiMessageRef = useRef<HTMLDivElement>(null);

  // 獲取上傳的檔案列表
  const fetchUploadedFiles = async () => {
    try {
      const files = await getUploadedFiles();
      setUploadedFiles(files);
    } catch (error) {
      console.error("can't access file list:", error);
    }
  };

  useEffect(() => {
    fetchUploadedFiles();
  }, []);

  useEffect(() => {
    if (selectedFiles.length > 0) {
      setUseRAG(true);
    } else {
      setUseRAG(false);
    }
  }, [selectedFiles]);

  const scrollToBottom = () => {
    setTimeout(() => {
      aiMessageRef.current?.scrollIntoView({ behavior: "smooth" });
    }, 100);
  };

  const isAgentRequired = pluginDetail.some((plugin) => plugin.enable);
  const enabledPlugins = pluginDetail.filter((p) => p.enable);

  const handleSubmit = async () => {
    if (!userInput.trim()) return;

    const newMessages: Message[] = [
      ...messages,
      { role: "user", content: userInput },
    ];
    setMessages(newMessages);
    setLoading(true);
    setUserInput("");

    const options = {
      question: userInput,
      model,
      use_cot: useCOT,
      use_rag: useRAG,
      plugin_detail: enabledPlugins,
      selected_files: selectedFiles,
    };

    const result = isAgentRequired
      ? await askAgent(options)
      : await askQuestion(options);

    if (!result) {
      setMessages((prev) => [
        ...newMessages,
        {
          role: "ai",
          content: "⚠️ Unable to retrieve AI response. Please try again later.",
        },
      ]);
      setLoading(false);
      return;
    }

    let aiResponse = "";
    if (typeof result === "string") {
      // 非 streaming（例如 CoT），直接顯示整段
      aiResponse += result;
      setMessages((prev) => [
        ...newMessages,
        { role: "ai", content: aiResponse },
      ]);
      scrollToBottom();
    } else {
      // streaming（非 CoT 模式）
      for await (const chunk of result) {
        aiResponse += chunk;
        setMessages((prev) => [
          ...newMessages,
          { role: "ai", content: aiResponse },
        ]);
        scrollToBottom();
      }
    }

    setLoading(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="flex h-screen w-screen bg-gray-400 overflow-hidden">
      {/* 左側邊欄 */}
      <div className="w-72 bg-[#97A5C0] h-full overflow-y-auto shadow-md">
        <h3 className="text-xl font-medium text-center my-4 !text-[#2A4C65]">
          Settings
        </h3>

        <div className="px-4 mb-6">
          <h5 className="text-sm font-medium mb-2 !text-blue-950">
            Model Options
          </h5>
          <OptionsPanel
            model={model}
            setModel={setModel}
            useCOT={useCOT}
            setUseCOT={setUseCOT}
            pluginDetail={pluginDetail}
            setPluginDetail={setPluginDetail}
            selectedFiles={selectedFiles}
            setSelectedFiles={setSelectedFiles}
            uploadedFiles={uploadedFiles}
          />
        </div>

        <div className="px-4">
          <h5 className="text-sm font-medium mb-2 !text-blue-950">
            File Upload
          </h5>
          <FileUploader
            file={file}
            setFile={setFile}
            onUploadSuccess={fetchUploadedFiles}
          />
        </div>
      </div>

      {/* 右側對話框 */}
      <div className="flex-1 flex flex-col bg-[#B6BBBE] h-full">
        <h2 className="text-2xl !font-extrabold !text-[#8F6849] px-6 pt-4 pb-2">
          AI Chatting Room
        </h2>

        <div className="flex-1 px-6 pb-4 overflow-y-auto">
          <div className="bg-[#DCDDDF] rounded-lg p-4 h-full overflow-y-auto">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`mb-4 ${
                  msg.role === "user" ? "text-right" : "text-left"
                }`}
              >
                <div
                  className={`inline-block w-[80%] p-3 rounded-lg ${
                    msg.role === "user"
                      ? "bg-[#C0B0A2] text-white"
                      : "bg-gray-400 text-gray-100"
                  } text-left`}
                >
                  <div className="mb-1 font-medium">
                    {msg.role === "user" ? " 🐻 You" : "🤖 AI"}
                  </div>
                  <ReactMarkdown
                    components={{
                      h2: ({ node, ...props }) => (
                        <h2 className="!text-base" {...props} />
                      ),
                    }}
                  >
                    {msg.content.replace(/\\n/g, "\n")}
                  </ReactMarkdown>
                </div>
              </div>
            ))}
            {loading && (
              <div ref={aiMessageRef} className="text-left">
                <div className="inline-block p-3 rounded-lg bg-gray-400 text-gray-100">
                  <div className="mb-1 font-medium">🤖 AI</div>
                  <div className="flex items-center">
                    <span className="w-2 h-2 bg-blue-300 rounded-full mr-1 animate-pulse delay-75"></span>
                    <span className="w-2 h-2 bg-blue-300 rounded-full mr-1 animate-pulse delay-150"></span>
                    <span className="w-2 h-2 bg-blue-300 rounded-full animate-pulse delay-300"></span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="p-3 bg-[#BFD1C4]">
          <div className="flex rounded-lg bg-[#A1B0AD] m-1 p-1">
            <textarea
              className="flex-1 bg-gray-300 text-[#66828E] placeholder-[#66828E] border-0 focus:ring-0 resize-none outline-none"
              rows={3}
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder=" Ask anything..."
            />
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="ml-2 px-4 py-2 bg-[#66828E] text-white font-medium rounded-xl disabled:opacity-50"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatBox;
