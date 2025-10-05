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
import { authAPI } from '@/lib/api'; // Using real API

export const PatientRegister = () => {
  const navigate = useNavigate();
  const { t } = useLanguage();
  const [formData, setFormData] = useState({
    name: '',
    username: '',
    email: '',
    phone: '',
    password: '',
    bloodGroup: 'O+',
  });
  const [loading, setLoading] = useState(false);

  // Form validation helper
  const isFormValid = () => {
    return (
      formData.name.trim().length > 0 &&
      formData.username.trim().length > 0 &&
      formData.email.trim().length > 0 &&
      formData.phone.length >= 10 &&
      formData.password.length >= 6
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    // Additional validation
    if (!formData.name.trim()) {
      toast.error('Please enter your full name');
      setLoading(false);
      return;
    }
    
    if (!formData.username.trim()) {
      toast.error('Please enter a username');
      setLoading(false);
      return;
    }
    
    if (!formData.password || formData.password.length < 6) {
      toast.error('Password must be at least 6 characters long');
      setLoading(false);
      return;
    }
    
    try {
      // Using real API with your backend
      console.log('Attempting registration with data:', {
        name: formData.name.trim(),
        email: formData.email.trim(),
        phone: formData.phone.trim(),
        username: formData.username.trim(),
        bloodGroup: formData.bloodGroup,
      });

      const response = await authAPI.registerPatient({
        name: formData.name.trim(),
        email: formData.email.trim(),
        phone: formData.phone.trim(),
        password: formData.password,
        username: formData.username.trim(),
        bloodGroup: formData.bloodGroup,
      });

      console.log('Registration response:', response);

      if (response.success) {
        // Store auth data
        localStorage.setItem('authToken', response.access_token);
        localStorage.setItem('user', JSON.stringify(response.user));
        localStorage.setItem('userType', 'patient');
        localStorage.setItem('isLoggedIn', 'true');
        
        toast.success('Registration successful! Redirecting to dashboard...');
        navigate('/patient/dashboard');
      } else {
        toast.error(response.message || 'Registration failed. Please try again.');
      }
    } catch (error: unknown) {
      console.error('Registration error:', error);
      
      // More specific error handling
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as { response: { data?: { detail?: string; message?: string } } };
        const errorMessage = axiosError.response.data?.detail || axiosError.response.data?.message || 'Registration failed. Please try again.';
        toast.error(errorMessage);
      } else if (error && typeof error === 'object' && 'request' in error) {
        toast.error('Cannot connect to server. Please check your internet connection.');
      } else {
        toast.error('Registration failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
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
                <Label htmlFor="bloodGroup">Blood Group</Label>
                <select
                  id="bloodGroup"
                  value={formData.bloodGroup}
                  onChange={(e) => setFormData({ ...formData, bloodGroup: e.target.value })}
                  required
                  className="w-full px-3 py-2 bg-background/50 border border-primary/20 rounded-md focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                >
                  <option value="O+">O+</option>
                  <option value="O-">O-</option>
                  <option value="A+">A+</option>
                  <option value="A-">A-</option>
                  <option value="B+">B+</option>
                  <option value="B-">B-</option>
                  <option value="AB+">AB+</option>
                  <option value="AB-">AB-</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="phone">Phone Number</Label>
                <Input
                  id="phone"
                  type="tel"
                  placeholder="Enter your phone number"
                  value={formData.phone}
                  onChange={(e) => {
                    // Allow only numbers and basic formatting
                    const value = e.target.value.replace(/[^\d+\-\s()]/g, '');
                    setFormData({ ...formData, phone: value });
                  }}
                  required
                  className="bg-background/50 border-primary/20 focus:border-primary"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Create a password (min 6 characters)"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  required
                  minLength={6}
                  className="bg-background/50 border-primary/20 focus:border-primary"
                />
                <p className="text-xs text-muted-foreground">
                  Password must be at least 6 characters long
                </p>
              </div>

              <Button 
                type="submit" 
                disabled={loading || !isFormValid()}
                className="w-full bg-primary hover:bg-primary/90 text-white py-6 text-lg disabled:opacity-50 transition-all duration-200"
              >
                {loading ? 'Registering...' : `Register as ${t('patient')}`}
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
