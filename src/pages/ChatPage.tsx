import { useState, useRef, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ArrowUp, Sparkles, Mic, Square } from 'lucide-react';
import { DatlyLogo } from '../components/DatlyLogo';
import { WaveBackground } from '../components/WaveBackground';
import { AttachmentButton } from '../components/chat/AttachmentButton';
import { AttachmentPreview, validateFile } from '../components/chat/AttachmentPreview';
import type { Attachment } from '../components/chat/AttachmentPreview';
import { DatasetProcessing } from '../components/chat/DatasetProcessing';
import { DatasetUnderstanding } from '../components/chat/DatasetUnderstanding';
import type { Dataset } from '../lib/datasetParser';
import { uploadDataset, askQuestion, analyzeVoice } from '../services/api';
import type { AnalysisResponse } from '../services/api';
import { AnswerCard } from '../components/chat/AnswerCard';
import { InsightCard } from '../components/chat/InsightCard';
import { LoadingState } from '../components/chat/LoadingState';
import { ErrorState } from '../components/chat/ErrorState';

interface Message {
  id: number;
  role: 'user' | 'assistant';
  text?: string;
  attachment?: Attachment;
  dataset?: Dataset;
  isProcessing?: boolean;
  filename?: string;
  analysis?: AnalysisResponse;
  insight?: string;
  error?: string;
  isLoading?: boolean;
}

