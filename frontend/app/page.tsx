"use client"

import { useState, useEffect } from "react"
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
import { useToast } from "@/hooks/use-toast"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { ThemeToggle } from "@/components/theme-toggle"
import { CodeEditor } from "@/components/code-editor"

// API URL 설정
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Runtime {
    value: string;
    label: string;
    category: string;
}

export default function ServerlessPlatform() {
    const [open, setOpen] = useState(false)
    const [runtimes, setRuntimes] = useState<Runtime[]>([])
    const [selectedRuntime, setSelectedRuntime] = useState<Runtime | null>(null)
    const [memorySize, setMemorySize] = useState(1024)
    const [timeout, setTimeout] = useState(10)
    const [functionName, setFunctionName] = useState("my-function")
    const [entrypoint, setEntrypoint] = useState("main")
    const [functionCode, setFunctionCode] = useState(
        `def main(event):
    name = event.get('name', 'World')
    return f"Hello {name}!"`,
    )
    const [eventJson, setEventJson] = useState('{\n  "name": "Barq"\n}')
    const [isLoading, setIsLoading] = useState(false)
    const [response, setResponse] = useState<string | null>(null)
    const [performance, setPerformance] = useState<any | null>(null)
    const [error, setError] = useState<string | null>(null)
    const { toast } = useToast()

    // 컴포넌트 마운트시 런타임 목록 가져오기
    useEffect(() => {
        const fetchRuntimes = async () => {
            try {
                const response = await fetch(`${API_URL}/functions/runtimes`)
                const data = await response.json()

                if (response.ok) {
                    setRuntimes(data.runtimes)
                    // 기본 런타임 설정
                    const defaultRuntime = data.runtimes.find((r: Runtime) => r.value === data.default)
                    if (defaultRuntime) {
                        setSelectedRuntime(defaultRuntime)
                    }
                } else {
                    console.error('Failed to fetch runtimes:', data)
                }
            } catch (err) {
                console.error('Error fetching runtimes:', err)
            }
        }

        fetchRuntimes()
    }, [])

    // 런타임별 언어 매핑 함수
    const getLanguageFromRuntime = (runtime: string | undefined) => {
        if (!runtime) return "python"
        if (runtime.includes("python")) return "python"
        if (runtime.includes("node") || runtime.includes("javascript")) return "javascript"
        if (runtime.includes("go")) return "go"
        if (runtime.includes("java")) return "java"
        if (runtime.includes("csharp") || runtime.includes("dotnet")) return "csharp"
        if (runtime.includes("php")) return "php"
        if (runtime.includes("ruby")) return "ruby"
        return "python" // 기본값
    }

    // 함수 배포 API 호출
    const handleDeploy = async () => {
        if (!selectedRuntime) {
            setError('런타임을 선택해주세요.')
            return
        }

        try {
            setIsLoading(true)
            setError(null)
            setResponse(null)
            setPerformance(null)

            console.log('Deploying function with data:', {
                func_id: functionName,
                runtime: selectedRuntime.value,
                entrypoint: entrypoint,
                code: functionCode,
            });

            const response = await fetch(`${API_URL}/functions/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    func_id: functionName,
                    runtime: selectedRuntime.value,
                    entrypoint: entrypoint,
                    code: functionCode,
                }),
            })

            console.log('Deploy response status:', response.status);
            console.log('Deploy response headers:', Object.fromEntries(response.headers.entries()));

            const data = await response.json()
            console.log('Deploy response data:', data);

            if (response.ok) {
                toast({
                    title: "배포 성공",
                    description: `함수 ${functionName}이 성공적으로 배포되었습니다.`,
                })
            } else {
                const errorMessage = data.detail || data.message || JSON.stringify(data) || '알 수 없는 오류';
                setError(`배포 실패: ${errorMessage}`)
            }
        } catch (err) {
            console.error('Deploy error:', err);
            const errorMessage = err instanceof Error ? err.message : JSON.stringify(err);
            setError(`오류 발생: ${errorMessage}`)
        } finally {
            setIsLoading(false)
        }
    }

    // 함수 실행 API 호출
    const handleInvoke = async () => {
        try {
            setIsLoading(true)
            setError(null)
            setPerformance(null)

            // JSON 파싱 시도
            let eventData;
            try {
                eventData = JSON.parse(eventJson);
            } catch (parseError) {
                setError('이벤트 JSON 형식이 올바르지 않습니다. 유효한 JSON을 입력해주세요.');
                setIsLoading(false);
                return;
            }

            // 먼저 함수가 존재하는지 확인
            const checkResponse = await fetch(`${API_URL}/functions/${functionName}`)
            if (checkResponse.status === 404) {
                toast({
                    title: "함수를 찾을 수 없습니다",
                    description: `함수 '${functionName}'이 배포되지 않았습니다. 먼저 함수를 배포해주세요.`,
                    variant: "destructive",
                })
                setIsLoading(false)
                return
            } else if (!checkResponse.ok) {
                const checkData = await checkResponse.json()
                const errorMessage = checkData.detail || checkData.message || '함수 확인 중 오류가 발생했습니다.';
                setError(`함수 확인 실패: ${errorMessage}`)
                setIsLoading(false)
                return
            }

            console.log('Invoking function with data:', {
                func_id: functionName,
                event: eventData
            });

            const response = await fetch(`${API_URL}/functions/${functionName}/invoke`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    event: eventData
                }),
            })

            console.log('Invoke response status:', response.status);
            console.log('Invoke response headers:', Object.fromEntries(response.headers.entries()));

            const data = await response.json()
            console.log('Invoke response data:', data);

            if (response.ok) {
                setResponse(data.output)
                setPerformance(data.performance)
                toast({
                    title: "함수 실행 성공",
                    description: "함수가 성공적으로 실행되었습니다.",
                })
            } else {
                const errorMessage = data.detail || data.message || JSON.stringify(data) || '알 수 없는 오류';
                setError(`실행 실패: ${errorMessage}`)
            }
        } catch (err) {
            console.error('Invoke error:', err);
            const errorMessage = err instanceof Error ? err.message : JSON.stringify(err);
            setError(`오류 발생: ${errorMessage}`)
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="container mx-auto py-10">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold">Barq</h1>
                <ThemeToggle />
            </div>

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
                                    <TabsTrigger value="test">Test Event</TabsTrigger>
                                    <TabsTrigger value="environment">Environment Variables</TabsTrigger>
                                </TabsList>
                                <TabsContent value="code" className="space-y-4">
                                    <div className="space-y-2">
                                        <Label htmlFor="code-editor">Function Code</Label>
                                        <CodeEditor
                                            value={functionCode}
                                            onChange={(value) => setFunctionCode(value || "")}
                                            language={getLanguageFromRuntime(selectedRuntime?.value)}
                                            height="400px"
                                        />
                                    </div>
                                </TabsContent>
                                <TabsContent value="test" className="space-y-4">
                                    <div className="space-y-2">
                                        <Label htmlFor="event-editor">Test Event (JSON)</Label>
                                        <CodeEditor
                                            value={eventJson}
                                            onChange={(value) => setEventJson(value || "")}
                                            language="json"
                                            height="200px"
                                        />
                                        <p className="text-sm text-muted-foreground">
                                            함수 실행시 전달될 이벤트 데이터를 JSON 형식으로 입력하세요.
                                        </p>
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
                                <pre className="bg-muted p-4 rounded-md overflow-auto text-foreground border">{response}</pre>
                            </CardContent>
                        </Card>
                    )}

                    {performance && (
                        <Card className="mt-4">
                            <CardHeader>
                                <CardTitle>성능 메트릭</CardTitle>
                                <CardDescription>함수 실행 성능 정보</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    <div className="space-y-2">
                                        <div className="text-sm font-medium text-muted-foreground">실행 유형</div>
                                        <div className="text-lg font-semibold">
                                            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${performance.execution_type === 'warm'
                                                ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                                                : 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                                                }`}>
                                                {performance.execution_type === 'warm' ? '🔥 Warm' : '❄️ Cold'}
                                            </span>
                                        </div>
                                    </div>

                                    {performance.coldstart_time_ms && (
                                        <div className="space-y-2">
                                            <div className="text-sm font-medium text-muted-foreground">Cold Start</div>
                                            <div className="text-lg font-semibold">{performance.coldstart_time_ms.toFixed(1)}ms</div>
                                        </div>
                                    )}

                                    <div className="space-y-2">
                                        <div className="text-sm font-medium text-muted-foreground">실행 시간</div>
                                        <div className="text-lg font-semibold">{performance.execution_time_ms.toFixed(1)}ms</div>
                                    </div>

                                    <div className="space-y-2">
                                        <div className="text-sm font-medium text-muted-foreground">총 시간</div>
                                        <div className="text-lg font-semibold">{performance.total_time_ms.toFixed(1)}ms</div>
                                    </div>
                                </div>

                                {performance.container_id && (
                                    <div className="mt-4 pt-4 border-t">
                                        <div className="text-sm font-medium text-muted-foreground mb-2">컨테이너 ID</div>
                                        <code className="bg-muted px-2 py-1 rounded text-sm">{performance.container_id}</code>
                                    </div>
                                )}
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
                                <Label htmlFor="entrypoint">Entrypoint</Label>
                                <Input
                                    id="entrypoint"
                                    value={entrypoint}
                                    onChange={(e) => setEntrypoint(e.target.value)}
                                    placeholder="main"
                                />
                                <p className="text-sm text-muted-foreground">
                                    Examples: main, handler.main, index.handler
                                </p>
                            </div>

                            <div className="space-y-2">
                                <Label>Runtime</Label>
                                <Popover open={open} onOpenChange={setOpen}>
                                    <PopoverTrigger asChild>
                                        <Button variant="outline" role="combobox" aria-expanded={open} className="w-full justify-between">
                                            {selectedRuntime ? selectedRuntime.label : "런타임 선택..."}
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
                                                                    selectedRuntime?.value === runtime.value ? "opacity-100" : "opacity-0",
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
