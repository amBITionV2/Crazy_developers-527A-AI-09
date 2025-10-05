// Mock API responses for testing the interface when backend is not available
import { User, AuthResponse, SOSResponse, HealthResponse, HealthVitals, EmergencyAlert, DonationHistory, ScheduledDonation } from './api';

// Mock delay to simulate network requests
const mockDelay = (ms: number = 1000) => new Promise(resolve => setTimeout(resolve, ms));

// Mock user data
const mockUsers: User[] = [
  {
    id: '1',
    name: 'John Doe',
    email: 'john.doe@example.com',
    userType: 'donor',
    eRaktKoshId: 'RK123456',
    isVerified: true,
  },
  {
    id: '2',
    name: 'Jane Smith',
    email: 'jane.smith@example.com',
    userType: 'patient',
    username: 'janesmith',
    isVerified: true,
  },
];

// Mock authentication API
export const mockAuthAPI = {
  registerDonor: async (data: {
    eRaktKoshId?: string;
    name: string;
    email: string;
    phone: string;
    password: string;
  }) => {
    await mockDelay();
    const user: User = {
      id: Date.now().toString(),
      name: data.name,
      email: data.email,
      userType: 'donor',
      eRaktKoshId: data.eRaktKoshId,
      isVerified: true,
    };
    
    return {
      access_token: 'mock_token_' + Date.now(),
      user,
      success: true,
      message: 'Donor registered successfully',
    };
  },

  registerPatient: async (data: {
    name: string;
    email: string;
    phone: string;
    password: string;
    username: string;
    bloodGroup: string;
  }) => {
    await mockDelay();
    const user: User = {
      id: Date.now().toString(),
      name: data.name,
      email: data.email,
      userType: 'patient',
      username: data.username,
      isVerified: true,
    };
    
    return {
      access_token: 'mock_token_' + Date.now(),
      user,
      success: true,
      message: 'Patient registered successfully',
    };
  },

  login: async (data: {
    email: string;
    password: string;
    userType: 'donor' | 'patient';
  }): Promise<AuthResponse> => {
    await mockDelay();
    
    // Mock successful login
    const user: User = {
      id: '1',
      name: data.userType === 'donor' ? 'John Doe' : 'Jane Smith',
      email: data.email,
      userType: data.userType,
      eRaktKoshId: data.userType === 'donor' ? 'RK123456' : undefined,
      username: data.userType === 'patient' ? 'janesmith' : undefined,
      isVerified: true,
    };
    
    return {
      success: true,
      user,
      token: 'mock_token_' + Date.now(),
      message: 'Login successful',
      redirectTo: data.userType === 'donor' ? '/donor/dashboard' : '/patient/dashboard',
    };
  },

  verifyToken: async (token: string) => {
    await mockDelay(500);
    return {
      valid: true,
      user: mockUsers[0],
    };
  },
};

// Mock emergency API
export const mockEmergencyAPI = {
  sendSOS: async (data: {
    patientName: string;
    hospitalName: string;
    bloodType: string;
    urgencyLevel: 'critical' | 'high' | 'medium';
    location: { latitude: number; longitude: number };
    contactInfo: string;
  }): Promise<SOSResponse> => {
    await mockDelay();
    return {
      success: true,
      alertId: 'alert_' + Date.now(),
      message: 'SOS alert sent successfully',
      donorsFound: [
        {
          id: '1',
          name: 'John Doe',
          distance: '2.5 km',
          area: 'Central Mumbai',
          bloodGroup: 'O+',
          phone: '+91 98765 43210',
          isAvailable: true,
        },
        {
          id: '2',
          name: 'Alice Kumar',
          distance: '4.1 km',
          area: 'Bandra West',
          bloodGroup: 'O+',
          phone: '+91 87654 32109',
          isAvailable: true,
        },
      ],
      searchRadius: '10 km',
    };
  },

  respondToEmergency: async (data: { alertId: string; response: 'accept' | 'decline' }) => {
    await mockDelay();
    return {
      success: true,
      message: data.response === 'accept' ? 'Emergency response accepted' : 'Emergency response declined',
    };
  },

  getEmergencyAlerts: async () => {
    await mockDelay();
    const alerts: EmergencyAlert[] = [
      {
        id: '1',
        patientName: 'Emergency Patient',
        hospitalName: 'City Hospital',
        bloodType: 'A+',
        urgencyLevel: 'critical',
        location: { latitude: 19.0760, longitude: 72.8777 },
        contactInfo: '+91 98765 43210',
        createdAt: new Date().toISOString(),
        status: 'active',
      },
    ];
    
    return {
      success: true,
      alerts,
    };
  },
};

