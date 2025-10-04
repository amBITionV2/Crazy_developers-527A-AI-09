import { useNavigate } from 'react-router-dom';
import { Activity, Brain, Globe, Heart, Bell, Mic } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { BloodCells } from '@/components/BloodCells';
import { LanguageSelector } from '@/components/LanguageSelector';
import { FeatureCard } from '@/components/FeatureCard';
import { useLanguage } from '@/contexts/LanguageContext';

export const Landing = () => {
  const navigate = useNavigate();
  const { t } = useLanguage();

  const features = [
    {
      icon: Heart,
      title: t('smartNetwork'),
      description: t('smartNetworkDesc'),
      delay: 0,
    },
    {
      icon: Activity,
      title: t('healthTracker'),
      description: t('healthTrackerDesc'),
      delay: 100,
    },
    {
      icon: Globe,
      title: t('multiLanguage'),
      description: t('multiLanguageDesc'),
      delay: 200,
    },
    {
      icon: Brain,
      title: t('aiAssistant'),
      description: t('aiAssistantDesc'),
      delay: 300,
    },
    {
      icon: Mic,
      title: t('voiceAssistant'),
      description: t('voiceAssistantDesc'),
      delay: 400,
    },
    {
      icon: Bell,
      title: t('emergencyAlerts'),
      description: t('emergencyAlertsDesc'),
      delay: 500,
    },
  ];

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      <BloodCells />
      
      {/* Header */}
      <header className="relative z-10 container mx-auto px-4 py-6 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary to-primary/50 flex items-center justify-center animate-pulse-glow">
            <Heart className="w-6 h-6 text-white fill-white" />
          </div>
          <h1 className="text-2xl font-bold text-primary">{t('appName')}</h1>
        </div>
        <LanguageSelector />
      </header>

      {/* Hero Section */}
      <section className="relative z-10 container mx-auto px-4 py-20 text-center">
        <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
          <h2 className="text-5xl md:text-7xl font-bold leading-tight">
            {t('appName')}
          </h2>
          <p className="text-xl md:text-2xl text-primary/80 font-semibold">
            {t('tagline')}
          </p>
          <p className="text-lg text-muted-foreground max-w-3xl mx-auto leading-relaxed">
            {t('description')}
          </p>
          <Button
            size="lg"
            onClick={() => navigate('/select-user')}
            className="mt-8 bg-primary hover:bg-primary/90 text-white px-12 py-6 text-lg rounded-full shadow-[0_0_40px_rgba(220,38,38,0.4)] hover:shadow-[0_0_60px_rgba(220,38,38,0.6)] transition-all duration-300 animate-pulse-glow"
          >
            {t('getStarted')}
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-20 max-w-4xl mx-auto">
          <div className="bg-card/30 backdrop-blur-sm border border-primary/20 rounded-lg p-6">
            <div className="text-4xl font-bold text-primary">1-5 km</div>
            <div className="text-muted-foreground mt-2">Donor Search Radius</div>
          </div>
          <div className="bg-card/30 backdrop-blur-sm border border-primary/20 rounded-lg p-6">
            <div className="text-4xl font-bold text-primary">24/7</div>
            <div className="text-muted-foreground mt-2">AI Health Assistant</div>
          </div>
          <div className="bg-card/30 backdrop-blur-sm border border-primary/20 rounded-lg p-6">
            <div className="text-4xl font-bold text-primary">5+</div>
            <div className="text-muted-foreground mt-2">Languages Supported</div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative z-10 container mx-auto px-4 py-20">
        <h3 className="text-4xl font-bold text-center mb-12">{t('features')}</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <FeatureCard key={index} {...feature} />
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 container mx-auto px-4 py-20 text-center">
        <div className="max-w-2xl mx-auto bg-gradient-to-br from-primary/10 to-primary/5 border border-primary/20 rounded-2xl p-12 space-y-6">
          <h3 className="text-3xl font-bold">Ready to Save Lives?</h3>
          <p className="text-muted-foreground text-lg">
            Join thousands of verified donors and patients in making blood donation fast, smart, and compassionate.
          </p>
          <Button
            size="lg"
            onClick={() => navigate('/select-user')}
            className="bg-primary hover:bg-primary/90 text-white px-12 py-6 text-lg rounded-full shadow-[0_0_40px_rgba(220,38,38,0.4)] hover:shadow-[0_0_60px_rgba(220,38,38,0.6)] transition-all duration-300"
          >
            {t('getStarted')}
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-primary/20 mt-20">
        <div className="container mx-auto px-4 py-8 text-center text-muted-foreground">
          <p>© 2025 {t('appName')}. Saving lives, one drop at a time.</p>
        </div>
      </footer>
    </div>
  );
};
