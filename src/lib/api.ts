import axios, { AxiosResponse } from 'axios';

// Create axios instance with base configuration
const API = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8003/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds timeout
});

// Request interceptor to add auth token
API.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for global error handling
API.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// API Interface Types
export interface User {
  id: string;
  name: string;
  email: string;
  userType: 'donor' | 'patient';
  eRaktKoshId?: string;
  username?: string;
  isVerified?: boolean;
}

export interface AuthResponse {
  success: boolean;
  user: User;
  token: string;
  message: string;
  redirectTo?: string;
}

export interface SOSAlert {
  patient_name: string;
  blood_group: string;
  urgency_level: 'CRITICAL' | 'HIGH' | 'MEDIUM';
  state: string;
  district: string;
  hospital_name: string;
  hospital_address: string;
  contact_number: string;
  units_needed?: number;
  additional_info?: string;
  patient_age?: number;
  medical_condition?: string;
}

export interface ERaktkoshBloodBank {
  name: string;
  location: string;
  contact: string;
  availability: string;
  last_updated: string;
}

export interface ERaktkoshData {
  timestamp: string;
  request_details: {
    blood_group: string;
    location: string;
    urgency: string;
  };
  blood_availability: {
    total_banks: number;
    blood_banks: ERaktkoshBloodBank[];
    search_timestamp: string;
  };
  nearby_blood_centers: Array<{
    name: string;
    address: string;
    phone: string;
    email: string;
    timings: string;
  }>;
  upcoming_camps: Array<{
    date: string;
    time: string;
    venue: string;
    organizer: string;
    contact: string;
  }>;
  emergency_contacts: Array<{
    service: string;
    number: string;
    type: string;
  }>;
  recommendations: string[];
}

export interface EmergencySOSResponse {
  sos_id: string;
  status: 'SUCCESS' | 'LIMITED_AVAILABILITY' | 'ERROR';
  message: string;
  timestamp: string;
  eraktkosh_data: ERaktkoshData;
  local_donors: Array<{
    donor_id: string;
    name: string;
    blood_group: string;
    phone: string;
    last_donation: string | null;
    location: string;
    availability_status: string;
  }>;
  emergency_actions: string[];
}

export interface DonorMatch {
  id: string;
  name: string;
  distance: string;
  area: string;
  bloodGroup: string;
  phone: string;
  isAvailable: boolean;
}

export interface SOSResponse {
  success: boolean;
  alert_id: string;
  message: string;
  donors_found: DonorMatch[];
  search_radius: string;
}

export interface HealthVitals {
  bloodPressure: {
    systolic: number;
    diastolic: number;
  };
  hemoglobin: number;
  heartRate: number;
  temperature: number;
  oxygenLevel: number;
  sugarLevel: number;
}

export interface HealthResponse {
  success: boolean;
  healthScore: number;
  vitals: HealthVitals;
  recommendations: string[];
  donationEligible: boolean;
}

export interface ChatRequest {
  message: string;
  language: string;
  context: string;
  userId: string;
}

export interface ChatResponse {
  response: string;
  language: string;
  suggestions?: string[];
}

export interface DonationHistory {
  id: string;
  recipientName: string;
  hospital: string;
  bloodGroup: string;
  date: string;
  status: string;
  units: number;
}

export interface ScheduledDonation {
  id: string;
  patient: string;
  hospital: string;
  date: string;
  status: string;
}

export interface EmergencyAlert {
  id: string;
  patientName: string;
  hospitalName: string;
  bloodType: string;
  urgencyLevel: 'critical' | 'high' | 'medium';
  location: {
    latitude: number;
    longitude: number;
  };
  contactInfo: string;
  createdAt: string;
  status: 'active' | 'fulfilled' | 'expired';
}

