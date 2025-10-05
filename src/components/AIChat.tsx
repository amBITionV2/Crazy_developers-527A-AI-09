import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Send, Bot, User, MessageCircle, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { chatAPI } from '@/lib/api';
import { useLanguage } from '@/contexts/LanguageContext';

interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
}

interface AIChatProps {
  userType: 'patient' | 'donor';
  userId: string;
  className?: string;
}

export const AIChat: React.FC<AIChatProps> = ({ userType, userId, className }) => {
  const { t, language } = useLanguage();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: userType === 'patient' 
        ? "Hi! I'm your AI assistant for blood donation queries. Ask me about finding donors, health requirements, or any emergency blood needs."
        : "Hello! I'm here to help with blood donation questions. Ask me about eligibility, health guidelines, donation process, or scheduling.",
      isUser: false,
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage.trim(),
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Determine context based on user type and message content
      let context = 'general';
      const messageContent = inputMessage.toLowerCase();
      
      if (messageContent.includes('emergency') || messageContent.includes('urgent') || messageContent.includes('sos')) {
        context = 'emergency';
      } else if (messageContent.includes('health') || messageContent.includes('eligible') || messageContent.includes('hemoglobin')) {
        context = 'health';
      } else if (messageContent.includes('donate') || messageContent.includes('donation') || messageContent.includes('blood')) {
        context = 'donation';
      }

      const response = await chatAPI.sendMessage({
        message: inputMessage.trim(),
        language: language,
        context: context,
        userId: userId
      });

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.response,
        isUser: false,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);

      // Add suggestions if provided
      if (response.suggestions && response.suggestions.length > 0) {
        const suggestionsMessage: Message = {
          id: (Date.now() + 2).toString(),
          content: `💡 Suggestions: ${response.suggestions.join(', ')}`,
          isUser: false,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, suggestionsMessage]);
      }

    } catch (error) {
      console.error('AI Chat error:', error);
      
      // Enhanced fallback response system
      let fallbackResponse = '';
      const messageContent = inputMessage.toLowerCase();
      
      // Emergency responses
      if (messageContent.includes('emergency') || messageContent.includes('urgent') || messageContent.includes('sos')) {
        fallbackResponse = userType === 'patient' 
          ? "🚨 **EMERGENCY DETECTED** 🚨\n\nFor immediate blood needs:\n\n1. **Use SOS Alert** - Click the Emergency tab to send alerts to nearby donors\n2. **Call 108** - National emergency number\n3. **Contact nearby blood banks** immediately\n4. **Required info**: Blood group, units needed, hospital details\n\nStay calm. Help is on the way! 🩸❤️"
          : "🚨 **EMERGENCY ALERT** 🚨\n\nAs a donor, you can help save lives:\n\n1. **Check Emergency tab** for active alerts\n2. **Respond quickly** if you're eligible and available\n3. **Verify your contact info** is updated\n4. **Share with other donors** in your network\n\nYour quick response can save a life! 🦸‍♂️";
      }
      
      // Health and eligibility responses
      else if (messageContent.includes('eligible') || messageContent.includes('health') || messageContent.includes('hemoglobin')) {
        fallbackResponse = userType === 'patient'
          ? "🏥 **Health Information** 🏥\n\n**Before receiving blood:**\n• Inform about allergies/medications\n• Blood type matching is crucial\n• Medical history review required\n• Stay hydrated and rested\n\n**Blood group compatibility:**\n• O- can receive from O- only\n• AB+ can receive from anyone\n• Check with your doctor for specifics\n\n💡 Monitor your health vitals in the Health tab!"
          : "🩺 **Donation Eligibility** 🩺\n\n**Basic Requirements:**\n• Age: 18-65 years\n• Weight: >50kg (110 lbs)\n• Hemoglobin: >12.5 g/dL\n• No recent illness/medication\n\n**Health Tips:**\n• Iron-rich foods (spinach, red meat)\n• Stay hydrated (drink water before donation)\n• Good sleep (7-8 hours)\n• Avoid alcohol 24 hours before\n\n✅ Check your health score in the dashboard!";
      }
      
      // Blood type and compatibility
      else if (messageContent.includes('blood group') || messageContent.includes('blood type') || messageContent.includes('compatibility')) {
        fallbackResponse = "🩸 **Blood Group Compatibility** 🩸\n\n**Universal Donors & Recipients:**\n• O- (Universal Donor) → Can give to ALL groups\n• AB+ (Universal Recipient) → Can receive from ALL\n\n**Compatibility Chart:**\n🅾️ **O-**: Can donate to → All groups\n🅾️ **O+**: Can donate to → O+, A+, B+, AB+\n🅰️ **A-**: Can donate to → A-, A+, AB-, AB+\n🅰️ **A+**: Can donate to → A+, AB+\n🅱️ **B-**: Can donate to → B-, B+, AB-, AB+\n🅱️ **B+**: Can donate to → B+, AB+\n🆎 **AB-**: Can donate to → AB-, AB+\n🆎 **AB+**: Can donate to → AB+ only\n\n💡 **Remember**: Same or compatible blood types only!";
      }
      
      // Donation process
      else if (messageContent.includes('donate') || messageContent.includes('donation') || messageContent.includes('process')) {
        fallbackResponse = userType === 'patient'
          ? "🏥 **Blood Request Process** 🏥\n\n**For Emergencies:**\n1. Use SOS Alert feature\n2. Fill hospital & contact details\n3. Specify blood group & units needed\n4. Alert sent to nearby donors\n\n**For Planned Needs:**\n1. Schedule future requests\n2. Contact blood banks in advance\n3. Coordinate with family/friends\n4. Keep all medical documents ready\n\n📍 **Tip**: Location services help find nearby donors faster!"
          : "🩸 **Blood Donation Process** 🩸\n\n**Step by Step:**\n1. **Health screening** (15 mins)\n2. **Registration** & ID verification\n3. **Mini health check** (BP, temp, hemoglobin)\n4. **Donation** (8-10 minutes)\n5. **Rest & refreshments** (15 mins)\n\n**After Donation:**\n• Drink plenty of fluids\n• Avoid heavy lifting (24 hours)\n• Eat iron-rich foods\n• Next donation after 84 days\n\n🏆 **You save up to 3 lives per donation!**";
      }
      
      // Frequency and scheduling
      else if (messageContent.includes('often') || messageContent.includes('frequency') || messageContent.includes('schedule')) {
        fallbackResponse = userType === 'patient'
          ? "📅 **Blood Request Scheduling** 📅\n\n**Emergency Requests:**\n• Immediate SOS alerts\n• No daily limits for emergencies\n• Available 24/7\n\n**Regular Requests:**\n• Plan ahead when possible\n• Book appointments with blood banks\n• Coordinate with donor network\n• Keep emergency contacts ready\n\n💡 **Tip**: Build relationships with regular donors in your area!"
          : "📅 **Donation Frequency** 📅\n\n**Whole Blood Donation:**\n• Every **84 days** (12 weeks)\n• Maximum **4 times per year**\n• Body needs time to replenish\n\n**Other Donations:**\n• Platelets: Every 2 weeks\n• Plasma: Every 28 days\n• Double red cells: Every 112 days\n\n⏰ **Scheduling Tips:**\n• Set calendar reminders\n• Join donor drives\n• Maintain consistent schedule\n• Track your donation history";
      }
      
      // Food and preparation
      else if (messageContent.includes('eat') || messageContent.includes('food') || messageContent.includes('prepare')) {
        fallbackResponse = userType === 'patient'
          ? "🍎 **Nutrition for Blood Recipients** 🍎\n\n**Before Transfusion:**\n• Stay hydrated\n• Light, nutritious meal\n• Avoid alcohol\n• Take prescribed medications\n\n**After Transfusion:**\n• Iron-rich foods (spinach, red meat)\n• Vitamin C (citrus fruits)\n• Plenty of water\n• Follow doctor's diet plan\n\n⚠️ **Always consult your healthcare provider for personalized advice!**"
          : "🥗 **Pre-Donation Nutrition** 🥗\n\n**Night Before:**\n• Iron-rich dinner (red meat, spinach, lentils)\n• Good night's sleep (7-8 hours)\n• Stay hydrated\n• Avoid alcohol\n\n**Day of Donation:**\n• Hearty breakfast (avoid fatty foods)\n• Drink 16 oz water 2 hours before\n• Eat vitamin C foods (orange, tomato)\n• Avoid empty stomach donation\n\n**Foods to Include:**\n🥩 Red meat, 🍃 Leafy greens, 🥜 Nuts, 🍊 Citrus fruits";
      }
      
      // General information
      else if (messageContent.includes('help') || messageContent.includes('info') || messageContent.includes('about')) {
        fallbackResponse = userType === 'patient'
          ? "🤝 **How I Can Help You** 🤝\n\n**Emergency Support:**\n• Guide you through SOS alerts\n• Blood group compatibility info\n• Emergency procedures\n• Contact information\n\n**Health Guidance:**\n• Pre-transfusion preparation\n• Understanding blood types\n• Finding donors nearby\n• Medical terminology\n\n**Available 24/7** to help you get the blood you need safely and quickly! Ask me anything about blood donation, health, or emergencies."
          : "🤝 **How I Can Help You** 🤝\n\n**Donation Guidance:**\n• Eligibility requirements\n• Health screening info\n• Donation process steps\n• Recovery tips\n\n**Emergency Response:**\n• How to respond to SOS alerts\n• Emergency procedures\n• Quick decision making\n• Donor network coordination\n\n**Health & Wellness:**\n• Nutrition advice\n• Fitness for donation\n• Schedule management\n• Impact of your donations\n\n🩸 **Ready to save lives? Ask me anything!**";
      }
      
      // Default responses
      else {
        const defaultResponses = userType === 'patient' ? [
          "🩸 I'm here to help you with blood requests and emergencies. Try asking about:\n• 'Emergency blood needs'\n• 'Blood group compatibility'\n• 'How to find donors'\n• 'Health requirements for transfusion'",
          "🏥 Need blood assistance? I can help with:\n• SOS emergency alerts\n• Understanding blood types\n• Finding nearby donors\n• Health and safety info",
          "❤️ I'm your blood donation assistant! Ask me about:\n• Emergency procedures\n• Blood compatibility\n• Donor network\n• Health requirements"
        ] : [
          "🦸‍♂️ I'm here to guide your blood donation journey! Try asking:\n• 'Am I eligible to donate?'\n• 'How often can I donate?'\n• 'What should I eat before donating?'\n• 'How to respond to emergencies?'",
          "🩸 Ready to save lives? I can help with:\n• Donation eligibility\n• Health requirements\n• Emergency response\n• Nutrition and preparation",
          "🌟 Your donation saves lives! Ask me about:\n• Donation process\n• Health screening\n• Emergency alerts\n• Frequency and scheduling"
        ];
        
        fallbackResponse = defaultResponses[Math.floor(Math.random() * defaultResponses.length)];
      }

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: fallbackResponse,
        isUser: false,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
      
      // Show friendly error message instead of alarming error
      toast.info('Using offline AI assistant - responses are still helpful! 🤖');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const quickQuestions = userType === 'patient' ? [
    "🚨 Emergency blood needed - what should I do?",
    "🩸 What blood types are compatible with mine?",
    "🏥 How to prepare for blood transfusion?",
    "📍 How to find nearby blood donors?",
    "⚕️ What health info do I need to provide?",
    "📱 How does the SOS alert system work?",
    "🔍 How to verify donor reliability?",
    "📋 What documents are needed for transfusion?"
  ] : [
    "🩸 Am I eligible to donate blood today?",
    "🍎 What should I eat before donating?",
    "⏰ How often can I donate blood?",
    "🚨 How to respond to emergency alerts?",
    "💪 How to maintain good health for donation?",
    "📍 Where are the nearest donation centers?",
    "🏆 How many lives can my donation save?",
    "📊 What health tests are done before donation?"
  ];

  return (
    <Card className={`bg-card/50 backdrop-blur-sm border-primary/20 ${className}`}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2">
          <MessageCircle className="w-5 h-5 text-primary" />
          AI Health Assistant
          <div className="ml-auto flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-green-500"></div>
            <span className="text-xs text-muted-foreground">Online</span>
          </div>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Messages */}
        <ScrollArea className="h-80 w-full rounded-md border border-primary/10 p-4" ref={scrollAreaRef}>
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${message.isUser ? 'justify-end' : 'justify-start'}`}
              >
                {!message.isUser && (
                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                    <Bot className="w-4 h-4 text-primary" />
                  </div>
                )}
                
                <div
                  className={`max-w-[75%] rounded-lg p-3 ${
                    message.isUser
                      ? 'bg-primary text-white'
                      : 'bg-background border border-primary/20'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  <span className="text-xs opacity-70 mt-1 block">
                    {message.timestamp.toLocaleTimeString()}
                  </span>
                </div>
                
                {message.isUser && (
                  <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                    <User className="w-4 h-4 text-white" />
                  </div>
                )}
              </div>
            ))}
            
            {isLoading && (
              <div className="flex gap-3 justify-start">
                <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-primary" />
                </div>
                <div className="bg-background border border-primary/20 rounded-lg p-3">
                  <div className="flex items-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin text-primary" />
                    <span className="text-sm text-muted-foreground">AI is thinking...</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        {/* Quick Questions */}
        <div className="space-y-2">
          <p className="text-xs text-muted-foreground">Quick questions:</p>
          <div className="grid grid-cols-1 gap-2">
            {quickQuestions.map((question, index) => (
              <Button
                key={index}
                variant="outline"
                size="sm"
                className="text-xs h-auto p-2 justify-start border-primary/20 hover:bg-primary/10"
                onClick={() => {
                  setInputMessage(question);
                  handleSendMessage();
                }}
                disabled={isLoading}
              >
                {question}
              </Button>
            ))}
          </div>
        </div>

        {/* Input */}
        <div className="flex gap-2">
          <Input
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me about blood donation..."
            className="flex-1 border-primary/20 focus:border-primary"
            disabled={isLoading}
          />
          <Button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="bg-primary hover:bg-primary/90"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};