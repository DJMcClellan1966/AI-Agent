'use client';

import { useState, useRef, useEffect, useMemo } from 'react';
import { agentApi, type PendingApproval, type AgentContext } from '@/lib/api';
import { Bot, Send, Loader2, ShieldCheck, X, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';

type DisplayMessage = { role: 'user' | 'assistant'; content: string };

export default function AgentPage() {
  const [displayMessages, setDisplayMessages] = useState<DisplayMessage[]>([]);
  const [fullMessages, setFullMessages] = useState<Record<string, string>[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pendingApproval, setPendingApproval] = useState<PendingApproval | null>(null);
  const [workspaceRoot, setWorkspaceRoot] = useState('');
  const [autonomous, setAutonomous] = useState(false);
  const [agentStyle] = useState<string>('opus_like');
  const conversationEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    conversationEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [displayMessages, pendingApproval]);

  const context = useMemo<AgentContext | undefined>(() => {
    const base: AgentContext = { agent_style: agentStyle };
    if (workspaceRoot) base.workspace_root = workspaceRoot;
    if (autonomous) base.autonomous = true;
    return base;
  }, [agentStyle, workspaceRoot, autonomous]);

  const sendToAgent = async (messagesForApi: Record<string, string>[]) => {
    setError(null);
    setLoading(true);
    try {
      const { data } = await agentApi.chat({ messages: messagesForApi, context });
      setFullMessages(data.messages || []);
      if (data.reply) {
        setDisplayMessages((m) => [...m, { role: 'assistant', content: data.reply! }]);
      }
      if (data.pending_approval) {
        setDisplayMessages((m) => [...m, { role: 'assistant', content: `Waiting for your approval to run **${data.pending_approval.tool}**.` }]);
      }
      setPendingApproval(data.pending_approval || null);
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } };
      setError(err.response?.data?.detail || 'Agent request failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async () => {
    const text = input.trim();
    if (!text || loading) return;
    const userMsg = { role: 'user', content: text };
    setDisplayMessages((m) => [...m, userMsg]);
    setInput('');
    const nextFull = fullMessages.length ? [...fullMessages, userMsg] : [userMsg];
    await sendToAgent(nextFull);
  };

  const handleApprove = async () => {
    if (!pendingApproval || loading) return;
    setLoading(true);
    setError(null);
    try {
      const { data } = await agentApi.executePending({
        messages: fullMessages,
        context,
        tool: pendingApproval.tool,
        args: pendingApproval.args as Record<string, unknown>,
      });
      setFullMessages(data.messages || []);
      setPendingApproval(data.pending_approval || null);
      if (data.reply) {
        setDisplayMessages((m) => [...m, { role: 'assistant', content: data.reply! }]);
      }
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } };
      setError(err.response?.data?.detail || 'Execute failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-0px)] overflow-hidden bg-[#0a0a0f] text-[#e8e8ed]">
      <div className="flex w-full max-w-[520px] flex-col border-r border-white/10 shrink-0">
        <div className="flex items-center justify-between gap-3 border-b border-white/10 px-6 py-4">
          <div className="flex items-center gap-3 min-w-0">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 shrink-0">
              <Bot className="h-5 w-5 text-white" />
            </div>
            <div className="min-w-0">
              <h1 className="text-lg font-semibold tracking-tight">Agent</h1>
              <span className="text-xs text-[#8888a0]">Opus-like · edit/run require approval</span>
            </div>
          </div>
          <label className="flex items-center gap-2 cursor-pointer shrink-0" title="Edit and run without asking.">
            <Zap className="h-4 w-4 text-[#8888a0]" />
            <span className="text-xs text-[#8888a0]">Autonomous</span>
            <input
              type="checkbox"
              checked={autonomous}
              onChange={(e) => setAutonomous(e.target.checked)}
              className="rounded border-white/20 bg-[#0a0a0f] text-amber-500 focus:ring-amber-500"
            />
          </label>
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-6 flex flex-col gap-4 min-h-0">
          {displayMessages.length === 0 && !loading && (
            <div className="flex flex-col items-center text-center py-12">
              <Bot className="h-14 w-14 text-[#555568] mb-4 opacity-50" />
              <h2 className="text-lg font-semibold mb-2">Chat with the agent</h2>
              <p className="text-sm text-[#8888a0] max-w-sm mb-4">
                Ask for code changes, run commands, or generate an app. Set workspace root so the agent can read/edit files.
              </p>
              <div className="w-full max-w-xs">
                <label className="text-xs text-[#555568] block mb-1">Workspace root</label>
                <input
                  type="text"
                  value={workspaceRoot}
                  onChange={(e) => setWorkspaceRoot(e.target.value)}
                  placeholder="C:\path\to\project"
                  className="w-full rounded-lg border border-white/10 bg-[#1a1a24] px-3 py-2 text-sm text-[#e8e8ed] placeholder:text-[#555568] focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>
          )}

          {displayMessages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                  msg.role === 'user' ? 'bg-indigo-500 text-white rounded-br-md' : 'bg-white/5 border border-white/10 rounded-bl-md'
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}

          {pendingApproval && (
            <div className="rounded-xl border border-amber-500/50 bg-amber-500/10 p-4 space-y-3">
              <div className="flex items-center gap-2 text-amber-400">
                <ShieldCheck className="h-5 w-5" />
                <span className="font-medium">Approval: {pendingApproval.tool}</span>
              </div>
              <pre className="text-xs text-[#8888a0] whitespace-pre-wrap overflow-x-auto max-h-48 overflow-y-auto bg-[#0a0a0f] rounded-lg p-3">
                {pendingApproval.preview}
              </pre>
              <div className="flex gap-2">
                <Button onClick={handleApprove} disabled={loading} className="bg-emerald-600 hover:bg-emerald-700 text-white">
                  {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Approve'}
                </Button>
                <Button onClick={() => setPendingApproval(null)} disabled={loading} variant="outline" className="border-white/20 text-[#e8e8ed]">
                  <X className="h-4 w-4 mr-1" /> Cancel
                </Button>
              </div>
            </div>
          )}

          {error && <p className="text-sm text-red-400 px-1">{error}</p>}
          <div ref={conversationEndRef} />
        </div>

        <div className="border-t border-white/10 bg-[#12121a] p-4">
          <div className="flex gap-3 items-end">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
              placeholder="Ask the agent..."
              rows={1}
              className="flex-1 min-h-[52px] max-h-[150px] resize-none rounded-xl border border-white/10 bg-[#1a1a24] px-4 py-3 text-sm text-[#e8e8ed] placeholder:text-[#555568] focus:outline-none focus:border-indigo-500"
            />
            <Button onClick={handleSend} disabled={loading || !input.trim()} size="icon" className="h-[52px] w-[52px] rounded-xl bg-indigo-500 hover:bg-indigo-600 shrink-0">
              {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
            </Button>
          </div>
        </div>
      </div>

      <div className="flex-1 flex flex-col min-w-0 bg-[#12121a] px-6 py-4">
        <p className="text-sm text-[#555568]">
          Agent uses workspace root for read_file, edit_file, run_terminal. Approve edits and commands when prompted.
        </p>
      </div>
    </div>
  );
}