// Authentication API
export const authAPI = {
  // Donor Registration
  registerDonor: async (data: {
    eRaktKoshId?: string;
    name: string;
    email: string;
    phone: string;
    password: string;
    bloodGroup?: string;
  }): Promise<{
    access_token: string;
    user: User;
    success: boolean;
    message: string;
  }> => {
    const response = await API.post('/auth/donor/register', {
      eraktkosh_id: data.eRaktKoshId || '',
      name: data.name,
      email: data.email,
      phone: data.phone,
      password: data.password,
      blood_group: data.bloodGroup || 'O_POS', // Default blood group if not provided
    });
    return response.data;
  },

  // Patient Registration
  registerPatient: async (data: {
    name: string;
    email: string;
    phone: string;
    password: string;
    username: string;
    bloodGroup: string;
  }): Promise<{
    access_token: string;
    user: User;
    success: boolean;
    message: string;
  }> => {
    const response = await API.post('/auth/patient/register', {
      name: data.name,
      email: data.email,
      phone: data.phone,
      password: data.password,
      username: data.username,
      blood_group: data.bloodGroup,
    });
    return response.data;
  },

  // Patient OTP sending
  sendOTP: async (phone: string): Promise<{ 
    success: boolean; 
    message: string; 
    expires_at?: string;
    otp_code?: string;
  }> => {
    const response = await API.post('/auth/otp/send', { 
      phone_number: phone,
      purpose: 'registration'
    });
    return response.data;
  },

  // Patient OTP verification and registration
  verifyOTP: async (data: {
    phone: string;
    otp: string;
    name: string;
    username: string;
    email: string;
  }): Promise<AuthResponse> => {
    const response = await API.post('/auth/patient/verify-otp', data);
    return response.data;
  },

  // Universal login
  login: async (data: {
    email: string;
    password: string;
    userType: 'donor' | 'patient';
  }): Promise<AuthResponse> => {
    const response = await API.post('/auth/login', {
      email: data.email,
      password: data.password,
      user_type: data.userType, // Transform userType to user_type for backend
    });
    
    // Transform backend response to match frontend interface
    return {
      success: response.data.success,
      user: response.data.user,
      token: response.data.access_token, // Backend uses access_token, frontend expects token
      message: response.data.message,
    };
  },

  // Verify token
  verifyToken: async (token: string): Promise<{ valid: boolean; user: User }> => {
    const response = await API.get(`/auth/verify?token=${token}`);
    return response.data;
  },
};

// Emergency API with eRaktkosh Integration
export const emergencyAPI = {
  // Send SOS Alert with eRaktkosh real-time data
  sendSOS: async (data: SOSAlert): Promise<EmergencySOSResponse> => {
    const response = await API.post('/emergency/sos-alert', data);
    return response.data;
  },

  // Get SOS status with real-time updates
  getSOSStatus: async (sosId: string): Promise<{
    sos_id: string;
    status: string;
    created_at: string;
    last_updated: string;
    patient_details: any;
    eraktkosh_data: ERaktkoshData;
    response_count: number;
  }> => {
    const response = await API.get(`/emergency/sos-status/${sosId}`);
    return response.data;
  },

  // Respond to SOS (for donors)
  respondToSOS: async (sosId: string, responseData: {
    availability: 'AVAILABLE' | 'NOT_AVAILABLE';
    message?: string;
  }): Promise<{
    message: string;
    sos_id: string;
    total_responses: number;
  }> => {
    const response = await API.post(`/emergency/sos-respond/${sosId}`, responseData);
    return response.data;
  },

  // Get real-time blood availability from eRaktkosh
  getBloodAvailability: async (params: {
    state: string;
    district: string;
    blood_group: string;
  }): Promise<{
    blood_availability: any;
    blood_centers: any[];
    search_params: any;
    timestamp: string;
  }> => {
    const response = await API.get('/emergency/blood-availability', { params });
    return response.data;
  },

  // Get upcoming donation camps from eRaktkosh
  getDonationCamps: async (params: {
    state: string;
    district: string;
  }): Promise<{
    camps: any[];
    total_camps: number;
    location: string;
    timestamp: string;
  }> => {
    const response = await API.get('/emergency/donation-camps', { params });
    return response.data;
  },

  // Legacy methods for backward compatibility
  respondToEmergency: async (data: {
    alertId: string;
    response: 'accept' | 'decline';
  }): Promise<{ success: boolean; message: string }> => {
    const response = await API.post('/emergency/respond', data);
    return response.data;
  },

  getEmergencyAlerts: async (): Promise<{ success: boolean; alerts: EmergencyAlert[] }> => {
    const response = await API.get('/emergency/alerts');
    return response.data;
  },
};

