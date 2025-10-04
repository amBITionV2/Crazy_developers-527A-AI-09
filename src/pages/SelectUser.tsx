import { useNavigate } from 'react-router-dom';
import { Heart, User } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { BloodCells } from '@/components/BloodCells';
import { LanguageSelector } from '@/components/LanguageSelector';
import { useLanguage } from '@/contexts/LanguageContext';

export const SelectUser = () => {
  const navigate = useNavigate();
  const { t } = useLanguage();

  return (
    <div className="min-h-screen bg-background relative overflow-hidden flex flex-col">
      <BloodCells />
      
      {/* Header */}
      <header className="relative z-10 container mx-auto px-4 py-6 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary to-primary/50 flex items-center justify-center animate-pulse-glow">
            <Heart className="w-6 h-6 text-white fill-white" />
          </div>
          <h1 className="text-2xl font-bold text-primary">{t('appName')}</h1>
        </div>
        <div className="flex items-center gap-4">
          <Button variant="outline" onClick={() => navigate('/')} className="border-primary/20 hover:bg-primary/10">
            Back
          </Button>
          <LanguageSelector />
        </div>
      </header>

      {/* Selection Cards */}
      <div className="relative z-10 flex-1 flex items-center justify-center px-4">
        <div className="w-full max-w-4xl space-y-8">
          <div className="text-center space-y-4 animate-fade-in">
            <h2 className="text-4xl md:text-5xl font-bold">{t('selectUserType')}</h2>
            <p className="text-xl text-muted-foreground">Choose your role to continue</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-12">
            {/* Donor Card */}
            <Card 
              className="bg-card/50 backdrop-blur-sm border-primary/20 hover:border-primary hover:shadow-[0_0_40px_rgba(220,38,38,0.3)] transition-all duration-300 cursor-pointer group animate-slide-up"
              onClick={() => navigate('/donor/register')}
            >
              <CardContent className="p-12 text-center space-y-6">
                <div className="mx-auto w-24 h-24 rounded-full bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                  <Heart className="w-12 h-12 text-primary" />
                </div>
                <div className="space-y-2">
                  <h3 className="text-3xl font-bold">{t('donor')}</h3>
                  <p className="text-muted-foreground">{t('donorDesc')}</p>
                </div>
                <Button 
                  className="w-full bg-primary hover:bg-primary/90 text-white"
                  onClick={(e) => {
                    e.stopPropagation();
                    navigate('/donor/register');
                  }}
                >
                  Continue as {t('donor')}
                </Button>
              </CardContent>
            </Card>

            {/* Patient Card */}
            <Card 
              className="bg-card/50 backdrop-blur-sm border-primary/20 hover:border-primary hover:shadow-[0_0_40px_rgba(220,38,38,0.3)] transition-all duration-300 cursor-pointer group animate-slide-up"
              style={{ animationDelay: '100ms' }}
              onClick={() => navigate('/patient/register')}
            >
              <CardContent className="p-12 text-center space-y-6">
                <div className="mx-auto w-24 h-24 rounded-full bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                  <User className="w-12 h-12 text-primary" />
                </div>
                <div className="space-y-2">
                  <h3 className="text-3xl font-bold">{t('patient')}</h3>
                  <p className="text-muted-foreground">{t('patientDesc')}</p>
                </div>
                <Button 
                  className="w-full bg-primary hover:bg-primary/90 text-white"
                  onClick={(e) => {
                    e.stopPropagation();
                    navigate('/patient/register');
                  }}
                >
                  Continue as {t('patient')}
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};
