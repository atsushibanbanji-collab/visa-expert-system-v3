import { useState, useEffect } from 'react';
import DiagnosisPanel from './components/DiagnosisPanel';
import VisualizationPanel from './components/VisualizationPanel';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

function App() {
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [conclusions, setConclusions] = useState([]);
  const [isFinished, setIsFinished] = useState(false);
  const [visualizationData, setVisualizationData] = useState(null);
  const [questionHistory, setQuestionHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Start consultation on mount
  useEffect(() => {
    startConsultation();
  }, []);

  const startConsultation = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/consultation/start`, {
        method: 'POST',
      });
      const data = await response.json();
      setCurrentQuestion(data.next_question);
      setQuestionHistory(data.next_question ? [data.next_question] : []);
      setConclusions([]);
      setIsFinished(false);
      await fetchVisualization();
    } catch (err) {
      setError('診断の開始に失敗しました: ' + err.message);
      console.error('Error starting consultation:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchVisualization = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/consultation/visualization`);
      const data = await response.json();
      setVisualizationData(data);
    } catch (err) {
      console.error('Error fetching visualization:', err);
    }
  };

  const handleAnswer = async (question, answer) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/consultation/answer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: question,
          answer: answer,
        }),
      });
      const data = await response.json();

      setCurrentQuestion(data.next_question);
      setConclusions(data.conclusions);
      setIsFinished(data.is_finished);

      if (data.next_question && !questionHistory.includes(data.next_question)) {
        setQuestionHistory([...questionHistory, data.next_question]);
      }

      await fetchVisualization();
    } catch (err) {
      setError('回答の送信に失敗しました: ' + err.message);
      console.error('Error answering question:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBack = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/consultation/back`, {
        method: 'POST',
      });
      const data = await response.json();

      if (data.current_question) {
        setCurrentQuestion(data.current_question);
        // Remove last question from history
        setQuestionHistory(questionHistory.slice(0, -1));
        setIsFinished(false);
        setConclusions([]);
      }

      await fetchVisualization();
    } catch (err) {
      setError('前の質問に戻れませんでした: ' + err.message);
      console.error('Error going back:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRestart = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/consultation/restart`, {
        method: 'POST',
      });
      const data = await response.json();

      setCurrentQuestion(data.next_question);
      setQuestionHistory(data.next_question ? [data.next_question] : []);
      setConclusions([]);
      setIsFinished(false);

      await fetchVisualization();
    } catch (err) {
      setError('診断の再開に失敗しました: ' + err.message);
      console.error('Error restarting:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-navy-50 via-gray-50 to-navy-100">
      {/* Header */}
      <header className="bg-navy-900 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold">ビザ選定エキスパートシステム</h1>
          <p className="text-navy-200 mt-2">
            オブジェクト指向設計による推論エンジン
          </p>
        </div>
      </header>

      {/* Error Display */}
      {error && (
        <div className="max-w-7xl mx-auto px-4 mt-4">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
            <strong className="font-bold">エラー: </strong>
            <span className="block sm:inline">{error}</span>
          </div>
        </div>
      )}

      {/* Main Content - 2 Column Layout */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-200px)]">
          {/* Left Panel - Diagnosis */}
          <div className="h-full">
            {loading && questionHistory.length === 0 ? (
              <div className="bg-white rounded-lg shadow-lg p-8 h-full flex items-center justify-center">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-navy-900 mx-auto mb-4"></div>
                  <p className="text-gray-600">読み込み中...</p>
                </div>
              </div>
            ) : (
              <DiagnosisPanel
                currentQuestion={currentQuestion}
                onAnswer={handleAnswer}
                onBack={handleBack}
                onRestart={handleRestart}
                conclusions={conclusions}
                isFinished={isFinished}
                questionHistory={questionHistory}
              />
            )}
          </div>

          {/* Right Panel - Visualization */}
          <div className="h-full">
            <VisualizationPanel visualizationData={visualizationData} />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-navy-900 text-white mt-8">
        <div className="max-w-7xl mx-auto px-4 py-4 text-center text-sm text-navy-200">
          © 2025 Visa Expert System - Built with React & FastAPI
        </div>
      </footer>
    </div>
  );
}

export default App;
