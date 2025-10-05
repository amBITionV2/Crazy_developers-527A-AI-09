import React, { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Phone, AlertCircle } from 'lucide-react';

interface PhoneInputProps {
  onSendOTP: (phoneNumber: string) => void;
  isLoading?: boolean;
  error?: string;
  defaultCountryCode?: string;
  placeholder?: string;
  label?: string;
}

export const PhoneInput: React.FC<PhoneInputProps> = ({
  onSendOTP,
  isLoading = false,
  error,
  defaultCountryCode = '+91',
  placeholder = 'Enter your phone number',
  label = 'Phone Number'
}) => {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [countryCode] = useState(defaultCountryCode);

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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Clean phone number and validate
    const cleaned = phoneNumber.replace(/\D/g, '');
    
    if (cleaned.length !== 10) {
      return;
    }
    
    // Format for API call
    const formattedNumber = `${countryCode}${cleaned}`;
    onSendOTP(formattedNumber);
  };

  const isValidPhone = phoneNumber.replace(/\D/g, '').length === 10;

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="phone" className="text-sm font-medium">
          {label}
        </Label>
        <div className="flex">
          <div className="flex items-center px-3 bg-gray-50 border border-r-0 border-gray-300 rounded-l-md">
            <Phone className="h-4 w-4 text-gray-500 mr-2" />
            <span className="text-sm text-gray-600">{countryCode}</span>
          </div>
          <Input
            id="phone"
            type="tel"
            value={phoneNumber}
            onChange={handlePhoneChange}
            placeholder={placeholder}
            className="rounded-l-none border-l-0 focus:ring-red-500 focus:border-red-500"
            disabled={isLoading}
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

      <Button
        type="submit"
        className="w-full bg-red-600 hover:bg-red-700 text-white"
        disabled={!isValidPhone || isLoading}
        size="lg"
      >
        {isLoading ? (
          <div className="flex items-center gap-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            Sending OTP...
          </div>
        ) : (
          'Send OTP'
        )}
      </Button>

      <p className="text-xs text-center text-gray-500">
        By continuing, you agree to receive SMS messages from BloodAid
      </p>
    </form>
  );
};