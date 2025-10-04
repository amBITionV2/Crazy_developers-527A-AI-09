import { useState, useEffect } from 'react';
import { Mic, MicOff, Volume2, VolumeX } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { useLanguage } from '@/contexts/LanguageContext';

export const VoiceAssistant = () => {
  const { toast } = useToast();
  const { language } = useLanguage();
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [recognition, setRecognition] = useState<any>(null);
  const [synthesis] = useState(window.speechSynthesis);

  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
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

      recognitionInstance.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        handleVoiceCommand(transcript);
      };

      recognitionInstance.onerror = (event: any) => {
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
  }, [language]);

  const handleVoiceCommand = (command: string) => {
    console.log('Voice command:', command);
    
    // Mock response based on command
    let response = 'I heard you. How can I help with blood donation?';
    
    if (command.toLowerCase().includes('donate') || command.toLowerCase().includes('donation')) {
      response = 'You can donate blood if you are healthy, above 18 years, and weigh at least 50 kg. Last donation should be 3 months ago.';
    } else if (command.toLowerCase().includes('emergency') || command.toLowerCase().includes('sos')) {
      response = 'Emergency requests are shown in your emergency tab. You can accept or decline based on your availability.';
    } else if (command.toLowerCase().includes('health') || command.toLowerCase().includes('status')) {
      response = 'Your current health score is 85%. Blood pressure and hemoglobin levels are normal.';
    }
    
    speak(response);
  };

  const speak = (text: string) => {
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
  };

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
          isListening ? 'bg-destructive animate-pulse' : 'bg-card/80 backdrop-blur-sm border-primary/20'
        }`}
      >
        {isListening ? <MicOff className="w-6 h-6" /> : <Mic className="w-6 h-6" />}
      </Button>
    </div>
  );
};
