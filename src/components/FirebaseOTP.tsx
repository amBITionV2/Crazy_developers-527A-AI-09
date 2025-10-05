import React, { useState, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Phone, AlertCircle, CheckCircle } from 'lucide-react';
import { firebaseAuthService } from '../services/firebaseAuth';

// Define user interface (matching the one in firebaseAuth.ts)
interface UserData {
  uid: string;
  phoneNumber: string | null;
  isAnonymous?: boolean;
  name?: string;
  email?: string;
  userType?: 'DONOR' | 'PATIENT';
  bloodGroup?: string;
  age?: number;
  weight?: number;
  gender?: string;
  isVerified?: boolean;
  isPhoneVerified?: boolean;
  createdAt?: string;
}

interface FirebaseOTPProps {
  onPhoneVerified: (phoneNumber: string, userData: UserData) => void;
  onError?: (error: string) => void;
}

export const FirebaseOTP: React.FC<FirebaseOTPProps> = ({ 
  onPhoneVerified, 
  onError 
}) => {
  const [step, setStep] = useState<'phone' | 'otp'>('phone');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    // Initialize reCAPTCHA when component mounts
    firebaseAuthService.initializeRecaptcha();
    
    return () => {
      // Cleanup when component unmounts
      firebaseAuthService.cleanup();
    };
  }, []);

  const formatPhoneNumber = (value: string) => {
    // Remove all non-digit characters
    const cleaned = value.replace(/\D/g, '');
    
    // Limit to 10 digits for Indian numbers
    const limited = cleaned.slice(0, 10);
    
    // Format as XXX XXX XXXX
    if (limited.length >= 6) {
      return `${limited.slice(0, 3)} ${limited.slice(3, 6)} ${limited.slice(6)}`;
    } else if (limited.length >= 3) {
      return `${limited.slice(0, 3)} ${limited.slice(3)}`;
    }
    return limited;
  };

  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatPhoneNumber(e.target.value);
    setPhoneNumber(formatted);
  };

  const handleSendOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      // Clean phone number and validate
      const cleaned = phoneNumber.replace(/\D/g, '');
      
      if (cleaned.length !== 10) {
        setError('Please enter a valid 10-digit mobile number');
        setLoading(false);
        return;
      }

      const fullPhoneNumber = `+91${cleaned}`;
      const result = await firebaseAuthService.sendOTP(fullPhoneNumber);

      if (result.success) {
        setSuccess(result.message);
        setStep('otp');
      } else {
        setError(result.message);
        onError?.(result.message);
      }
    } catch (error: unknown) {
      const errorMsg = 'Failed to send OTP. Please try again.';
      setError(errorMsg);
      onError?.(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      if (otp.length !== 6) {
        setError('Please enter a valid 6-digit OTP');
        setLoading(false);
        return;
      }

      const result = await firebaseAuthService.verifyOTP(otp);

      if (result.success) {
        setSuccess('Phone number verified successfully!');
        const cleaned = phoneNumber.replace(/\D/g, '');
        const fullPhoneNumber = `+91${cleaned}`;
        
        if (result.user) {
          onPhoneVerified(fullPhoneNumber, result.user);
        } else {
          setError('Verification successful but user data is missing');
          onError?.('Verification successful but user data is missing');
        }
      } else {
        setError(result.message);
        onError?.(result.message);
      }
    } catch (error: unknown) {
      const errorMsg = 'Failed to verify OTP. Please try again.';
      setError(errorMsg);
      onError?.(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleResendOTP = async () => {
    const cleaned = phoneNumber.replace(/\D/g, '');
    const fullPhoneNumber = `+91${cleaned}`;
    
    setError('');
    setSuccess('');
    setLoading(true);

    const result = await firebaseAuthService.sendOTP(fullPhoneNumber);
    
    if (result.success) {
      setSuccess('OTP resent successfully');
    } else {
      setError(result.message);
      onError?.(result.message);
    }
    
    setLoading(false);
  };

  const isValidPhone = phoneNumber.replace(/\D/g, '').length === 10;

  if (step === 'phone') {
    return (
      <form onSubmit={handleSendOTP} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="phone" className="text-sm font-medium">
            Phone Number
          </Label>
          <div className="flex">
            <div className="flex items-center px-3 bg-gray-50 border border-r-0 border-gray-300 rounded-l-md">
              <Phone className="h-4 w-4 text-gray-500 mr-2" />
              <span className="text-sm text-gray-600">+91</span>
            </div>
            <Input
              id="phone"
              type="tel"
              value={phoneNumber}
              onChange={handlePhoneChange}
              placeholder="Enter your phone number"
              className="rounded-l-none border-l-0 focus:ring-red-500 focus:border-red-500"
              disabled={loading}
              autoComplete="tel"
              maxLength={12} // XXX XXX XXXX format
            />
          </div>
          <p className="text-xs text-gray-500">
            We'll send you a verification code via SMS
          </p>
        </div>

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert>
            <CheckCircle className="h-4 w-4" />
            <AlertDescription>{success}</AlertDescription>
          </Alert>
        )}

        <Button
          type="submit"
          className="w-full bg-red-600 hover:bg-red-700 text-white"
          disabled={!isValidPhone || loading}
          size="lg"
        >
          {loading ? (
            <div className="flex items-center gap-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              Sending OTP...
            </div>
          ) : (
            'Send OTP'
          )}
        </Button>

        {/* Hidden reCAPTCHA container */}
        <div id="recaptcha-container"></div>

        <p className="text-xs text-center text-gray-500">
          By continuing, you agree to receive SMS messages from BloodAid
        </p>
      </form>
    );
  }

  return (
    <form onSubmit={handleVerifyOTP} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="otp" className="text-sm font-medium">
          Enter OTP
        </Label>
        <p className="text-sm text-gray-600">
          We've sent a 6-digit code to +91 {phoneNumber}
        </p>
        <Input
          id="otp"
          type="text"
          value={otp}
          onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
          placeholder="Enter 6-digit OTP"
          className="text-center text-lg tracking-widest focus:ring-red-500 focus:border-red-500"
          maxLength={6}
          disabled={loading}
        />
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert>
          <CheckCircle className="h-4 w-4" />
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

      <div className="space-y-2">
        <Button
          type="submit"
          className="w-full bg-red-600 hover:bg-red-700 text-white"
          disabled={otp.length < 6 || loading}
          size="lg"
        >
          {loading ? (
            <div className="flex items-center gap-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              Verifying...
            </div>
          ) : (
            'Verify OTP'
          )}
        </Button>

        <Button
          type="button"
          variant="outline"
          onClick={handleResendOTP}
          disabled={loading}
          className="w-full"
        >
          Resend OTP
        </Button>

        <Button
          type="button"
          variant="ghost"
          onClick={() => {
            setStep('phone');
            setOtp('');
            setError('');
            setSuccess('');
          }}
          className="w-full"
        >
          Change Phone Number
        </Button>
      </div>
    </form>
  );
};