export function ChatPage() {
  const location = useLocation();
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [nextId, setNextId] = useState(1);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Attachment & Dataset state
  const [attachmentMenuOpen, setAttachmentMenuOpen] = useState(false);
  const [attachment, setAttachment] = useState<Attachment | null>(null);
  const [activeDatasetId, setActiveDatasetId] = useState<string | null>(null);
  
  // Voice State
  const [voiceState, setVoiceState] = useState<'IDLE' | 'LISTENING' | 'TRANSCRIBING' | 'ANALYZING' | 'RESPONDING'>('IDLE');
  // Close menu when clicking outside
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (!(e.target as Element).closest('#attachment-btn') && !(e.target as Element).closest('[role="menu"]')) {
        setAttachmentMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  // Handle dataset passed from upload page (if any)
  useEffect(() => {
    if (location.state?.dataset && messages.length === 0) {
      // Defer state update to avoid set-state-in-effect warning if rendering synchronously
      const timer = setTimeout(() => {
        setActiveDatasetId(location.state.dataset.id);
      setMessages([
        {
          id: nextId,
          role: 'assistant',
          text: `Dataset received. DATLY is ready to answer questions about ${location.state.dataset.name}.`
        }
      ]);
      setNextId(n => n + 1);
      
      // Clear state so it doesn't re-trigger on refresh
      window.history.replaceState({}, document.title);
      }, 0);
      return () => clearTimeout(timer);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.state?.dataset]);

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 180)}px`;
  }, [input, attachment]);

  // Scroll to bottom on new message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, attachment]);

  const handleFile = (file: File) => {
    const error = validateFile(file);
    setAttachment({ kind: 'file', file, error });
  };


  const isSubmittingRef = useRef(false);

  const handleSubmit = async () => {
    if (isSubmittingRef.current) return;
    const trimmed = input.trim();
    if (!trimmed && !attachment) return;
    if (attachment?.error) return; 
    if (trimmed && !attachment && !activeDatasetId) return; // Prevent submission if no dataset

    isSubmittingRef.current = true;
    try {
      const baseId = nextId;
      setNextId(n => n + 5);

      const userMsgId = baseId;
      const userMessage: Message = { id: userMsgId, role: 'user', text: trimmed, attachment: attachment || undefined };
      
      const activeAttachment = attachment;
      setAttachment(null);
      setInput('');
      
      // Show user message
      setMessages(prev => [...prev, userMessage]);

      let currentDatasetId = activeDatasetId;

      // 1. Handle Upload First
      if (activeAttachment?.kind === 'file') {
        const uploadMsgId = baseId + 1;
        
        setMessages(prev => [
          ...prev,
          { id: uploadMsgId, role: 'assistant', isProcessing: true, filename: activeAttachment.file.name }
        ]);

        try {
          const dataset = await uploadDataset(activeAttachment.file);
          currentDatasetId = dataset.id;
          setActiveDatasetId(dataset.id);

          setMessages(prev => prev.map(m => 
            m.id === uploadMsgId ? { id: m.id, role: 'assistant', dataset } : m
          ));
        } catch {
          setMessages(prev => prev.map(m => 
            m.id === uploadMsgId ? { id: m.id, role: 'assistant', error: 'Failed to upload dataset.' } : m
          ));
          return; // Stop if upload fails
        }
      }

      // 2. Handle Question
      if (trimmed) {
        if (!currentDatasetId) {
          setMessages(prev => [
            ...prev,
            { id: baseId + 2, role: 'assistant', error: 'No dataset selected. Please upload a dataset first.' }
          ]);
          return;
        }

        const qMsgId = baseId + 3;

        setMessages(prev => [
          ...prev,
          { id: qMsgId, role: 'assistant', isLoading: true }
        ]);

        try {
            const response = await askQuestion(currentDatasetId, trimmed);
            setMessages(prev => prev.map(m => 
              m.id === qMsgId ? { id: m.id, role: 'assistant', analysis: response } : m
            ));
        } catch (error: any) {
            setMessages(prev => prev.map(m => 
              m.id === qMsgId ? { id: m.id, role: 'assistant', error: error.message || 'Failed to analyze.' } : m
            ));
        }
      }
    } finally {
      isSubmittingRef.current = false;
    }
  };

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const isVoiceProcessingRef = useRef(false);

  const handleVoice = async () => {
    let currentDatasetId = activeDatasetId;

    if (voiceState === 'LISTENING') {
      mediaRecorderRef.current?.stop();
      return;
    }

    if (voiceState !== 'IDLE' || isVoiceProcessingRef.current) return;
    isVoiceProcessingRef.current = true;

    if (attachment?.kind === 'file') {
      const activeAttachment = attachment;
      setAttachment(null);
      const uploadMsgId = nextId;
      setNextId(n => n + 1);
      
      setMessages(prev => [
        ...prev,
        { id: uploadMsgId, role: 'assistant', isProcessing: true, filename: activeAttachment.file.name }
      ]);

      try {
        const dataset = await uploadDataset(activeAttachment.file);
        currentDatasetId = dataset.id;
        setActiveDatasetId(dataset.id);
        
        setMessages(prev => prev.map(m => 
          m.id === uploadMsgId ? { id: m.id, role: 'assistant', dataset } : m
        ));
      } catch {
        setMessages(prev => prev.map(m => 
          m.id === uploadMsgId ? { id: m.id, role: 'assistant', error: 'Failed to upload dataset.' } : m
        ));
        isVoiceProcessingRef.current = false;
        return;
      }
    }

    if (!currentDatasetId) {
      setMessages(prev => [
        ...prev,
        { id: nextId, role: 'assistant', error: 'No dataset selected. Please upload a dataset first.' }
      ]);
      setNextId(n => n + 1);
      isVoiceProcessingRef.current = false;
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      // Start Web Speech API for visual feedback if supported
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.onresult = (event: any) => {
          const transcript = Array.from(event.results)
            .map((result: any) => result[0].transcript)
            .join('');
          setInput(transcript);
        };
        recognition.start();
        (mediaRecorderRef as any).currentRecognition = recognition;
      }

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        stream.getTracks().forEach(track => track.stop());
        
        if ((mediaRecorderRef as any).currentRecognition) {
          (mediaRecorderRef as any).currentRecognition.stop();
        }
        setInput('');

        if (audioBlob.size === 0) {
           setVoiceState('IDLE');
           return;
        }

        setVoiceState('TRANSCRIBING');
        
        const baseId = nextId;
        setNextId(n => n + 2);
        
        const userMsgId = baseId;
        const qMsgId = baseId + 1;
        
        setMessages(prev => [
          ...prev,
          { id: userMsgId, role: 'user', text: '🎤 Listening...' },
          { id: qMsgId, role: 'assistant', isLoading: true }
        ]);

        try {
          const response = await analyzeVoice(currentDatasetId!, audioBlob);
          
          setVoiceState('RESPONDING');

          setMessages(prev => prev.map(m => {
            if (m.id === userMsgId) {
              return { ...m, text: response.transcript || '(Audio message)' };
            }
            if (m.id === qMsgId) {
              return { id: m.id, role: 'assistant', analysis: response };
            }
            return m;
          }));
          
        } catch {
          setMessages(prev => prev.map(m => 
            m.id === qMsgId ? { id: m.id, role: 'assistant', error: 'Failed to process voice request.' } : m
          ));
        } finally {
          setVoiceState('IDLE');
          isVoiceProcessingRef.current = false;
        }
      };

      mediaRecorder.start();
      setVoiceState('LISTENING');

    } catch {
      console.error('Error accessing microphone');
      setMessages(prev => [
        ...prev,
        { id: nextId, role: 'assistant', error: 'Microphone access denied or unavailable.' }
      ]);
      setNextId(n => n + 1);
      isVoiceProcessingRef.current = false;
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const isEmpty = input.trim().length === 0 && !attachment;
  const isMissingDataset = input.trim().length > 0 && !attachment && !activeDatasetId;
  const isDisabled = isEmpty || !!attachment?.error || isMissingDataset;

  return (
    <div className="h-screen h-[100dvh] w-full flex flex-col bg-[#141414] text-white font-sans overflow-hidden relative">
      <WaveBackground />

      {/* Navbar */}
      <nav className="w-full flex items-center justify-between py-6 px-6 md:px-12 max-w-7xl mx-auto z-10 relative shrink-0">
        <Link to="/" className="flex items-center gap-2 scale-[0.35] origin-left -ml-4 md:ml-0 hover:opacity-80 transition-opacity">
          <DatlyLogo reducedMotion={true} />
        </Link>

        
        {/* Active Dataset Context */}
        <div className="flex items-center justify-end flex-1 md:flex-none">
          {activeDatasetId && (() => {
            const activeDataset = messages.find(m => m.dataset?.id === activeDatasetId)?.dataset;
            if (!activeDataset) return null;
            return (
              <div className="flex items-center gap-2 bg-white/5 border border-white/10 rounded-full px-3 py-1.5 shadow-sm">
                <span className="text-sm">📊</span>
                <span className="text-xs text-white/90 font-medium truncate max-w-[100px]">{activeDataset.name}</span>
                <span className="text-white/20 text-xs px-1">•</span>
                <span className="text-white/40 text-xs font-mono">{activeDataset.rows.toLocaleString()} rows</span>
              </div>
            );
          })()}
        </div>
      </nav>

      {/* Main */}
      <main className="flex-1 min-h-0 flex flex-col relative z-10 w-full max-w-3xl mx-auto px-4 md:px-6 pb-8">

        {/* Welcome section — only show when no messages yet */}
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center flex-1 text-center py-16">


            <h1 className="text-3xl md:text-4xl font-semibold text-[#f3f2ee] mb-4 tracking-tight">
              What would you like to discover?
            </h1>
            <p className="text-white/50 text-base md:text-lg max-w-md leading-relaxed font-light">
              Ask questions about your datasets in plain English. DATLY will find patterns, trends, and insights instantly.
            </p>


          </div>
        )}

        {/* Message thread */}
        {messages.length > 0 && (
          <div className="flex-1 py-8 space-y-6 overflow-y-auto" style={{ scrollbarWidth: 'none' }}>
            {messages.map((msg) =>
              msg.role === 'user' ? (
                <div key={msg.id} className="flex justify-end">
                  <div className="max-w-[80%] flex flex-col items-end gap-2">
                    {msg.attachment && (
                      <div className="pointer-events-none">
                         <AttachmentPreview attachment={msg.attachment} onRemove={() => {}} />
                      </div>
                    )}
                    {msg.text && (
                       <div className="bg-white/8 border border-white/10 rounded-2xl rounded-br-sm px-5 py-3 text-sm text-white/90 leading-relaxed whitespace-pre-wrap">
                        {msg.text}
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div key={msg.id} className="flex items-start gap-3">
                  <div className="shrink-0 w-8 h-8 rounded-xl bg-gradient-to-br from-[#7c3aed] to-[#f97316] flex items-center justify-center mt-0.5">
                    <Sparkles size={14} className="text-white" strokeWidth={1.8} />
                  </div>
                  <div className="max-w-[82%] border border-white/10 bg-white/4 rounded-2xl rounded-tl-sm px-5 py-3 text-sm text-white/80 leading-relaxed whitespace-pre-wrap">
                    {msg.isProcessing ? (
                       <DatasetProcessing filename={msg.filename || 'dataset'} />
                    ) : msg.isLoading ? (
                       <LoadingState />
                    ) : msg.error ? (
                       <ErrorState message={msg.error} />
                    ) : msg.dataset ? (
                       <div>
                         <DatasetUnderstanding dataset={msg.dataset} />
                         {msg.insight && <InsightCard insight={msg.insight} />}
                       </div>
                    ) : msg.analysis ? (
                       <AnswerCard analysis={msg.analysis} onClarify={(opt) => {
                         setInput(opt.label);
                         // Delay to allow state update then submit
                         setTimeout(() => document.getElementById('chat-send-btn')?.click(), 100);
                       }} />
                    ) : (
                       msg.text
                    )}
                  </div>
                </div>
              )
            )}
            <div ref={bottomRef} />
          </div>
        )}

        {/* Input bar */}
        <div className={messages.length > 0 ? 'mt-auto sticky bottom-6' : 'mt-auto'}>
          <div className="relative group">
            {/* Voice Pill */}
            {voiceState !== 'IDLE' && (
              <div className="absolute -top-12 left-1/2 -translate-x-1/2 px-4 py-2 rounded-full bg-[#1c1c1c] border border-white/10 shadow-[0_4px_24px_rgba(0,0,0,0.5)] flex items-center gap-2.5 z-20 animate-in slide-in-from-bottom-2 fade-in duration-200">
                <div className="flex gap-1 items-center h-3">
                  <div className="w-1 bg-[#f97316] rounded-full animate-[pulse_1s_infinite_100ms] h-full" />
                  <div className="w-1 bg-[#f97316] rounded-full animate-[pulse_1s_infinite_300ms] h-2/3" />
                  <div className="w-1 bg-[#f97316] rounded-full animate-[pulse_1s_infinite_200ms] h-full" />
                </div>
                <span className="text-xs text-white/80 font-medium tracking-wide">
                  {voiceState === 'LISTENING' ? 'Listening...' : 
                   voiceState === 'TRANSCRIBING' ? 'Transcribing...' :
                   voiceState === 'ANALYZING' ? 'Analyzing...' :
                   voiceState === 'RESPONDING' ? 'Speaking...' : ''}
                </span>
              </div>
            )}
            
            {/* Gradient border glow on focus */}
            <div
              className="absolute -inset-[1px] rounded-2xl opacity-0 group-focus-within:opacity-100 transition-opacity duration-300 pointer-events-none"
              style={{
                background: 'linear-gradient(135deg, #7c3aed, #8b5cf6, #f97316)',
                borderRadius: '1rem',
                zIndex: 0,
              }}
            />

            <div className="relative z-10 flex flex-col bg-[#1c1c1c] rounded-2xl border border-white/10 group-focus-within:border-transparent transition-colors shadow-lg">
              
              {/* Attachment Preview Area */}
              {attachment && (
                <div className="px-4 pt-3 pb-1 border-b border-white/5">
                   <AttachmentPreview attachment={attachment} onRemove={() => setAttachment(null)} />
                </div>
              )}

              <div className="flex items-end gap-3 px-4 py-3">
                <AttachmentButton
                  open={attachmentMenuOpen}
                  onToggle={() => setAttachmentMenuOpen(!attachmentMenuOpen)}
                  onFile={handleFile}
                />

                <textarea
                  ref={textareaRef}
                  id="chat-input"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={attachment ? "Add a message..." : "Find insights. Just ask…"}
                  rows={1}
                  className="flex-1 bg-transparent resize-none outline-none text-white/90 placeholder-white/30 text-sm leading-relaxed max-h-[180px] overflow-y-auto py-1.5"
                  style={{ scrollbarWidth: 'none' }}
                />

                <div className="flex items-center gap-2 pb-0.5">
                    <button 
                     onClick={handleVoice}
                     className={`w-8 h-8 rounded-lg flex items-center justify-center transition-colors ${
                       voiceState === 'LISTENING' ? 'text-red-400 bg-red-400/10 animate-pulse' : 
                       voiceState === 'TRANSCRIBING' ? 'text-[#a78bfa] bg-[#a78bfa]/10 animate-pulse' :
                       'text-white/35 hover:text-white/70 hover:bg-white/6'
                     }`}
                     title={voiceState === 'IDLE' ? "Start voice input" : voiceState === 'LISTENING' ? "Stop voice input" : voiceState}
                   >
                      {voiceState === 'LISTENING' ? (
                        <Square size={14} fill="currentColor" strokeWidth={0} />
                      ) : (
                        <Mic size={16} strokeWidth={2} />
                      )}
                   </button>
                  <button
                    id="chat-send-btn"
                    onClick={handleSubmit}
                    disabled={isDisabled}
                    className={`shrink-0 w-9 h-9 rounded-xl flex items-center justify-center transition-all duration-200
                      ${isDisabled
                        ? 'bg-white/5 text-white/20 cursor-not-allowed'
                        : 'bg-gradient-to-br from-[#7c3aed] to-[#f97316] text-white hover:scale-105 shadow-[0_0_14px_rgba(139,92,246,0.4)] hover:shadow-[0_0_20px_rgba(139,92,246,0.6)]'
                      }`}
                  >
                    <ArrowUp size={16} strokeWidth={2.5} />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <p className="text-center text-white/20 text-xs mt-3">
            Press <kbd className="font-mono bg-white/5 border border-white/10 rounded px-1">Enter</kbd> to send · <kbd className="font-mono bg-white/5 border border-white/10 rounded px-1">Shift+Enter</kbd> for new line
          </p>
        </div>
      </main>
    </div>
  );
}
