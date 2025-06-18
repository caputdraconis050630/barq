"use client"

import { useTheme } from "next-themes"
import { Editor } from "@monaco-editor/react"
import { useEffect, useState } from "react"

interface CodeEditorProps {
    value: string
    onChange: (value: string | undefined) => void
    language?: string
    height?: string
    placeholder?: string
}

export function CodeEditor({
    value,
    onChange,
    language = "python",
    height = "400px",
    placeholder = "// 코드를 작성하세요..."
}: CodeEditorProps) {
    const { resolvedTheme } = useTheme()
    const [mounted, setMounted] = useState(false)

    // 클라이언트 사이드에서만 렌더링되도록 함
    useEffect(() => {
        setMounted(true)
    }, [])

    // 테마에 따른 Monaco 테마 결정
    const getMonacoTheme = () => {
        switch (resolvedTheme) {
            case "dark":
                return "vs-dark"
            case "orange":
                return "vs" // 오렌지 테마는 밝은 테마 기반
            default:
                return "vs" // 라이트 테마
        }
    }

    // 런타임별 언어 매핑
    const getLanguageFromRuntime = (runtime: string) => {
        if (runtime.includes("python")) return "python"
        if (runtime.includes("node") || runtime.includes("javascript")) return "javascript"
        if (runtime.includes("go")) return "go"
        if (runtime.includes("java")) return "java"
        if (runtime.includes("csharp") || runtime.includes("dotnet")) return "csharp"
        if (runtime.includes("php")) return "php"
        if (runtime.includes("ruby")) return "ruby"
        return "python" // 기본값
    }

    const handleEditorChange = (value: string | undefined) => {
        onChange(value)
    }

    // 에디터 옵션
    const editorOptions = {
        minimap: { enabled: false },
        fontSize: 14,
        lineNumbers: "on" as const,
        roundedSelection: false,
        scrollBeyondLastLine: false,
        automaticLayout: true,
        tabSize: 2,
        insertSpaces: true,
        wordWrap: "on" as const,
        contextmenu: true,
        selectOnLineNumbers: true,
        glyphMargin: false,
        folding: true,
        foldingHighlight: true,
        showFoldingControls: "always" as const,
        bracketPairColorization: {
            enabled: true,
        },
        guides: {
            bracketPairs: true,
            indentation: true,
        },
        suggest: {
            showKeywords: true,
            showSnippets: true,
            showFunctions: true,
            showConstructors: true,
            showFields: true,
            showVariables: true,
            showClasses: true,
            showStructs: true,
            showInterfaces: true,
            showModules: true,
            showProperties: true,
            showEvents: true,
            showOperators: true,
            showUnits: true,
            showValues: true,
            showConstants: true,
            showEnums: true,
            showEnumMembers: true,
            showColors: true,
            showFiles: true,
            showReferences: true,
            showFolders: true,
            showTypeParameters: true,
        },
    }

    if (!mounted) {
        return (
            <div
                className="w-full border border-border rounded-md bg-muted flex items-center justify-center text-muted-foreground"
                style={{ height }}
            >
                코드 에디터 로딩 중...
            </div>
        )
    }

    return (
        <div className="w-full border border-border rounded-md overflow-hidden">
            <Editor
                height={height}
                language={language}
                value={value}
                theme={getMonacoTheme()}
                onChange={handleEditorChange}
                options={editorOptions}
                loading={
                    <div className="w-full h-full flex items-center justify-center bg-muted text-muted-foreground">
                        에디터 로딩 중...
                    </div>
                }
            />
        </div>
    )
} 