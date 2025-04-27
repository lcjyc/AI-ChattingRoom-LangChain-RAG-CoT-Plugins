"use client";

import { useRef, useState } from "react";
import { uploadFile } from "../utils/api";

type FileUploaderProps = {
  file: File | null;
  setFile: (file: File | null) => void;
  onUploadSuccess: () => void;
};

const FileUploader = ({
  file,
  setFile,
  onUploadSuccess,
}: FileUploaderProps) => {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    setFile(file);
  };

  const handleClear = () => {
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
    setFile(null);
  };

  const handleFileUpload = async () => {
    if (file) {
      try {
        setIsUploading(true);
        await uploadFile(file);
        // 上傳成功後更新檔案列表
        onUploadSuccess();
      } catch (error) {
        console.error("File Upload Failed:", error);
      } finally {
        handleClear();
        setIsUploading(false);
      }
    }
  };

  return (
    <div className="space-y-3">
      <label htmlFor="fileUpload" className="text-sm d-block mb-2">
        Upload RAG File (.txt, .pdf, .csv)
      </label>
      <input
        type="file"
        id="fileUpload"
        className="form-control form-control-sm"
        accept=".txt,.pdf,.csv"
        onChange={handleFileChange}
        ref={fileInputRef}
        disabled={isUploading}
      />
      <div className="d-flex gap-2">
        <button
          type="button"
          className="btn btn-sm btn-outline-light mt-2"
          onClick={handleClear}
        >
          Clear File
        </button>
        <button
          type="button"
          className="btn btn-sm btn-light mt-2"
          onClick={handleFileUpload}
        >
          {isUploading ? (
            <>
              <span
                className="spinner-border spinner-border-sm me-1"
                role="status"
                aria-hidden="true"
              ></span>
              Uploading
            </>
          ) : (
            "Upload file"
          )}
        </button>
      </div>
    </div>
  );
};

export default FileUploader;
