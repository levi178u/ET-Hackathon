import { useState, useRef, useEffect, useContext } from 'react';
import { Sparkles, X, Send, Volume2, Maximize2, Loader2, Minus, MousePointer2 } from 'lucide-react';
import axios from 'axios';
import { clsx } from 'clsx';
import { motion, AnimatePresence } from 'framer-motion';
import { AuthContext } from '../context/AuthContext';

export default function SquirrelChat() {
  const { user, API_BASE_URL } = useContext(AuthContext);
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hey there! I\'m **Squirrel** 🐿️ — your personal news companion. I can:\n• **Explain news** in simple terms\n• **Read articles aloud** for you\n• **Quiz you** on current affairs\n\nWhat would you like to know?'
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [audioLoading, setAudioLoading] = useState({});
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = useCallback(async (text) => {
    const textToSend = text || input;
    if (!textToSend.trim()) return;

    setMessages(prev => [...prev, { role: 'user', content: textToSend }]);
    setInput('');
    setIsLoading(true);

    try {
      const { data } = await axios.post(`${API_BASE_URL}/api/assistant/chat`, { 
        message: textToSend,
        role_context: user?.role || 'Student',
        history: messages.slice(-4).map(m => `${m.role.toUpperCase()}: ${m.content}`).join('\n')
      });
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { role: 'assistant', content: "Oops! I couldn't reach the server right now 🐿️" }]);
    } finally {
      setIsLoading(false);
    }
  }, [API_BASE_URL, input, messages, user?.role]);

  useEffect(() => {
    const handleExplain = (e) => {
      const { text } = e.detail;
      setIsOpen(true);
      handleSend(text);
    };
    window.addEventListener('squirrel-explain', handleExplain);
    return () => window.removeEventListener('squirrel-explain', handleExplain);
  }, [handleSend]);

  const handleListen = async (text, index) => {
    setAudioLoading(prev => ({ ...prev, [index]: true }));
    try {
      const { data } = await axios.post(`${API_BASE_URL}/api/assistant/tts`, { text });
      if (data.audio_base64) {
        const audio = new Audio(data.audio_base64);
        audio.play();
      }
    } catch (err) {
      console.error("TTS failed", err);
    } finally {
      setAudioLoading(prev => ({ ...prev, [index]: false }));
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSend();
  };

  if (!isOpen) {
    return (
      <button 
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 p-0 rounded-full shadow-lg flex items-center justify-center transition-all hover:scale-110 active:scale-95 z-50 overflow-hidden border-2 border-primary/20"
      >
        <img 
          src="/sq1.png" 
          alt="Squirrel" 
          className="w-16 h-16 object-cover"
        />
        <div className="absolute inset-0 bg-primary/10 hover:bg-transparent transition-colors" />
      </button>
    );
  }

  return (
    <motion.div 
      drag
      dragMomentum={false}
      dragElastic={0.1}
      dragTransition={{ bounceStiffness: 600, bounceDamping: 20 }}
      whileDrag={{ scale: 1.02 }}
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ 
        opacity: 1, 
        y: 0, 
        scale: 1,
        width: isMinimized ? 256 : (window.innerWidth < 768 ? 320 : 384),
        height: isMinimized ? 56 : 'auto'
      }}
      className="fixed bottom-6 right-6 bg-surface border border-surfaceHover rounded-xl shadow-2xl flex flex-col overflow-hidden z-[100] transition-shadow duration-300"
      style={{ touchAction: 'none' }}
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-orange-500 to-primary p-3 flex items-center justify-between text-white cursor-grab active:cursor-grabbing shrink-0 select-none">
        <div className="flex items-center space-x-3 pointer-events-none">
          <div className="relative">
            <img 
              src={isLoading ? "/sq2.png" : "/sq1.png"} 
              alt="Squirrel" 
              className={clsx(
                "w-10 h-10 rounded-full border-2 border-white/20 bg-white/10 shadow-inner",
                isLoading && "animate-bounce"
              )}
            />
          </div>
          <div>
            <div className="flex items-center space-x-1">
               <h3 className="font-bold text-sm leading-tight">Squirrel</h3>
               <Sparkles size={10} className="text-white/70 animate-pulse" />
            </div>
            <p className="text-[10px] opacity-90">{isLoading ? 'Writing thoughts...' : 'AI News Companion'}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button 
            onClick={(e) => { e.stopPropagation(); setIsMinimized(!isMinimized); }} 
            className="p-1.5 hover:bg-white/20 rounded-lg transition-colors"
            title={isMinimized ? "Maximize" : "Minimize"}
          >
            {isMinimized ? <Maximize2 size={16} /> : <Minus size={16} />}
          </button>
          <button 
            onClick={(e) => { e.stopPropagation(); setIsOpen(false); }} 
            className="p-1.5 hover:bg-white/20 rounded-lg transition-colors"
            title="Close"
          >
            <X size={18} />
          </button>
        </div>
      </div>

      <AnimatePresence>
        {!isMinimized && (
          <motion.div 
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="flex flex-col flex-1"
          >
            {/* Chat Area */}
            <div className="flex-1 p-4 overflow-y-auto h-[350px] flex flex-col space-y-4 bg-background/50 scrollbar-thin scrollbar-thumb-surfaceHover">
              {messages.map((msg, i) => (
                <div key={i} className={clsx(
                  "max-w-[90%] rounded-xl p-3 text-sm flex flex-col group shadow-sm",
                  msg.role === 'assistant' 
                    ? "bg-surface text-textDefault self-start rounded-tl-sm border border-border" 
                    : "bg-primary text-white self-end rounded-tr-sm"
                )}>
                  <div className="whitespace-pre-wrap leading-relaxed">{msg.content}</div>
                  
                  {msg.role === 'assistant' && (
                    <button 
                      onClick={() => handleListen(msg.content, i)}
                      disabled={audioLoading[i]}
                      className="mt-2 text-textMuted hover:text-primary transition-colors flex items-center space-x-1 self-start opacity-0 group-hover:opacity-100 disabled:opacity-50"
                    >
                      {audioLoading[i] ? <Loader2 size={12} className="animate-spin" /> : <Volume2 size={12} />}
                      <span className="text-xs">{audioLoading[i] ? 'Generating...' : 'Listen'}</span>
                    </button>
                  )}
                </div>
              ))}
              {isLoading && (
                <div className="bg-surface text-textDefault self-start rounded-xl rounded-tl-sm px-4 py-3 border border-border flex items-center space-x-2">
                  <Loader2 className="w-4 h-4 animate-spin text-primary" />
                  <span className="text-sm opacity-80">Squirrel is thinking...</span>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Suggestions */}
            <div className="px-4 py-3 border-t border-border bg-surface overflow-x-auto whitespace-nowrap scrollbar-hide flex gap-2 w-full">
              <button onClick={() => handleSend("Explain today's top story")} className="bg-background border border-border hover:border-primary/50 text-textMuted hover:text-textDefault px-3 py-1.5 rounded-full text-xs transition-colors">Explain top story</button>
              <button onClick={() => handleSend("Quiz me on today's news")} className="bg-background border border-border hover:border-primary/50 text-textMuted hover:text-textDefault px-3 py-1.5 rounded-full text-xs transition-colors">Quiz me</button>
            </div>

            {/* Input Area */}
            <div className="p-3 bg-surface border-t border-border flex items-center space-x-2">
              <input 
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={isLoading}
                placeholder="Ask Squirrel anything..."
                className="flex-1 bg-background border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary transition-colors text-textDefault placeholder-textMuted disabled:opacity-50"
              />
              <button 
                onClick={() => handleSend()}
                disabled={!input.trim() || isLoading}
                className="bg-primary hover:bg-primaryHover text-white p-2 rounded-lg transition-colors disabled:opacity-50 shadow-sm"
              >
                <Send size={16} />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
