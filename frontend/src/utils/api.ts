import axios from "axios";

const API_BASE = "http://localhost:8000/api";

// 一般問答（不含插件）
export async function askQuestion(payload: {
  question: string;
  model: string;
  use_rag?: boolean;
  use_cot?: boolean;
  selected_files?: string[];
}) {
  const response = await fetch(`${API_BASE}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Session-ID": "lesleyc" },
    body: JSON.stringify(payload),
  });

  const contentType = response.headers.get("Content-Type") || "";

  if (contentType.includes("text/event-stream")) {
    // --- 處理 Streaming Response ---
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) return;

    async function* stream() {
      while (true) {
        const { done, value } = await reader!.read();
        if (done) break;
        yield decoder.decode(value);
      }
    }

    return stream(); // 回傳 async generator
  } else {
    // --- 處理非 Streaming Response（CoT 模式）---
    const text = await response.text();
    return text; // 回傳一般文字
  }
}

// 使用 Agent + Plugin 的問答
export async function askAgent(payload: {
  question: string;
  model: string;
  use_rag?: boolean;
  use_cot?: boolean;
  selected_files?: string[];
  plugin_detail?: {
    id: number;
    tool_name: string;
    enable: boolean;
  }[];
}) {
  const response = await fetch(`${API_BASE}/agent`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Session-ID": "lesleyc" },
    body: JSON.stringify(payload),
  });

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  async function* stream() {
    while (true) {
      const { done, value } = await reader!.read();
      if (done) break;
      yield decoder.decode(value);
    }
  }

  return stream();
}

// 檔案上傳
export async function uploadFile(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await axios.post(`${API_BASE}/upload`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return response.data; // 應回傳檔案儲存後的資訊（如檔名、路徑等）
}

// 取得所有已上傳的檔案名稱
export async function getUploadedFiles(): Promise<string[]> {
  const response = await axios.get(`${API_BASE}/files`);
  return response.data;
}
