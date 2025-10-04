import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Heart, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BloodCells } from '@/components/BloodCells';
import { LanguageSelector } from '@/components/LanguageSelector';
import { useLanguage } from '@/contexts/LanguageContext';
import { toast } from 'sonner';

export const PatientRegister = () => {
  const navigate = useNavigate();
  const { t } = useLanguage();
  const [formData, setFormData] = useState({
    name: '',
    username: '',
    email: '',
    phone: '',
    otp: '',
  });
  const [otpSent, setOtpSent] = useState(false);

  const handleSendOTP = () => {
    if (!formData.phone) {
      toast.error('Please enter your phone number');
      return;
    }
    // Here you would integrate with Firebase to send OTP
    toast.success('OTP sent to your phone!');
    setOtpSent(true);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Here you would integrate with Firebase Auth and verify OTP
    toast.success('Registration successful! Redirecting to dashboard...');
    setTimeout(() => navigate('/patient/dashboard'), 2000);
  };

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
          <Button 
            variant="outline" 
            onClick={() => navigate('/select-user')}
            className="border-primary/20 hover:bg-primary/10"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <LanguageSelector />
        </div>
      </header>

      {/* Registration Form */}
      <div className="relative z-10 flex-1 flex items-center justify-center px-4 py-12">
        <Card className="w-full max-w-md bg-card/50 backdrop-blur-sm border-primary/20 animate-slide-up">
          <CardHeader>
            <CardTitle className="text-3xl text-center">{t('patient')} Registration</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="name">Full Name</Label>
                <Input
                  id="name"
                  placeholder="Enter your full name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  className="bg-background/50 border-primary/20 focus:border-primary"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  placeholder="Choose a username"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  required
                  className="bg-background/50 border-primary/20 focus:border-primary"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="Enter your email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                  className="bg-background/50 border-primary/20 focus:border-primary"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="phone">Phone Number</Label>
                <div className="flex gap-2">
                  <Input
                    id="phone"
                    type="tel"
                    placeholder="Enter your phone number"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    required
                    className="bg-background/50 border-primary/20 focus:border-primary flex-1"
                  />
                  <Button
                    type="button"
                    onClick={handleSendOTP}
                    variant="outline"
                    className="border-primary/20 hover:bg-primary/10"
                  >
                    Send OTP
                  </Button>
                </div>
              </div>

              {otpSent && (
                <div className="space-y-2">
                  <Label htmlFor="otp">OTP</Label>
                  <Input
                    id="otp"
                    placeholder="Enter OTP"
                    value={formData.otp}
                    onChange={(e) => setFormData({ ...formData, otp: e.target.value })}
                    required
                    className="bg-background/50 border-primary/20 focus:border-primary"
                  />
                </div>
              )}

              <Button 
                type="submit" 
                className="w-full bg-primary hover:bg-primary/90 text-white py-6 text-lg"
                disabled={!otpSent}
              >
                Register as {t('patient')}
              </Button>

              <p className="text-center text-sm text-muted-foreground">
                Already have an account?{' '}
                <button
                  type="button"
                  onClick={() => navigate('/patient/login')}
                  className="text-primary hover:underline"
                >
                  Login here
                </button>
              </p>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
