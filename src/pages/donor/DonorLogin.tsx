import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft, Mail, Lock } from 'lucide-react';
import { BloodCells } from '@/components/BloodCells';
import { toast } from 'sonner';
import { useLanguage } from '@/contexts/LanguageContext';
import { authAPI } from '@/lib/api'; // Using real API

export const DonorLogin = () => {
  const navigate = useNavigate();
  const { t } = useLanguage();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.email || !formData.password) {
      toast.error('Please fill in all fields');
      return;
    }

    setLoading(true);

    try {
      // Using real API with your backend
      console.log('Attempting login with:', { email: formData.email, userType: 'donor' });
      
      const response = await authAPI.login({
        email: formData.email,
        password: formData.password,
        userType: 'donor',
      });

      console.log('Login response:', response);

      if (response.success) {
        // Store auth data
        localStorage.setItem('authToken', response.token);
        localStorage.setItem('user', JSON.stringify(response.user));
        localStorage.setItem('userId', response.user.id); // Add userId for dashboard compatibility
        
        toast.success('Login successful!');
        navigate('/donor/dashboard');
      } else {
        console.error('Login failed - response not successful:', response);
        toast.error(response.message || 'Invalid credentials');
      }
    } catch (error) {
      console.error('Login error:', error);
      
      // Enhanced error handling
      if (error instanceof Error) {
        if (error.message.includes('Network Error') || error.message.includes('fetch')) {
          toast.error('Unable to connect to server. Please check your connection.');
        } else if (error.message.includes('400')) {
          toast.error('Invalid email or password format.');
        } else if (error.message.includes('401')) {
          toast.error('Invalid credentials. Please check your email and password.');
        } else if (error.message.includes('404')) {
          toast.error('Login service not found. Please contact support.');
        } else {
          toast.error(`Login failed: ${error.message}`);
        }
      } else {
        toast.error('Login failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-red-100 relative overflow-hidden">
      <BloodCells />
      
      <div className="relative z-10 container mx-auto px-4 py-8">
        <Button
          variant="ghost"
          onClick={() => navigate('/select-user')}
          className="mb-6 text-red-600 hover:text-red-700 hover:bg-red-50"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>

        <div className="max-w-md mx-auto">
          <Card className="backdrop-blur-sm bg-white/80 border-red-200 shadow-xl">
            <CardHeader className="text-center">
              <CardTitle className="text-2xl font-bold text-red-600">
                Donor Login
              </CardTitle>
              <p className="text-gray-600">
                Sign in to access your account
              </p>
            </CardHeader>
            
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">
                    Email Address
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      placeholder="Enter your email"
                      className="pl-10 border-red-200 focus:border-red-500"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">
                    Password
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      name="password"
                      type="password"
                      value={formData.password}
                      onChange={handleInputChange}
                      placeholder="Enter your password"
                      className="pl-10 border-red-200 focus:border-red-500"
                    />
                  </div>
                </div>

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-red-600 hover:bg-red-700 text-white py-3"
                >
                  {loading ? 'Signing In...' : 'Sign In'}
                </Button>
              </form>

              <div className="mt-6 text-center">
                <p className="text-sm text-gray-600">
                  Don't have an account?{' '}
                  <button
                    onClick={() => navigate('/donor/register')}
                    className="text-red-600 hover:text-red-700 font-medium"
                  >
                    Register here
                  </button>
                </p>
                
                {/* Demo Login for Testing */}
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <p className="text-xs text-gray-500 mb-2">For testing purposes:</p>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      // Demo login without backend
                      const mockUser = {
                        id: 'demo-donor-123',
                        name: 'Test Donor',
                        email: 'donor@test.com',
                        userType: 'donor' as const,
                        bloodGroup: 'O+',
                        isVerified: true
                      };
                      
                      // Store mock auth data
                      localStorage.setItem('authToken', 'demo-token-123');
                      localStorage.setItem('user', JSON.stringify(mockUser));
                      localStorage.setItem('userId', mockUser.id);
                      
                      toast.success('Demo login successful!');
                      navigate('/donor/dashboard');
                    }}
                    className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 border-gray-300"
                  >
                    🚀 Demo Login (No Backend Required)
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
