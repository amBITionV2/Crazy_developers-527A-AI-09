import { 
  signInWithPhoneNumber, 
  RecaptchaVerifier, 
  ConfirmationResult,
  PhoneAuthProvider,
  signInWithCredential,
  createUserWithEmailAndPassword,
  updateProfile
} from 'firebase/auth';
import { auth } from '../firebase';

// Define user interface
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

interface AuthResponse {
  success: boolean;
  message: string;
  user?: UserData;
}

class FirebaseAuthService {
  private recaptchaVerifier: RecaptchaVerifier | null = null;
  private confirmationResult: ConfirmationResult | null = null;

  // Initialize reCAPTCHA
  initializeRecaptcha(elementId: string = 'recaptcha-container') {
    if (!this.recaptchaVerifier) {
      this.recaptchaVerifier = new RecaptchaVerifier(auth, elementId, {
        size: 'invisible',
        callback: () => {
          console.log('reCAPTCHA verified');
        },
        'expired-callback': () => {
          console.log('reCAPTCHA expired');
          this.recaptchaVerifier = null;
        }
      });
    }
    return this.recaptchaVerifier;
  }

  // Send OTP to phone number
  async sendOTP(phoneNumber: string): Promise<{ success: boolean; message: string }> {
    try {
      // Ensure phone number is in international format
      const formattedPhone = phoneNumber.startsWith('+') ? phoneNumber : `+91${phoneNumber}`;
      
      if (!this.recaptchaVerifier) {
        this.initializeRecaptcha();
      }

      this.confirmationResult = await signInWithPhoneNumber(
        auth, 
        formattedPhone, 
        this.recaptchaVerifier!
      );

      return {
        success: true,
        message: `OTP sent to ${formattedPhone}`
      };
    } catch (error: unknown) {
      console.error('Error sending OTP:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to send OTP';
      return {
        success: false,
        message: errorMessage
      };
    }
  }

  // Verify OTP
  async verifyOTP(otp: string): Promise<AuthResponse> {
    try {
      if (!this.confirmationResult) {
        return {
          success: false,
          message: 'No OTP request found. Please request OTP first.'
        };
      }

      const result = await this.confirmationResult.confirm(otp);
      const user = result.user;

      return {
        success: true,
        message: 'Phone number verified successfully',
        user: {
          uid: user.uid,
          phoneNumber: user.phoneNumber,
          isAnonymous: user.isAnonymous
        }
      };
    } catch (error: unknown) {
      console.error('Error verifying OTP:', error);
      const errorMessage = error instanceof Error ? error.message : 'Invalid OTP';
      return {
        success: false,
        message: errorMessage
      };
    }
  }

  // Complete registration with additional user details
  async completeRegistration(userDetails: {
    name: string;
    email: string;
    userType: 'DONOR' | 'PATIENT';
    bloodGroup: string;
    age: number;
    weight?: number;
    gender: string;
  }): Promise<AuthResponse> {
    try {
      const currentUser = auth.currentUser;
      if (!currentUser) {
        return {
          success: false,
          message: 'No authenticated user found'
        };
      }

      // Update user profile
      await updateProfile(currentUser, {
        displayName: userDetails.name
      });

      // You can store additional user details in Firestore or your backend
      const userData = {
        uid: currentUser.uid,
        name: userDetails.name,
        email: userDetails.email,
        phoneNumber: currentUser.phoneNumber,
        userType: userDetails.userType,
        bloodGroup: userDetails.bloodGroup,
        age: userDetails.age,
        weight: userDetails.weight,
        gender: userDetails.gender,
        isVerified: true,
        isPhoneVerified: true,
        createdAt: new Date().toISOString()
      };

      // Store user data in your backend
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/users/profile`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await currentUser.getIdToken()}`
        },
        body: JSON.stringify(userData)
      });

      if (response.ok) {
        return {
          success: true,
          message: 'Registration completed successfully',
          user: userData
        };
      } else {
        return {
          success: false,
          message: 'Failed to save user profile'
        };
      }
    } catch (error: unknown) {
      console.error('Error completing registration:', error);
      const errorMessage = error instanceof Error ? error.message : 'Registration failed';
      return {
        success: false,
        message: errorMessage
      };
    }
  }

  // Clean up
  cleanup() {
    if (this.recaptchaVerifier) {
      this.recaptchaVerifier.clear();
      this.recaptchaVerifier = null;
    }
    this.confirmationResult = null;
  }

  // Get current user
  getCurrentUser() {
    return auth.currentUser;
  }

  // Sign out
  async signOut() {
    try {
      await auth.signOut();
      this.cleanup();
      return { success: true, message: 'Signed out successfully' };
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Sign out failed';
      return { success: false, message: errorMessage };
    }
  }
}

export const firebaseAuthService = new FirebaseAuthService();
export default firebaseAuthService;