// Health API
export const healthAPI = {
  // Update health vitals
  updateVitals: async (vitals: HealthVitals): Promise<HealthResponse> => {
    const response = await API.post('/health/vitals', vitals);
    return response.data;
  },

  // Get health score
  getHealthScore: async (userId: string): Promise<{
    healthScore: number;
    vitals: HealthVitals;
    lastUpdated: string;
  }> => {
    const response = await API.get(`/health/score/${userId}`);
    return response.data;
  },

  // Check donation eligibility
  checkDonationEligibility: async (donorId: string): Promise<{
    isEligible: boolean;
    lastDonation: string;
    nextEligibleDate: string;
    totalDonations: number;
    healthScore: number;
    restrictions: string[];
  }> => {
    const response = await API.get(`/health/donation-eligibility/${donorId}`);
    return response.data;
  },
};

// AI Chat API
export const aiAPI = {
  // Chat with AI
  chat: async (data: ChatRequest): Promise<ChatResponse> => {
    const response = await API.post('/ai/chat', data);
    return response.data;
  },

  // Voice response
  getVoiceResponse: async (data: ChatRequest): Promise<{
    success: boolean;
    text: string;
    language: string;
    suggestions: string[];
  }> => {
    const response = await API.post('/ai/voice-response', data);
    return response.data;
  },

  // Health assistant
  healthAssistant: async (data: ChatRequest): Promise<{
    response: string;
    type: string;
    language: string;
    disclaimer: string;
  }> => {
    const response = await API.post('/ai/health-assistant', data);
    return response.data;
  },
};

// Donations API
export const donationsAPI = {
  // Get donation history
  getHistory: async (userId: string): Promise<DonationHistory[]> => {
    const response = await API.get(`/donations/history/${userId}`);
    return response.data;
  },

  // Get scheduled donations (for donors)
  getScheduled: async (donorId: string): Promise<ScheduledDonation[]> => {
    const response = await API.get(`/donations/scheduled/${donorId}`);
    return response.data;
  },

  // Respond to donation request
  respondToRequest: async (data: {
    donationId: string;
    response: 'accept' | 'decline';
  }): Promise<{ success: boolean; message: string; donationStatus: string }> => {
    const response = await API.post('/donations/respond', data);
    return response.data;
  },

  // Request donation (from patient to donor)
  requestDonation: async (data: {
    donorId: string;
    hospitalName: string;
    scheduledDate: string;
    bloodType: string;
    units: number;
    urgency: string;
  }): Promise<{ success: boolean; message: string; donationId: string }> => {
    const response = await API.post('/donations/request', data);
    return response.data;
  },

  // Get donation stats
  getStats: async (userId: string): Promise<{
    totalDonations: number;
    pendingRequests: number;
    livesImpacted: number;
    nextEligibleDate: string;
  }> => {
    const response = await API.get(`/donations/stats/${userId}`);
    return response.data;
  },
};

// AI Chat API
export const chatAPI = {
  // Send message to AI assistant
  sendMessage: async (data: ChatRequest): Promise<ChatResponse> => {
    const response = await API.post('/ai/chat', data);
    return response.data;
  },

  // Check AI service health
  healthCheck: async (): Promise<{ status: string; message: string }> => {
    const response = await API.get('/ai/health-check');
    return response.data;
  },
};

// Health check
export const healthCheck = async (): Promise<{ status: string; service: string; version: string }> => {
  const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL?.replace('/api/v1', '') || 'http://localhost:8001'}/health`);
  return response.data;
};

export default API;