import type { AnalysisResponse, ClarificationOption } from '../../services/api';
import { VerificationDetails } from './VerificationDetails';
import { ChartRenderer } from './ChartRenderer';
import { ClarificationCard } from './ClarificationCard';
import { AudioPlayer } from './AudioPlayer';

interface AnswerCardProps {
  analysis: AnalysisResponse;
  onClarify?: (option: ClarificationOption) => void;
}

export function AnswerCard({ analysis, onClarify }: AnswerCardProps) {
  if (!analysis.success) {
    let errorMessage = analysis.error || 'An error occurred during analysis.';
    if (errorMessage === 'SARVAM_STT_FAILED') {
      errorMessage = 'Speech not recognized. Please try speaking clearly or ask in English.';
    } else if (analysis.answer && analysis.answer !== errorMessage) {
      errorMessage = analysis.answer;
    }

    if (!errorMessage.toLowerCase().includes('try again') && !errorMessage.toLowerCase().includes('try speaking')) {
      errorMessage = errorMessage.trim();
      if (!errorMessage.endsWith('.')) errorMessage += '.';
      errorMessage += ' Please try again.';
    }

    return (
      <div className="flex flex-col gap-2">
        <p className="text-red-400">{errorMessage}</p>
      </div>
    );
  }

  if (analysis.clarificationRequired && analysis.clarificationPrompt && analysis.clarificationOptions) {
    return (
      <ClarificationCard 
        prompt={analysis.clarificationPrompt} 
        options={analysis.clarificationOptions} 
        onSelect={onClarify || (() => {})} 
      />
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="text-white/90 text-sm leading-relaxed">
        {analysis.answer}
      </div>

      {analysis.visualization && (
        <div className="w-full">
           <ChartRenderer spec={analysis.visualization} />
        </div>
      )}

      {analysis.verification && (
        <VerificationDetails details={analysis.verification} />
      )}

      {analysis.audioUrl && (
        <div className="w-full mt-2">
          <AudioPlayer src={analysis.audioUrl} />
        </div>
      )}
    </div>
  );
}
