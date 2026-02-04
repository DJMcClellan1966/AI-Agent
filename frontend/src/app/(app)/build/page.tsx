'use client';

import { useState, useRef, useEffect } from 'react';
import { buildApi } from '@/lib/api';
import {
  Sparkles,
  Download,
  Loader2,
  MessageSquare,
  Send,
  CheckCircle2,
  Layers,
} from 'lucide-react';
import { Button } from '@/components/ui/button';

type Message = { role: 'user' | 'system'; content: string };

const SUGGESTIONS = [
  'A personal dashboard that shows my day',
  'A tool to track my reading list',
  'A habit tracker with streaks',
  'A notes app with tagging',
];

export default function BuildPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [generating, setGenerating] = useState(false);
  const [project, setProject] = useState<{
    id: number;
    name: string;
    spec: Record<string, unknown>;
    files: Record<string, string>;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const conversationEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    conversationEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = (text: string) => {
    const t = text.trim();
    if (!t) return;
    setMessages((m) => [...m, { role: 'user', content: t }]);
    setInput('');
    if (inputRef.current) inputRef.current.style.height = 'auto';
  };

  const useSuggestion = (text: string) => {
    setInput(text);
    inputRef.current?.focus();
  };

  const handleGenerate = async () => {
    if (messages.length === 0) {
      setError('Describe what you want to build first, then click Generate.');
      return;
    }
    setError(null);
    setGenerating(true);
    try {
      const { data } = await buildApi.generate({
        messages: messages.map((m) => ({ role: m.role, content: m.content })),
      });
      setProject({
        id: data.id,
        name: data.name,
        spec: data.spec || {},
        files: data.files || {},
      });
      setMessages((m) => [
        ...m,
        {
          role: 'system',
          content: `I've generated "${data.name}" from our conversation. Check the panel on the right for the code and download.`,
        },
      ]);
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } };
      setError(err.response?.data?.detail || 'Generation failed. Try again.');
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = async () => {
    if (!project) return;
    try {
      const { data } = await buildApi.downloadProject(project.id);
      const url = URL.createObjectURL(new Blob([data]));
      const a = document.createElement('a');
      a.href = url;
      a.download = `${project.name}_project.zip`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      setError('Download failed.');
    }
  };

  const fileEntries = project?.files ? Object.entries(project.files) : [];

  return (
    <div className="flex h-[calc(100vh-0px)] overflow-hidden bg-[#0a0a0f] text-[#e8e8ed]">
      {/* Left: Conversation */}
      <div className="flex w-full max-w-[480px] flex-col border-r border-white/10 shrink-0">
        <div className="flex items-center gap-3 border-b border-white/10 px-6 py-4">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 text-lg font-semibold">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-semibold tracking-tight">Build</h1>
            <span className="text-xs text-[#8888a0]">Conversational app creation</span>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-6 flex flex-col gap-5 min-h-0">
          {messages.length === 0 && (
            <div className="flex flex-col items-center text-center py-8">
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 text-3xl mb-5">
                <MessageSquare className="h-8 w-8 text-white" />
              </div>
              <h2 className="text-xl font-semibold mb-2">What would you like to create?</h2>
              <p className="text-sm text-[#8888a0] max-w-sm mb-6">
                Describe your idea in plain language. When you&apos;re ready, click Generate to create a working app from our conversation.
              </p>
              <div className="flex flex-wrap gap-2 justify-center">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    onClick={() => useSuggestion(s)}
                    className="px-4 py-2 rounded-full text-sm bg-white/5 border border-white/10 text-[#8888a0] hover:border-indigo-500/50 hover:text-[#e8e8ed] transition-colors"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-indigo-500 text-white rounded-br-md'
                    : 'bg-white/5 border border-white/10 rounded-bl-md'
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}
          <div ref={conversationEndRef} />
        </div>

        <div className="border-t border-white/10 bg-[#12121a] p-4">
          {error && (
            <p className="text-sm text-red-400 mb-2 px-1">{error}</p>
          )}
          <div className="flex gap-3 items-end">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage(input);
                }
              }}
              placeholder="Describe what you want to create..."
              rows={1}
              className="flex-1 min-h-[52px] max-h-[150px] resize-none rounded-xl border border-white/10 bg-[#1a1a24] px-4 py-3 text-sm text-[#e8e8ed] placeholder:text-[#555568] focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
            />
            <Button
              onClick={() => sendMessage(input)}
              size="icon"
              className="h-[52px] w-[52px] rounded-xl bg-indigo-500 hover:bg-indigo-600 shrink-0"
            >
              <Send className="h-5 w-5" />
            </Button>
          </div>
          <Button
            onClick={handleGenerate}
            disabled={generating || messages.length === 0}
            className="w-full mt-3 h-11 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-medium"
          >
            {generating ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4 mr-2" />
                Generate app from conversation
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Right: Emerging structure / code */}
      <div className="flex-1 flex flex-col min-w-0 bg-[#12121a]">
        <div className="border-b border-white/10 px-6 py-4">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-[#8888a0]">
            Emerging structure
          </h2>
        </div>

        <div className="flex-1 overflow-y-auto p-6 min-h-0">
          {!project && !generating && (
            <div className="flex flex-col items-center justify-center h-full text-[#555568]">
              <Layers className="h-12 w-12 mb-4 opacity-30" />
              <p className="text-sm">Architecture and code will appear here after you generate.</p>
            </div>
          )}

          {generating && (
            <div className="flex items-center gap-3 p-4 rounded-2xl border border-white/10 bg-[#1a1a24] max-w-xs">
              <div className="flex gap-1">
                <span className="h-1.5 w-1.5 rounded-full bg-indigo-500 animate-pulse" style={{ animationDelay: '0ms' }} />
                <span className="h-1.5 w-1.5 rounded-full bg-indigo-500 animate-pulse" style={{ animationDelay: '200ms' }} />
                <span className="h-1.5 w-1.5 rounded-full bg-indigo-500 animate-pulse" style={{ animationDelay: '400ms' }} />
              </div>
              <span className="text-sm text-[#8888a0]">Synthesizing...</span>
            </div>
          )}

          {project && !generating && (
            <>
              <div className="mb-6 flex items-center gap-2 text-[#22c55e]">
                <CheckCircle2 className="h-5 w-5" />
                <span className="font-medium">{project.name} is ready</span>
              </div>

              {project.spec && typeof project.spec === 'object' && Object.keys(project.spec).length > 0 && (
                <div className="mb-6">
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-[#555568] mb-3">Spec</h3>
                  <div className="rounded-xl border border-white/10 bg-[#1a1a24] p-4">
                    <pre className="text-xs text-[#8888a0] overflow-x-auto">
                      {JSON.stringify(project.spec, null, 2)}
                    </pre>
                  </div>
                </div>
              )}

              <div className="space-y-4">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-[#555568]">Generated files</h3>
                {fileEntries.map(([filename, content]) => (
                  <div key={filename} className="rounded-xl border border-white/10 overflow-hidden">
                    <div className="flex justify-between items-center px-4 py-2 bg-[#1a1a24] border-b border-white/10">
                      <span className="font-mono text-xs text-[#8888a0]">{filename}</span>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-semibold">
                        {filename.endsWith('.html') ? 'HTML' : filename.endsWith('.css') ? 'CSS' : 'JS'}
                      </span>
                    </div>
                    <pre className="p-4 font-mono text-xs text-[#8888a0] overflow-x-auto max-h-[280px] overflow-y-auto whitespace-pre-wrap break-words">
                      {content.length > 1200 ? content.slice(0, 1200) + '\n...' : content}
                    </pre>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>

        <div className="border-t border-white/10 p-4">
          <Button
            onClick={handleDownload}
            disabled={!project || generating}
            className="w-full h-12 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-medium disabled:opacity-50 disabled:pointer-events-none"
          >
            <Download className="h-5 w-5 mr-2" />
            Download project
          </Button>
        </div>
      </div>
    </div>
  );
}