// Mock health API
export const mockHealthAPI = {
  updateVitals: async (vitals: HealthVitals): Promise<HealthResponse> => {
    await mockDelay();
    return {
      success: true,
      healthScore: 85.5,
      vitals,
      recommendations: [
        'Your blood pressure is normal',
        'Hemoglobin levels are good for donation',
        'Stay hydrated before donating',
      ],
      donationEligible: true,
    };
  },

  getHealthScore: async (userId: string) => {
    await mockDelay();
    return {
      healthScore: 85.5,
      vitals: {
        bloodPressure: { systolic: 120, diastolic: 80 },
        hemoglobin: 14.2,
        heartRate: 72,
        temperature: 98.6,
        oxygenLevel: 98,
        sugarLevel: 95,
      },
      lastUpdated: new Date().toISOString(),
    };
  },

  checkDonationEligibility: async (donorId: string) => {
    await mockDelay();
    return {
      isEligible: true,
      lastDonation: '45 days ago',
      nextEligibleDate: new Date().toISOString(),
      totalDonations: 12,
      healthScore: 85.5,
      restrictions: [],
    };
  },
};

// Mock donations API
export const mockDonationsAPI = {
  getHistory: async (userId: string): Promise<DonationHistory[]> => {
    await mockDelay();
    return [
      {
        id: '1',
        recipientName: 'Emergency Case #1',
        hospital: 'City Hospital',
        bloodGroup: 'O+',
        date: '2024-01-15',
        status: 'Completed',
        units: 1,
      },
      {
        id: '2',
        recipientName: 'Emergency Case #2',
        hospital: 'Metro Hospital',
        bloodGroup: 'O+',
        date: '2023-10-22',
        status: 'Completed',
        units: 1,
      },
    ];
  },

  getScheduled: async (donorId: string): Promise<ScheduledDonation[]> => {
    await mockDelay();
    return [
      {
        id: '1',
        patient: 'John Patient',
        hospital: 'City Hospital',
        date: '2024-02-20',
        status: 'Confirmed',
      },
    ];
  },

  respondToRequest: async (data: { donationId: string; response: 'accept' | 'decline' }) => {
    await mockDelay();
    return {
      success: true,
      message: data.response === 'accept' ? 'Donation request accepted' : 'Donation request declined',
      donationStatus: data.response === 'accept' ? 'accepted' : 'declined',
    };
  },

  requestDonation: async (data: {
    donorId: string;
    hospitalName: string;
    scheduledDate: string;
    bloodType: string;
    units: number;
    urgency: string;
  }) => {
    await mockDelay();
    return {
      success: true,
      message: 'Donation request sent successfully',
      donationId: 'donation_' + Date.now(),
    };
  },

  getStats: async (userId: string) => {
    await mockDelay();
    return {
      totalDonations: 12,
      pendingRequests: 2,
      livesImpacted: 36,
      nextEligibleDate: '2024-04-15',
    };
  },
};

// Mock health check
export const mockHealthCheck = async () => {
  await mockDelay(500);
  return {
    status: 'healthy',
    service: 'Mock BloodAid API',
    version: '1.0.0',
  };
};