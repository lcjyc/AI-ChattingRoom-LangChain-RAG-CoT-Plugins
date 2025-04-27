"use client";

import { Dispatch, SetStateAction, useEffect } from "react";

export type PluginDetail = {
  id: number;
  tool_name: string;
  enable: boolean;
};

export type OptionsProps = {
  model: string;
  setModel: Dispatch<SetStateAction<string>>;
  useCOT: boolean;
  setUseCOT: Dispatch<SetStateAction<boolean>>;
  pluginDetail: PluginDetail[];
  setPluginDetail: Dispatch<SetStateAction<PluginDetail[]>>;
  selectedFiles: string[];
  setSelectedFiles: Dispatch<SetStateAction<string[]>>;
  uploadedFiles: string[];
};

const AVAILABLE_PLUGINS: Omit<PluginDetail, "enable">[] = [
  { id: 1, tool_name: "web_search" },
  { id: 2, tool_name: "code_interpreter" },
  { id: 3, tool_name: "wikipedia" },
  { id: 4, tool_name: "arxiv" },
];

const OptionsPanel = ({
  model,
  setModel,
  useCOT,
  setUseCOT,
  pluginDetail,
  setPluginDetail,
  selectedFiles,
  setSelectedFiles,
  uploadedFiles,
}: OptionsProps) => {
  useEffect(() => {
    if (pluginDetail.length === 0) {
      setPluginDetail(AVAILABLE_PLUGINS.map((p) => ({ ...p, enable: false })));
    }
    if (pluginDetail.some((p) => p.enable)) {
      setUseCOT(false);
    }
  }, [pluginDetail, setPluginDetail, setUseCOT]);

  const handlePluginToggle = (id: number) => {
    const updated = pluginDetail.map((p) =>
      p.id === id ? { ...p, enable: !p.enable } : p
    );
    setPluginDetail(updated);
  };

  // 處理檔案選擇
  const handleFileToggle = (filePath: string) => {
    if (selectedFiles.includes(filePath)) {
      setSelectedFiles(selectedFiles.filter((f) => f !== filePath));
    } else {
      setSelectedFiles([...selectedFiles, filePath]);
    }
  };

  // 從路徑中提取檔案名稱
  const getFileName = (filePath: string) => {
    return filePath.split("/").pop() || filePath;
  };

  return (
    <div>
      <div>
        {/* 模型選擇 */}
        <div className="mb-3">
          <label className="text-sm">Select Model</label>
          <select
            className="form-select form-select-sm"
            value={model}
            onChange={(e) => setModel(e.target.value)}
          >
            <option value="openai">OpenAI: gpt-4o-mini</option>
            <option value="ollama">Ollama: llama3.2</option>
          </select>
        </div>

        {/* COT 開關 */}
        <div className="form-check mb-3">
          <input
            className="form-check-input"
            type="checkbox"
            id="cotSwitch"
            checked={useCOT}
            disabled={pluginDetail.some((p) => p.enable)}
            onChange={() => setUseCOT(!useCOT)}
          />
          <label className="form-check-label text-sm" htmlFor="cotSwitch">
            啟用 Chain-of-Thought 推理
          </label>
        </div>

        {/* Plugin 開關 */}
        <div className="mb-3">
          <label className="text-sm">Enable Plugin</label>
          {pluginDetail.map((plugin) => (
            <div className="form-check" key={plugin.id}>
              <input
                className="form-check-input"
                type="checkbox"
                id={`plugin-${plugin.id}`}
                checked={plugin.enable}
                onChange={() => handlePluginToggle(plugin.id)}
              />
              <label
                className="form-check-label text-sm"
                htmlFor={`plugin-${plugin.id}`}
              >
                {plugin.tool_name}
              </label>
            </div>
          ))}
        </div>

        {/* 顯示已上傳的檔案列表 */}
        {uploadedFiles.length > 0 && (
          <div className="mb-3">
            <label className="text-sm">RAG Files Knowledge</label>
            <div className="list-group list-group-sm">
              {uploadedFiles.map((file, index) => (
                <div key={index} className="list-group-item py-1 px-2">
                  <div className="form-check">
                    <input
                      className="form-check-input"
                      type="checkbox"
                      id={`file-${index}`}
                      checked={selectedFiles.includes(file)}
                      onChange={() => handleFileToggle(file)}
                    />
                    <label
                      className="form-check-label text-sm"
                      htmlFor={`file-${index}`}
                    >
                      {getFileName(file)}
                    </label>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default OptionsPanel;
