import { useState, useEffect } from 'react';
import { X, Loader2, CheckCircle, XCircle } from 'lucide-react';
import axios from 'axios';
import { clsx } from 'clsx';

export default function QuizModal({ article, onClose, baseUrl }) {
  const [loading, setLoading] = useState(true);
  const [questions, setQuestions] = useState([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [selectedOpt, setSelectedOpt] = useState(null);
  const [isAnswered, setIsAnswered] = useState(false);
  const [score, setScore] = useState(0);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchQuiz = async () => {
      try {
        const { data } = await axios.post(`${baseUrl}/api/assistant/generate_quiz`, {
          article_content: article.description || article.summary_raw || article.title
        });
        if (data.quiz && data.quiz.length > 0) {
          setQuestions(data.quiz);
        } else {
          setError("Couldn't generate quiz format properly.");
        }
      } catch (err) {
        setError("Error reaching the AI quiz engine.");
      } finally {
        setLoading(false);
      }
    };
    if (article && baseUrl) fetchQuiz();
  }, [article, baseUrl]);

  const handleOptionClick = (idx) => {
    if (isAnswered) return;
    setSelectedOpt(idx);
    setIsAnswered(true);
    if (idx === questions[currentIdx].answer) {
      setScore(s => s + 1);
    }
  };

  const nextQuestion = () => {
    setSelectedOpt(null);
    setIsAnswered(false);
    setCurrentIdx(c => c + 1);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in">
      <div className="bg-surface border border-surfaceHover rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-surfaceHover bg-surface/80">
          <h3 className="font-bold text-lg">Knowledge Check</h3>
          <button onClick={onClose} className="p-1 text-textMuted hover:text-white transition-colors">
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 min-h-[350px] flex flex-col">
          {loading ? (
            <div className="flex-1 flex flex-col items-center justify-center space-y-4 text-textMuted">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
              <p>Studying the article to generate questions...</p>
            </div>
          ) : error ? (
            <div className="flex-1 flex items-center justify-center text-red-400">
              {error}
            </div>
          ) : currentIdx >= questions.length ? (
            <div className="flex-1 flex flex-col items-center justify-center text-center space-y-4 animate-in zoom-in-95">
              <div className="w-24 h-24 bg-gradient-to-tr from-orange-400 to-primary rounded-full flex items-center justify-center mb-2 shadow-lg shadow-primary/20">
                <span className="text-4xl font-bold text-white">{score}/{questions.length}</span>
              </div>
              <h2 className="text-2xl font-bold font-serif">Quiz Complete!</h2>
              <p className="text-textMuted text-sm">You earned <span className="text-primary font-bold">{score * 10} XP</span> for this article.</p>
              <button onClick={onClose} className="mt-6 bg-primary hover:bg-primaryHover text-white px-8 py-3 rounded-xl font-bold transition-all hover:scale-105 active:scale-95">
                Continue Reading
              </button>
            </div>
          ) : (
            <div className="flex flex-col flex-1 h-full animate-in slide-in-from-right-4 fade-in">
              <div className="flex items-center justify-between mb-6 text-sm">
                <span className="text-textMuted uppercase font-bold tracking-wider text-xs">Question {currentIdx + 1} of {questions.length}</span>
                <span className="text-primary font-bold">Score: {score}</span>
              </div>
              
              <h4 className="text-lg font-medium leading-snug mb-6">{questions[currentIdx].question}</h4>

              <div className="space-y-3 flex-1">
                {questions[currentIdx].options.map((opt, i) => {
                  let btnClass = "w-full text-left p-4 rounded-xl border transition-all flex items-center justify-between ";
                  if (!isAnswered) {
                    btnClass += "border-surfaceHover bg-surfaceHover/50 hover:bg-surfaceHover hover:border-primary/50 text-textDefault hover:scale-[1.01]";
                  } else {
                    if (i === questions[currentIdx].answer) {
                      btnClass += "bg-emerald-500/10 border-emerald-500/50 text-emerald-100 scale-[1.02] shadow-sm";
                    } else if (i === selectedOpt) {
                      btnClass += "bg-red-500/10 border-red-500/50 text-red-100";
                    } else {
                      btnClass += "border-surfaceHover bg-surfaceHover/30 text-textMuted opacity-50";
                    }
                  }

                  return (
                    <button 
                      key={i} 
                      onClick={() => handleOptionClick(i)}
                      disabled={isAnswered}
                      className={btnClass}
                    >
                      <span className="font-medium text-sm">{opt}</span>
                      {isAnswered && i === questions[currentIdx].answer && <CheckCircle size={18} className="text-emerald-400" />}
                      {isAnswered && i === selectedOpt && i !== questions[currentIdx].answer && <XCircle size={18} className="text-red-400" />}
                    </button>
                  );
                })}
              </div>

              {isAnswered && (
                <div className="mt-6 pt-6 border-t border-surfaceHover animate-in fade-in slide-in-from-bottom-2">
                  <div className="bg-primary/10 border border-primary/20 rounded-lg p-4 mb-4">
                    <p className="text-sm leading-relaxed"><span className="font-bold text-primary mr-2">💡 Explanation:</span>{questions[currentIdx].explanation}</p>
                  </div>
                  <button 
                    onClick={nextQuestion}
                    className="w-full bg-primary hover:bg-primaryHover text-white py-3 rounded-xl font-bold transition-all hover:scale-[1.02] active:scale-[0.98]"
                  >
                    {currentIdx === questions.length - 1 ? "See Results" : "Next Question"}
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
