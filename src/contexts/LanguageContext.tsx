import React, { createContext, useContext, useState, ReactNode } from 'react';

type Language = 'en' | 'hi' | 'kn' | 'te' | 'ml';

interface Translations {
  [key: string]: {
    [key in Language]: string;
  };
}

const translations: Translations = {
  // Landing Page
  appName: {
    en: 'रक्त_Setu',
    hi: 'रक्त_सेतु',
    kn: 'ರಕ್ತ_ಸೇತು',
    te: 'రక్త_సేతు',
    ml: 'രക്ത_സേതു',
  },
  tagline: {
    en: 'Connecting donors to hope',
    hi: 'दाताओं को आशा से जोड़ना',
    kn: 'ದಾನಿಗಳನ್ನು ಭರವಸೆಗೆ ಸಂಪರ್ಕಿಸುವುದು',
    te: 'దాతలను ఆశకు కనెక్ట్ చేయడం',
    ml: 'ദാതാക്കളെ പ്രതീക്ഷയുമായി ബന്ധിപ്പിക്കുന്നു',
  },
  description: {
    en: 'रक्त_Setu is the first app to connect patients with verified donors in real-time, helping chronic patients like Thalassemia and dialysis cases. SOS alerts search donors 1–5 km away with live notifications. AI/ML predicts availability and guides health decisions. With multilingual support, voice assistance, transfusion tracking, and eRaktKosh integration, रक्त_Setu makes blood donation fast, smart, and compassionate.',
    hi: 'रक्त_सेतु पहला ऐप है जो मरीजों को सत्यापित दाताओं से रियल-टाइम में जोड़ता है, थैलेसीमिया और डायलिसिस जैसे क्रोनिक मरीजों की मदद करता है। एसओएस अलर्ट 1-5 किमी दूर दाताओं को लाइव नोटिफिकेशन के साथ खोजता है। एआई/एमएल उपलब्धता की भविष्यवाणी करता है और स्वास्थ्य निर्णयों का मार्गदर्शन करता है।',
    kn: 'ರಕ್ತ_ಸೇತು ರೋಗಿಗಳನ್ನು ಪರಿಶೀಲಿತ ದಾನಿಗಳೊಂದಿಗೆ ನೈಜ ಸಮಯದಲ್ಲಿ ಸಂಪರ್ಕಿಸುವ ಮೊದಲ ಅಪ್ಲಿಕೇಶನ್ ಆಗಿದೆ, ಥಲಸ್ಸೀಮಿಯಾ ಮತ್ತು ಡಯಾಲಿಸಿಸ್ ಪ್ರಕರಣಗಳಂತಹ ದೀರ್ಘಕಾಲದ ರೋಗಿಗಳಿಗೆ ಸಹಾಯ ಮಾಡುತ್ತದೆ।',
    te: 'రక్త_సేతు రోగులను ధృవీకరించబడిన దాతలతో రియల్-టైమ్‌లో కనెక్ట్ చేసే మొదటి యాప్, థలసీమియా మరియు డయాలసిస్ కేసుల వంటి దీర్ఘకాలిక రోగులకు సహాయపడుతుంది।',
    ml: 'രക്ത_സേതു രോഗികളെ പരിശോധിച്ച ദാതാക്കളുമായി തത്സമയം ബന്ധിപ്പിക്കുന്ന ആദ്യ ആപ്പാണ്, തലസീമിയ, ഡയാലിസിസ് കേസുകൾ പോലുള്ള ദീർഘകാല രോഗികളെ സഹായിക്കുന്നു।',
  },
  getStarted: {
    en: 'Get Started',
    hi: 'शुरू करें',
    kn: 'ಪ್ರಾರಂಭಿಸಿ',
    te: 'ప్రారంభించండి',
    ml: 'ആരംഭിക്കുക',
  },
  // Features
  features: {
    en: 'Key Features',
    hi: 'मुख्य विशेषताएं',
    kn: 'ಮುಖ್ಯ ವೈಶಿಷ್ಟ್ಯಗಳು',
    te: 'ముఖ్య లక్షణాలు',
    ml: 'പ്രധാന സവിശേഷതകൾ',
  },
  smartNetwork: {
    en: 'Smart Blood Network',
    hi: 'स्मार्ट ब्लड नेटवर्क',
    kn: 'ಸ್ಮಾರ್ಟ್ ಬ್ಲಡ್ ನೆಟ್‌ವರ್ಕ್',
    te: 'స్మార్ట్ బ్లడ్ నెట్‌వర్క్',
    ml: 'സ്മാർട്ട് ബ്ലഡ് നെറ്റ്‌വർക്ക്',
  },
  smartNetworkDesc: {
    en: 'AI-matched donors and instant emergency alerts',
    hi: 'एआई-मिलान दाता और तत्काल आपातकालीन अलर्ट',
    kn: 'AI-ಹೊಂದಾಣಿಕೆ ದಾನಿಗಳು ಮತ್ತು ತತ್ಕ್ಷಣ ತುರ್ತು ಎಚ್ಚರಿಕೆಗಳು',
    te: 'AI-సరిపోలిన దాతలు మరియు తక్షణ అత్యవసర హెచ్చరికలు',
    ml: 'AI-പൊരുത്തപ്പെടുത്തിയ ദാതാക്കളും തൽക്ഷണ അടിയന്തര മുന്നറിയിപ്പുകളും',
  },
  healthTracker: {
    en: 'Health Tracker',
    hi: 'स्वास्थ्य ट्रैकर',
    kn: 'ಆರೋಗ್ಯ ಟ್ರ್ಯಾಕರ್',
    te: 'ఆరోగ్య ట్రాకర్',
    ml: 'ഹെൽത്ത് ട്രാക്കർ',
  },
  healthTrackerDesc: {
    en: 'Real-time vitals monitoring with anomaly alerts',
    hi: 'विसंगति अलर्ट के साथ रीयल-टाइम वाइटल मॉनिटरिंग',
    kn: 'ಅಸಹಜ ಎಚ್ಚರಿಕೆಗಳೊಂದಿಗೆ ನೈಜ ಸಮಯದ ಪ್ರಮುಖ ಮಾನಿಟರಿಂಗ್',
    te: 'అసాధారణ హెచ్చరికలతో నిజ-సమయ ప్రాణాధార పర్యవేక్షణ',
    ml: 'അനോമലി അലേർട്ടുകളോടുകൂടിയ തത്സമയ വൈറ്റൽ മോണിറ്ററിംഗ്',
  },
  multiLanguage: {
    en: 'Multi-Language Support',
    hi: 'बहु-भाषा समर्थन',
    kn: 'ಬಹು-ಭಾಷಾ ಬೆಂಬಲ',
    te: 'బహుళ-భాషా మద్దతు',
    ml: 'മൾട്ടി-ലാംഗ്വേജ് പിന്തുണ',
  },
  multiLanguageDesc: {
    en: 'Access healthcare guidance in your preferred language',
    hi: 'अपनी पसंदीदा भाषा में स्वास्थ्य सेवा मार्गदर्शन तक पहुंचें',
    kn: 'ನಿಮ್ಮ ಆದ್ಯತೆಯ ಭಾಷೆಯಲ್ಲಿ ಆರೋಗ್ಯ ಮಾರ್ಗದರ್ಶನವನ್ನು ಪ್ರವೇಶಿಸಿ',
    te: 'మీ ఇష్టమైన భాషలో ఆరోగ్య మార్గదర్శకత్వాన్ని యాక్సెస్ చేయండి',
    ml: 'നിങ്ങളുടെ ഇഷ്ടഭാഷയിൽ ആരോഗ്യ മാർഗനിർദേശം ആക്സസ് ചെയ്യുക',
  },
  aiAssistant: {
    en: 'AI Health Assistant',
    hi: 'एआई स्वास्थ्य सहायक',
    kn: 'AI ಆರೋಗ್ಯ ಸಹಾಯಕ',
    te: 'AI ఆరోగ్య సహాయకుడు',
    ml: 'AI ഹെൽത്ത് അസിസ്റ്റന്റ്',
  },
  aiAssistantDesc: {
    en: '24/7 personalized guidance and symptom checks',
    hi: '24/7 व्यक्तिगत मार्गदर्शन और लक्षण जांच',
    kn: '24/7 ವೈಯಕ್ತಿಕ ಮಾರ್ಗದರ್ಶನ ಮತ್ತು ರೋಗಲಕ್ಷಣ ಪರಿಶೀಲನೆಗಳು',
    te: '24/7 వ్యక్తిగతీకరించిన మార్గదర్శకత్వం మరియు లక్షణ తనిఖీలు',
    ml: '24/7 വ്യക്തിഗത മാർഗനിർദേശവും രോഗലക്ഷണ പരിശോധനകളും',
  },
  voiceAssistant: {
    en: 'Voice Assistant',
    hi: 'वॉइस असिस्टेंट',
    kn: 'ವಾಯ್ಸ್ ಅಸಿಸ್ಟೆಂಟ್',
    te: 'వాయిస్ అసిస్టెంట్',
    ml: 'വോയ്സ് അസിസ്റ്റന്റ്',
  },
  voiceAssistantDesc: {
    en: 'Voice assistance for rural and non-literate users',
    hi: 'ग्रामीण और गैर-साक्षर उपयोगकर्ताओं के लिए आवाज सहायता',
    kn: 'ಗ್ರಾಮೀಣ ಮತ್ತು ಅನಕ್ಷರಸ್ಥ ಬಳಕೆದಾರರಿಗೆ ಧ್ವನಿ ಸಹಾಯ',
    te: 'గ్రామీణ మరియు నిరక్షరాస్య వినియోగదారులకు వాయిస్ సహాయం',
    ml: 'ഗ്രാമീണ, നിരക്ഷരരായ ഉപയോക്താക്കൾക്കുള്ള വോയ്സ് സഹായം',
  },
  emergencyAlerts: {
    en: 'Emergency Alerts',
    hi: 'आपातकालीन अलर्ट',
    kn: 'ತುರ್ತು ಎಚ್ಚರಿಕೆಗಳು',
    te: 'అత్యవసర హెచ్చరికలు',
    ml: 'അടിയന്തര മുന്നറിയിപ്പുകൾ',
  },
  emergencyAlertsDesc: {
    en: 'Track doses and notify family/hospitals in critical events',
    hi: 'खुराक ट्रैक करें और गंभीर घटनाओं में परिवार/अस्पतालों को सूचित करें',
    kn: 'ಡೋಸ್‌ಗಳನ್ನು ಟ್ರ್ಯಾಕ್ ಮಾಡಿ ಮತ್ತು ನಿರ್ಣಾಯಕ ಘಟನೆಗಳಲ್ಲಿ ಕುಟುಂಬ/ಆಸ್ಪತ್ರೆಗಳಿಗೆ ಸೂಚಿಸಿ',
    te: 'మోతాదులను ట్రాక్ చేయండి మరియు క్లిష్ట సంఘటనలలో కుటుంబం/ఆసుపత్రులకు తెలియజేయండి',
    ml: 'ഡോസുകൾ ട്രാക്ക് ചെയ്യുകയും നിർണായക സംഭവങ്ങളിൽ കുടുംബത്തെ/ആശുപത്രികളെ അറിയിക്കുകയും ചെയ്യുക',
  },
  // User Type Selection
  selectUserType: {
    en: 'I am a...',
    hi: 'मैं हूँ...',
    kn: 'ನಾನು...',
    te: 'నేను...',
    ml: 'ഞാൻ...',
  },
  donor: {
    en: 'Donor',
    hi: 'दाता',
    kn: 'ದಾನಿ',
    te: 'దాత',
    ml: 'ദാതാവ്',
  },
  patient: {
    en: 'Patient',
    hi: 'मरीज',
    kn: 'ರೋಗಿ',
    te: 'రోగి',
    ml: 'രോഗി',
  },
  donorDesc: {
    en: 'Register as a verified blood donor',
    hi: 'सत्यापित रक्तदाता के रूप में पंजीकरण करें',
    kn: 'ಪರಿಶೀಲಿತ ರಕ್ತದಾನಿಯಾಗಿ ನೋಂದಾಯಿಸಿ',
    te: 'ధృవీకరించబడిన రక్తదాతగా నమోదు చేసుకోండి',
    ml: 'പരിശോധിച്ച രക്തദാതാവായി രജിസ്റ്റർ ചെയ്യുക',
  },
  patientDesc: {
    en: 'Find donors quickly in emergencies',
    hi: 'आपात स्थिति में जल्दी से दाता खोजें',
    kn: 'ತುರ್ತು ಪರಿಸ್ಥಿತಿಗಳಲ್ಲಿ ತ್ವರಿತವಾಗಿ ದಾನಿಗಳನ್ನು ಹುಡುಕಿ',
    te: 'అత్యవసర పరిస్థితుల్లో త్వరగా దాతలను కనుగొనండి',
    ml: 'അടിയന്തിര സാഹചര്യങ്ങളിൽ വേഗത്തിൽ ദാതാക്കളെ കണ്ടെത്തുക',
  },
  // Dashboard
  dashboard: {
    en: 'Dashboard',
    hi: 'डैशबोर्ड',
    kn: 'ಡ್ಯಾಶ್‌ಬೋರ್ಡ್',
    te: 'డాష్‌బోర్డ్',
    ml: 'ഡാഷ്‌ബോർഡ്',
  },
  healthStatus: {
    en: 'Health Status',
    hi: 'स्वास्थ्य स्थिति',
    kn: 'ಆರೋಗ್ಯ ಸ್ಥಿತಿ',
    te: 'ఆరోగ్య స్థితి',
    ml: 'ആരോഗ്യ നില',
  },
  history: {
    en: 'History',
    hi: 'इतिहास',
    kn: 'ಇತಿಹಾಸ',
    te: 'చరిత్ర',
    ml: 'ചരിത്രം',
  },
  schedule: {
    en: 'Schedule',
    hi: 'अनुसूची',
    kn: 'ವೇಳಾಪಟ್ಟಿ',
    te: 'షెడ్యూల్',
    ml: 'ഷെഡ്യൂൾ',
  },
  emergency: {
    en: 'Emergency',
    hi: 'आपातकाल',
    kn: 'ತುರ್ತು',
    te: 'అత్యవసరం',
    ml: 'അടിയന്തിരം',
  },
  community: {
    en: 'Community',
    hi: 'समुदाय',
    kn: 'ಸಮುದಾಯ',
    te: 'సంఘం',
    ml: 'കമ്മ്യൂണിറ്റി',
  },
  sosAlert: {
    en: 'SOS Alert',
    hi: 'एसओएस अलर्ट',
    kn: 'SOS ಎಚ್ಚರಿಕೆ',
    te: 'SOS హెచ్చరిక',
    ml: 'SOS മുന്നറിയിപ്പ്',
  },
  futureRequest: {
    en: 'Future Request',
    hi: 'भविष्य का अनुरोध',
    kn: 'ಭವಿಷ್ಯದ ವಿನಂತಿ',
    te: 'భవిష్యత్తు అభ్యర్థన',
    ml: 'ഭാവി അഭ്യർത്ഥന',
  },
  healthMonitor: {
    en: 'Health Monitor',
    hi: 'स्वास्थ्य मॉनिटर',
    kn: 'ಆರೋಗ್ಯ ಮಾನಿಟರ್',
    te: 'ఆరోగ్య మానిటర్',
    ml: 'ഹെൽത്ത് മോണിറ്റർ',
  },
};

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider = ({ children }: { children: ReactNode }) => {
  const [language, setLanguage] = useState<Language>('en');

  const t = (key: string): string => {
    return translations[key]?.[language] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within LanguageProvider');
  }
  return context;
};
