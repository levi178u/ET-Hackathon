import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Zap, GraduationCap, Briefcase, Code, Rocket, Clock, AlignLeft, BookOpen } from 'lucide-react';
import { clsx } from 'clsx';

export default function Onboarding() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const totalSteps = 3;

  const [interests, setInterests] = useState([]);
  const [role, setRole] = useState(null);
  const [readMode, setReadMode] = useState(null);

  const topics = [
    "Economy & Markets", "Politics & Policy", "Technology", "Startups",
    "Global Affairs", "Climate & Energy", "Science", "Sports",
    "Entertainment", "Education", "Healthcare", "Real Estate"
  ];

  const roles = [
    { id: 'student', title: 'Student', desc: 'Preparing for exams or staying informed', icon: <GraduationCap size={20} /> },
    { id: 'investor', title: 'Investor', desc: 'Tracking markets and macro trends', icon: <Briefcase size={20} /> },
    { id: 'developer', title: 'Developer', desc: 'Following tech, startups, and innovation', icon: <Code size={20} /> },
    { id: 'founder', title: 'Founder', desc: 'Strategy, competition, and opportunity', icon: <Rocket size={20} /> }
  ];

  const modes = [
    { id: '60s', title: '60-second Briefings', desc: 'Headlines and key takeaways only', icon: <Clock size={18} /> },
    { id: 'smart', title: 'Smart summaries', desc: 'The sweet spot: context without overload', icon: <AlignLeft size={18} /> },
    { id: 'deep', title: 'Deep dives', desc: 'Full analysis, data, and expert views', icon: <BookOpen size={18} /> }
  ];

  const toggleInterest = (t) => {
    if (interests.includes(t)) setInterests(interests.filter(i => i !== t));
    else setInterests([...interests, t]);
  };

  const handleNext = () => {
    if (step < totalSteps) setStep(step + 1);
    else navigate('/feed'); // Submit and go to feed
  };

  const handleBack = () => {
    if (step > 1) setStep(step - 1);
    else navigate('/');
  };

  const canProceed = () => {
    if (step === 1) return interests.length >= 2;
    if (step === 2) return role !== null;
    if (step === 3) return readMode !== null;
    return false;
  };

  return (
    <div className="flex flex-col items-center w-full min-h-screen pt-20 px-6">
      {/* Header */}
      <div className="flex items-center space-x-2 mb-12">
        <div className="bg-primary text-white p-1 rounded">
          <Zap className="w-5 h-5" />
        </div>
        <span className="font-bold text-lg">News Navigator</span>
      </div>

      {/* Progress Bars */}
      <div className="flex items-center space-x-2 w-full max-w-md mb-12">
        {[1, 2, 3].map(i => (
          <div key={i} className={clsx(
            "h-1 flex-1 rounded-full",
            step >= i ? "bg-primary" : "bg-surfaceHover"
          )} />
        ))}
      </div>

      <div className="w-full max-w-2xl flex flex-col">
        {step === 1 && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <h1 className="text-3xl font-serif font-bold mb-2">What interests you?</h1>
            <p className="text-textMuted mb-8 text-sm">Pick at least 2 topics. We'll curate your feed around these.</p>
            
            <div className="flex flex-wrap gap-3">
              {topics.map(t => (
                <button
                  key={t}
                  onClick={() => toggleInterest(t)}
                  className={clsx(
                    "px-4 py-2 rounded-full text-sm font-medium transition-colors border",
                    interests.includes(t) 
                      ? "bg-primary/20 border-primary text-primary" 
                      : "bg-surface border-surfaceHover text-textMuted hover:border-textMuted/50 hover:text-textDefault"
                  )}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <h1 className="text-3xl font-serif font-bold mb-2">What best describes you?</h1>
            <p className="text-textMuted mb-8 text-sm">This helps us tailor your briefings.</p>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {roles.map(r => (
                <button
                  key={r.id}
                  onClick={() => setRole(r.id)}
                  className={clsx(
                    "p-5 rounded-xl border text-left transition-all flex flex-col items-start gap-4",
                    role === r.id 
                      ? "bg-surfaceHover border-primary" 
                      : "bg-surface border-surfaceHover hover:border-textMuted/30"
                  )}
                >
                  <div className={clsx(role === r.id ? "text-primary" : "text-textMuted")}>
                    {r.icon}
                  </div>
                  <div>
                    <h3 className="font-bold text-textDefault mb-1">{r.title}</h3>
                    <p className="text-xs text-textMuted leading-relaxed">{r.desc}</p>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <h1 className="text-3xl font-serif font-bold mb-2">How do you prefer to read?</h1>
            <p className="text-textMuted mb-8 text-sm">You can change this anytime.</p>
            
            <div className="flex flex-col gap-3">
              {modes.map(m => (
                <button
                  key={m.id}
                  onClick={() => setReadMode(m.id)}
                  className={clsx(
                    "p-5 rounded-xl border text-left transition-all",
                    readMode === m.id 
                      ? "bg-surfaceHover border-primary" 
                      : "bg-surface border-surfaceHover hover:border-textMuted/30"
                  )}
                >
                  <h3 className="font-bold text-textDefault mb-1">{m.title}</h3>
                  <p className="text-xs text-textMuted">{m.desc}</p>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Footer Actions */}
        <div className="flex items-center justify-between mt-12 pt-6 border-t border-surfaceHover">
          <button 
            onClick={handleBack}
            className="text-sm font-medium text-textMuted hover:text-textDefault transition-colors flex items-center gap-2"
          >
            ← Back
          </button>
          <button 
            disabled={!canProceed()}
            onClick={handleNext}
            className="bg-primary hover:bg-primaryHover disabled:opacity-50 disabled:cursor-not-allowed text-white px-6 py-2.5 rounded-md font-medium transition-colors flex items-center gap-2"
          >
            {step === totalSteps ? 'Launch My Feed' : 'Next'} 
            <span className="text-lg leading-none">→</span>
          </button>
        </div>
      </div>
    </div>
  );
}
