"use client"

import { useState } from "react"
import { Check, ChevronDown, Play, Save } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Slider } from "@/components/ui/slider"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"
import { cn } from "@/lib/utils"
import { useToast } from "@/components/ui/use-toast"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

// API URL 설정
const API_URL = "http://localhost:8000";

const runtimes = [
    { value: "nodejs22.x", label: "Node.js 22.x" },
    { value: "nodejs20.x", label: "Node.js 20.x" },
    { value: "nodejs18.x", label: "Node.js 18.x" },
    { value: "python3.12", label: "Python 3.12" },
    { value: "python3.11", label: "Python 3.11" },
    { value: "go1.x", label: "Go 1.x" },
    { value: "ruby3.2", label: "Ruby 3.2" },
    { value: "java17", label: "Java 17" },
]

export default function ServerlessPlatform() {
    const [open, setOpen] = useState(false)
    const [selectedRuntime, setSelectedRuntime] = useState(runtimes[4]) // Python 3.11을 기본값으로 설정
    const [memorySize, setMemorySize] = useState(1024)
    const [timeout, setTimeout] = useState(10)
    const [functionName, setFunctionName] = useState("my-function")
    const [functionCode, setFunctionCode] = useState(
        `def main(event):
    name = event.get('name', 'World')
    return f"Hello {name}!"`,
    )
    const [isLoading, setIsLoading] = useState(false)
    const [response, setResponse] = useState<string | null>(null)
    const [error, setError] = useState<string | null>(null)
    const { toast } = useToast()

    // 함수 배포 API 호출
    const handleDeploy = async () => {
        try {
            setIsLoading(true)
            setError(null)
            setResponse(null)

            const response = await fetch(`${API_URL}/functions/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    func_id: functionName,
                    runtime: selectedRuntime.value,
                    entrypoint: "main",
                    code: functionCode,
                }),
            })

            const data = await response.json()

            if (response.ok) {
                toast({
                    title: "배포 성공",
                    description: `함수 ${functionName}이 성공적으로 배포되었습니다.`,
                })
            } else {
                setError(`배포 실패: ${data.detail || '알 수 없는 오류'}`)
            }
        } catch (err) {
            setError(`오류 발생: ${err instanceof Error ? err.message : '알 수 없는 오류'}`)
        } finally {
            setIsLoading(false)
        }
    }

    // 함수 실행 API 호출
    const handleInvoke = async () => {
        try {
            setIsLoading(true)
            setError(null)

            const response = await fetch(`${API_URL}/functions/${functionName}/invoke`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    event: { name: "Barq" }
                }),
            })

            const data = await response.json()

            if (response.ok) {
                setResponse(data.output)
                toast({
                    title: "함수 실행 성공",
                    description: "함수가 성공적으로 실행되었습니다.",
                })
            } else {
                setError(`실행 실패: ${data.detail || '알 수 없는 오류'}`)
            }
        } catch (err) {
            setError(`오류 발생: ${err instanceof Error ? err.message : '알 수 없는 오류'}`)
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="container mx-auto py-10">
            <h1 className="text-3xl font-bold mb-6">Barq</h1>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                    <Card>
                        <CardHeader>
                            <CardTitle>Function Code</CardTitle>
                            <CardDescription>Write your serverless function code</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <Tabs defaultValue="code" className="w-full">
                                <TabsList className="mb-4">
                                    <TabsTrigger value="code">Code</TabsTrigger>
                                    <TabsTrigger value="environment">Environment Variables</TabsTrigger>
                                </TabsList>
                                <TabsContent value="code" className="space-y-4">
                                    <div className="space-y-2">
                                        <Label htmlFor="code-editor">Function Code</Label>
                                        <div className="relative">
                                            <Textarea
                                                id="code-editor"
                                                className="font-mono h-[400px] resize-none p-4"
                                                value={functionCode}
                                                onChange={(e) => setFunctionCode(e.target.value)}
                                            />
                                        </div>
                                    </div>
                                </TabsContent>
                                <TabsContent value="environment" className="space-y-4">
                                    <div className="space-y-2">
                                        <Label>Environment Variables</Label>
                                        <div className="grid grid-cols-2 gap-4">
                                            <Input placeholder="KEY" />
                                            <Input placeholder="VALUE" />
                                        </div>
                                        <Button variant="outline" size="sm" className="mt-2">
                                            Add Variable
                                        </Button>
                                    </div>
                                </TabsContent>
                            </Tabs>
                        </CardContent>
                        <CardFooter className="flex justify-between">
                            <Button variant="outline" onClick={handleInvoke} disabled={isLoading}>
                                <Play className="mr-2 h-4 w-4" />
                                Run Function
                            </Button>
                            <Button onClick={handleDeploy} disabled={isLoading}>
                                {isLoading ? "Deploying..." : "Deploy Function"}
                            </Button>
                        </CardFooter>
                    </Card>

                    {error && (
                        <Alert variant="destructive" className="mt-4">
                            <AlertTitle>에러</AlertTitle>
                            <AlertDescription>{error}</AlertDescription>
                        </Alert>
                    )}

                    {response && (
                        <Card className="mt-4">
                            <CardHeader>
                                <CardTitle>실행 결과</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <pre className="bg-slate-100 p-4 rounded-md overflow-auto">{response}</pre>
                            </CardContent>
                        </Card>
                    )}
                </div>

                <div>
                    <Card>
                        <CardHeader>
                            <CardTitle>Function Configuration</CardTitle>
                            <CardDescription>Configure your serverless function</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            <div className="space-y-2">
                                <Label htmlFor="function-name">Function Name</Label>
                                <Input
                                    id="function-name"
                                    value={functionName}
                                    onChange={(e) => setFunctionName(e.target.value)}
                                    placeholder="my-function"
                                />
                            </div>

                            <div className="space-y-2">
                                <Label>Runtime</Label>
                                <Popover open={open} onOpenChange={setOpen}>
                                    <PopoverTrigger asChild>
                                        <Button variant="outline" role="combobox" aria-expanded={open} className="w-full justify-between">
                                            {selectedRuntime.label}
                                            <ChevronDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                                        </Button>
                                    </PopoverTrigger>
                                    <PopoverContent className="w-[200px] p-0">
                                        <Command>
                                            <CommandInput placeholder="Search runtime..." />
                                            <CommandList>
                                                <CommandEmpty>No runtime found.</CommandEmpty>
                                                <CommandGroup>
                                                    {runtimes.map((runtime) => (
                                                        <CommandItem
                                                            key={runtime.value}
                                                            onSelect={() => {
                                                                setSelectedRuntime(runtime)
                                                                setOpen(false)
                                                            }}
                                                        >
                                                            <Check
                                                                className={cn(
                                                                    "mr-2 h-4 w-4",
                                                                    selectedRuntime.value === runtime.value ? "opacity-100" : "opacity-0",
                                                                )}
                                                            />
                                                            {runtime.label}
                                                        </CommandItem>
                                                    ))}
                                                </CommandGroup>
                                            </CommandList>
                                        </Command>
                                    </PopoverContent>
                                </Popover>
                            </div>

                            <div className="space-y-2">
                                <div className="flex justify-between">
                                    <Label htmlFor="memory">Memory Size: {memorySize} MB</Label>
                                </div>
                                <Slider
                                    id="memory"
                                    min={128}
                                    max={3008}
                                    step={64}
                                    value={[memorySize]}
                                    onValueChange={(value) => setMemorySize(value[0])}
                                />
                            </div>

                            <div className="space-y-2">
                                <div className="flex justify-between">
                                    <Label htmlFor="timeout">Timeout: {timeout} seconds</Label>
                                </div>
                                <Slider
                                    id="timeout"
                                    min={1}
                                    max={60}
                                    step={1}
                                    value={[timeout]}
                                    onValueChange={(value) => setTimeout(value[0])}
                                />
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    )
}
