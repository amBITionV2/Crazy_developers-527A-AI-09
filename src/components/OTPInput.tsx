import React, { useState, useRef, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

interface OTPInputProps {
  length?: number;
  onComplete: (otp: string) => void;
  onResend?: () => void;
  isLoading?: boolean;
  canResend?: boolean;
  resendCountdown?: number;
}

export const OTPInput: React.FC<OTPInputProps> = ({
  length = 6,
  onComplete,
  onResend,
  isLoading = false,
  canResend = false,
  resendCountdown = 0
}) => {
  const [otp, setOtp] = useState<string[]>(new Array(length).fill(''));
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    // Focus first input on mount
    if (inputRefs.current[0]) {
      inputRefs.current[0].focus();
    }
  }, []);

  const handleChange = (element: HTMLInputElement, index: number) => {
    if (isNaN(Number(element.value))) return false;

    const newOtp = [...otp];
    newOtp[index] = element.value;
    setOtp(newOtp);

    // Focus next input
    if (element.nextSibling && element.value !== '') {
      (element.nextSibling as HTMLInputElement).focus();
    }

    // Call onComplete when all fields are filled
    if (newOtp.every(digit => digit !== '') && newOtp.join('').length === length) {
      onComplete(newOtp.join(''));
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>, index: number) => {
    // Handle backspace
    if (e.key === 'Backspace') {
      e.preventDefault();
      const newOtp = [...otp];
      
      if (newOtp[index] !== '') {
        newOtp[index] = '';
        setOtp(newOtp);
      } else if (index > 0) {
        newOtp[index - 1] = '';
        setOtp(newOtp);
        inputRefs.current[index - 1]?.focus();
      }
    }
    
    // Handle arrow keys
    if (e.key === 'ArrowLeft' && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
    if (e.key === 'ArrowRight' && index < length - 1) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault();
    const pasteData = e.clipboardData.getData('text');
    const pasteArray = pasteData.slice(0, length).split('');
    
    if (pasteArray.every(char => !isNaN(Number(char)))) {
      const newOtp = new Array(length).fill('');
      pasteArray.forEach((char, index) => {
        if (index < length) newOtp[index] = char;
      });
      setOtp(newOtp);
      
      // Focus last filled input or first empty input
      const lastFilledIndex = Math.min(pasteArray.length - 1, length - 1);
      inputRefs.current[lastFilledIndex]?.focus();
      
      // Call onComplete if OTP is complete
      if (pasteArray.length === length) {
        onComplete(newOtp.join(''));
      }
    }
  };

  const clearOtp = () => {
    setOtp(new Array(length).fill(''));
    inputRefs.current[0]?.focus();
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-2 justify-center">
        {otp.map((digit, index) => (
          <Input
            key={index}
            ref={(el) => (inputRefs.current[index] = el)}
            type="text"
            inputMode="numeric"
            maxLength={1}
            value={digit}
            onChange={(e) => handleChange(e.target, index)}
            onKeyDown={(e) => handleKeyDown(e, index)}
            onPaste={handlePaste}
            className="w-12 h-12 text-center text-lg font-semibold border-2 rounded-lg focus:border-red-500 focus:ring-red-500"
            disabled={isLoading}
            autoComplete="one-time-code"
          />
        ))}
      </div>
      
      <div className="flex justify-center gap-2">
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={clearOtp}
          disabled={isLoading}
        >
          Clear
        </Button>
        
        {onResend && (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={onResend}
            disabled={isLoading || !canResend}
            className="text-red-600 hover:text-red-700"
          >
            {resendCountdown > 0 
              ? `Resend in ${resendCountdown}s` 
              : 'Resend OTP'
            }
          </Button>
        )}
      </div>
    </div>
  );
};