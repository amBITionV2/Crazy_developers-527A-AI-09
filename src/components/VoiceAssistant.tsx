import { useState, useEffect, useCallback } from 'react';
import { Mic, MicOff, Volume2, VolumeX } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { useLanguage } from '@/contexts/LanguageContext';
import { aiAPI } from '@/lib/api';

// Speech Recognition API type definitions
interface SpeechRecognitionEvent {
  results: {
    [index: number]: {
      [index: number]: {
        transcript: string;
      };
    };
  };
}

interface SpeechRecognitionErrorEvent {
  error: string;
}

interface SpeechRecognitionInstance {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  onresult: (event: SpeechRecognitionEvent) => void;
  onerror: (event: SpeechRecognitionErrorEvent) => void;
  onend: () => void;
  start: () => void;
  stop: () => void;
}

interface SpeechRecognitionConstructor {
  new (): SpeechRecognitionInstance;
}

declare global {
  interface Window {
    SpeechRecognition?: SpeechRecognitionConstructor;
    webkitSpeechRecognition?: SpeechRecognitionConstructor;
  }
}

export const VoiceAssistant = () => {
  const { toast } = useToast();
  const { language } = useLanguage();
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [recognition, setRecognition] = useState<SpeechRecognitionInstance | null>(null);
  const [synthesis] = useState(window.speechSynthesis);

  const speak = useCallback((text: string) => {
    if (synthesis) {
      synthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      
      const langMap: { [key: string]: string } = {
        en: 'en-US',
        hi: 'hi-IN',
        kn: 'kn-IN',
        te: 'te-IN',
        ml: 'ml-IN',
      };
      
      utterance.lang = langMap[language] || 'en-US';
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      
      synthesis.speak(utterance);
    }
  }, [language, synthesis]);

  const handleVoiceCommand = useCallback(async (command: string) => {
    if (!command.trim()) return;
    
    setIsProcessing(true);
    
    try {
      // Get userId from localStorage or use a guest user
      const userId = localStorage.getItem('userId') || 'guest-user';
      
      const response = await aiAPI.chat({
        userId,
        message: command,
        context: 'voice_assistant',
        language
      });
      
      if (response.response) {
        speak(response.response);
      }
    } catch (error) {
      console.error('Error processing voice command:', error);
      const errorMessage = language === 'hi' 
        ? 'क्षमा करें, कुछ समस्या हुई है।' 
        : 'Sorry, there was an error processing your request.';
      speak(errorMessage);
      
      toast({
        title: language === 'hi' ? 'त्रुटि' : 'Error',
        description: language === 'hi' 
          ? 'वॉयस कमांड प्रोसेस करने में त्रुटि' 
          : 'Error processing voice command',
        variant: 'destructive',
      });
    } finally {
      setIsProcessing(false);
    }
  }, [language, speak, toast]);

  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognitionInstance = new SpeechRecognition();
      
      const langMap: { [key: string]: string } = {
        en: 'en-US',
        hi: 'hi-IN',
        kn: 'kn-IN',
        te: 'te-IN',
        ml: 'ml-IN',
      };
      
      recognitionInstance.lang = langMap[language] || 'en-US';
      recognitionInstance.continuous = false;
      recognitionInstance.interimResults = false;

      recognitionInstance.onresult = (event: SpeechRecognitionEvent) => {
        const transcript = event.results[0][0].transcript;
        handleVoiceCommand(transcript);
      };

      recognitionInstance.onerror = (event: SpeechRecognitionErrorEvent) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        toast({
          title: 'Voice Error',
          description: 'Could not recognize speech. Please try again.',
          variant: 'destructive',
        });
      };

      recognitionInstance.onend = () => {
        setIsListening(false);
      };

      setRecognition(recognitionInstance);
    }
  }, [language, handleVoiceCommand, toast]);

  const toggleListening = () => {
    if (isListening) {
      recognition?.stop();
      setIsListening(false);
    } else {
      if (recognition) {
        recognition.start();
        setIsListening(true);
        toast({
          title: 'Listening...',
          description: 'Speak now',
        });
      } else {
        toast({
          title: 'Not Supported',
          description: 'Voice recognition is not supported in your browser.',
          variant: 'destructive',
        });
      }
    }
  };

  const toggleSpeaking = () => {
    if (isSpeaking) {
      synthesis?.cancel();
      setIsSpeaking(false);
    }
  };

  return (
    <div className="fixed bottom-8 right-8 flex gap-3 z-50">
      <Button
        onClick={toggleSpeaking}
        size="lg"
        variant={isSpeaking ? 'default' : 'outline'}
        className={`rounded-full w-14 h-14 shadow-lg ${
          isSpeaking ? 'bg-primary animate-pulse' : 'bg-card/80 backdrop-blur-sm border-primary/20'
        }`}
      >
        {isSpeaking ? <VolumeX className="w-6 h-6" /> : <Volume2 className="w-6 h-6" />}
      </Button>
      
      <Button
        onClick={toggleListening}
        size="lg"
        variant={isListening ? 'default' : 'outline'}
        className={`rounded-full w-14 h-14 shadow-lg ${
          isListening ? 'bg-destructive animate-pulse' : 
          isProcessing ? 'bg-orange-500 animate-spin' : 
          'bg-card/80 backdrop-blur-sm border-primary/20'
        }`}
        disabled={isProcessing}
      >
        {isListening ? <MicOff className="w-6 h-6" /> : <Mic className="w-6 h-6" />}
      </Button>
    </div>
  );
};
