'use client';

import { useState, useCallback, useEffect } from 'react';
import { workspaceApi, agentApi, type AgentContext } from '@/lib/api';
import { Bot, Send, Loader2, Folder, FileText, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

type Message = { role: 'user' | 'assistant'; content: string };

export default function IDEPage() {
  const [workspaceRoot, setWorkspaceRoot] = useState('');
  const [listPath, setListPath] = useState('.');
  const [entries, setEntries] = useState<string[]>([]);
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState('');
  const [loadingFile, setLoadingFile] = useState(false);
  const [treeLoading, setTreeLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);

  const loadList = useCallback(async (path: string) => {
    if (!workspaceRoot) return;
    setTreeLoading(true);
    try {
      const { data } = await workspaceApi.list(workspaceRoot, path);
      setEntries(data.entries);
      setListPath(path);
    } catch {
      setEntries([]);
    } finally {
      setTreeLoading(false);
    }
  }, [workspaceRoot]);

  useEffect(() => {
    if (workspaceRoot) loadList('.');
    else setEntries([]);
  }, [workspaceRoot, loadList]);

  const handleEntryClick = async (name: string) => {
    if (!workspaceRoot) return;
    if (name === '..') {
      const up = listPath === '.' ? '.' : listPath.split('/').slice(0, -1).join('/') || '.';
      loadList(up);
      return;
    }
    const path = listPath === '.' ? name : `${listPath}/${name}`;
    setTreeLoading(true);
    try {
      const { data } = await workspaceApi.list(workspaceRoot, path);
      setEntries(data.entries);
      setListPath(path);
    } catch {
      try {
        setLoadingFile(true);
        const { data } = await workspaceApi.read(workspaceRoot, path);
        setSelectedPath(path);
        setFileContent(data.content);
      } catch {
        setSelectedPath(null);
        setFileContent('');
      } finally {
        setLoadingFile(false);
      }
    } finally {
      setTreeLoading(false);
    }
  };

  const handleFileClick = async (path: string) => {
    if (!workspaceRoot) return;
    setLoadingFile(true);
    setSelectedPath(path);
    try {
      const { data } = await workspaceApi.read(workspaceRoot, path);
      setFileContent(data.content);
    } catch {
      setFileContent('');
    } finally {
      setLoadingFile(false);
    }
  };

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || chatLoading) return;
    setInput('');
    setMessages((m) => [...m, { role: 'user', content: text }]);
    setChatLoading(true);
    const fullMessages = [...messages, { role: 'user' as const, content: text }];
    const context: AgentContext = {
      workspace_root: workspaceRoot || undefined,
      agent_style: 'opus_like',
    };
    try {
      const { data } = await agentApi.chat({
        messages: fullMessages.map((x) => ({ role: x.role, content: x.content })),
        context,
      });
      const reply = data.reply ?? 'No response.';
      setMessages((m) => [...m, { role: 'assistant', content: reply }]);
    } catch {
      setMessages((m) => [...m, { role: 'assistant', content: 'Request failed. Check workspace root and backend.' }]);
    } finally {
      setChatLoading(false);
    }
  };

  const isLikelyDir = (name: string) => !name.includes('.');

  return (
    <div className="flex h-[calc(100vh-0px)] bg-[#0a0a0f] text-[#e8e8ed]">
      {/* File tree */}
      <div className="w-64 border-r border-white/10 flex flex-col shrink-0">
        <div className="p-3 border-b border-white/10">
          <label className="text-xs text-[#8888a0] block mb-1">Workspace root</label>
          <input
            type="text"
            value={workspaceRoot}
            onChange={(e) => setWorkspaceRoot(e.target.value)}
            placeholder="C:\path\to\project"
            className="w-full px-3 py-2 rounded-lg bg-[#1a1a24] border border-white/10 text-sm focus:outline focus:border-indigo-500"
          />
        </div>
        <div className="flex-1 overflow-y-auto p-2">
          {treeLoading ? (
            <div className="flex items-center gap-2 text-[#555568] text-sm py-2">
              <Loader2 className="h-4 w-4 animate-spin" /> Loading…
            </div>
          ) : (
            <div className="space-y-0.5">
              {listPath !== '.' && (
                <button
                  onClick={() => handleEntryClick('..')}
                  className="flex items-center gap-2 w-full px-2 py-1.5 rounded text-left text-sm hover:bg-white/5 text-[#8888a0]"
                >
                  <ChevronRight className="h-4 w-4 rotate-[-90deg]" /> ..
                </button>
              )}
              {entries.map((name) => {
                const isDir = isLikelyDir(name);
                const path = listPath === '.' ? name : `${listPath}/${name}`;
                return (
                  <button
                    key={name}
                    onClick={() => (isDir ? handleEntryClick(name) : handleFileClick(path))}
                    className="flex items-center gap-2 w-full px-2 py-1.5 rounded text-left text-sm hover:bg-white/5"
                  >
                    {isDir ? <Folder className="h-4 w-4 text-amber-500" /> : <FileText className="h-4 w-4 text-[#8888a0]" />}
                    <span className="truncate">{name}</span>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Editor */}
      <div className="flex-1 flex flex-col min-w-0 border-r border-white/10">
        <div className="px-4 py-2 border-b border-white/10 text-xs text-[#8888a0]">
          {selectedPath ?? 'Select a file'}
        </div>
        <div className="flex-1 overflow-hidden">
          {loadingFile ? (
            <div className="p-4 flex items-center gap-2 text-[#555568]">
              <Loader2 className="h-4 w-4 animate-spin" /> Loading file…
            </div>
          ) : (
            <textarea
              readOnly
              value={fileContent}
              className="w-full h-full p-4 bg-[#0a0a0f] text-sm font-mono text-[#e8e8ed] resize-none focus:outline-none"
              placeholder="Open a file from the tree"
              spellCheck={false}
            />
          )}
        </div>
      </div>

      {/* Agent chat */}
      <div className="w-96 flex flex-col shrink-0 bg-[#12121a]">
        <div className="px-4 py-3 border-b border-white/10 flex items-center gap-2">
          <Bot className="h-5 w-5 text-indigo-400" />
          <span className="font-medium">Agent (Opus-like · qwen3:8b)</span>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {messages.length === 0 && (
            <p className="text-sm text-[#555568]">
              Chat with the agent. Set a workspace root so it can read/edit files and run commands. Uses Ollama qwen3:8b with Opus-like prompting.
            </p>
          )}
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`rounded-xl px-3 py-2 text-sm ${msg.role === 'user' ? 'bg-indigo-500/20 ml-8' : 'bg-white/5 mr-8'}`}
            >
              {msg.content}
            </div>
          ))}
          {chatLoading && (
            <div className="flex items-center gap-2 text-[#555568] text-sm">
              <Loader2 className="h-4 w-4 animate-spin" /> Thinking…
            </div>
          )}
        </div>
        <div className="p-4 border-t border-white/10 flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
            placeholder="Ask the agent…"
            className="flex-1 px-3 py-2 rounded-lg bg-[#1a1a24] border border-white/10 text-sm focus:outline focus:border-indigo-500"
          />
          <Button onClick={sendMessage} disabled={chatLoading} className="shrink-0 bg-indigo-500 hover:bg-indigo-600">
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
