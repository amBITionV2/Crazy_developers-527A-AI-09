import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Star, MapPin, Phone, Clock, Droplets, Users, Zap, Award } from 'lucide-react';

interface MockDonor {
  id: string;
  name: string;
  bloodType: string;
  distance: number;
  rating: number;
  totalDonations: number;
  lastDonation: string;
  phone: string;
  location: string;
  availability: string;
  plateletCompatibility: number;
  responseTime: string;
  reliability: number;
  specialization: string[];
}

interface MockDonorResponseProps {
  requiredBloodType: string;
  requiredComponent: string;
  onContactDonor: (donorId: string) => void;
}

const MockDonorResponse: React.FC<MockDonorResponseProps> = ({ 
  requiredBloodType, 
  requiredComponent, 
  onContactDonor 
}) => {
  const mockDonors: MockDonor[] = [
    {
      id: "DNR-001",
      name: "Raj Kumar",
      bloodType: "B+",
      distance: 2.3,
      rating: 4.9,
      totalDonations: 47,
      lastDonation: "15 days ago",
      phone: "+91-9876543212",
      location: "Gandhi Nagar, Bangalore",
      availability: "Available Now",
      plateletCompatibility: 96,
      responseTime: "< 5 min",
      reliability: 98,
      specialization: ["Single Donor Platelet", "Regular Donor", "Emergency Response"]
    },
    {
      id: "DNR-002", 
      name: "Priya Sharma",
      bloodType: "B+",
      distance: 4.1,
      rating: 4.7,
      totalDonations: 32,
      lastDonation: "8 days ago",
      phone: "+91-9876543213",
      location: "Koramangala, Bangalore",
      availability: "Available in 2 hours",
      plateletCompatibility: 89,
      responseTime: "< 10 min",
      reliability: 94,
      specialization: ["Single Donor Platelet", "Apheresis Specialist"]
    }
  ];

  const renderDonorCard = (donor: MockDonor, rank: number) => (
    <Card key={donor.id} className={`shadow-lg ${rank === 1 ? 'border-destructive border-2 ring-2 ring-destructive/20' : 'border-destructive/30'}`}>
      <CardHeader className={`${rank === 1 ? 'bg-gradient-to-r from-destructive/10 to-destructive/5' : 'bg-gradient-to-r from-gray-50 to-gray-25'} rounded-t-lg`}>
        <div className="flex items-center justify-between">
          <CardTitle className={`flex items-center gap-2 ${rank === 1 ? 'text-destructive' : 'text-gray-900'}`}>
            <Users className="h-5 w-5" />
            {donor.name}
            {rank === 1 && (
              <Badge className="bg-destructive/20 text-destructive border-destructive/30">
                <Award className="h-3 w-3 mr-1" />
                Best Match
              </Badge>
            )}
          </CardTitle>
          <div className="flex items-center gap-1">
            <Star className="h-4 w-4 text-yellow-500 fill-current" />
            <span className="font-semibold text-gray-700">{donor.rating}</span>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="pt-6">
        <div className="space-y-4">
          {/* Key Metrics */}
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center gap-2">
              <Droplets className="h-4 w-4 text-red-500" />
              <span className="font-medium">{donor.bloodType}</span>
              <Badge variant="outline" className="text-xs">
                Perfect Match
              </Badge>
            </div>
            <div className="flex items-center gap-2">
              <MapPin className="h-4 w-4 text-blue-500" />
              <span className="text-sm text-gray-600">{donor.distance} km away</span>
            </div>
          </div>

          {/* Platelet Compatibility */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="font-medium">Single Donor Platelet Compatibility</span>
              <span className="font-bold text-green-600">{donor.plateletCompatibility}%</span>
            </div>
            <Progress value={donor.plateletCompatibility} className="h-2" />
          </div>

          {/* Reliability Score */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="font-medium">Reliability Score</span>
              <span className="font-bold text-blue-600">{donor.reliability}%</span>
            </div>
            <Progress value={donor.reliability} className="h-2" />
          </div>

          {/* Donor Stats */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="p-2 bg-gray-50 rounded">
              <p className="text-gray-600">Total Donations</p>
              <p className="font-bold text-gray-900">{donor.totalDonations}</p>
            </div>
            <div className="p-2 bg-gray-50 rounded">
              <p className="text-gray-600">Last Donation</p>
              <p className="font-bold text-gray-900">{donor.lastDonation}</p>
            </div>
          </div>

          {/* Availability & Response */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-green-500" />
              <span className="text-sm font-medium text-green-700">{donor.availability}</span>
            </div>
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-orange-500" />
              <span className="text-sm text-gray-600">Response Time: {donor.responseTime}</span>
            </div>
          </div>

          {/* Specializations */}
          <div className="space-y-2">
            <p className="text-sm font-medium text-gray-700">Specializations:</p>
            <div className="flex flex-wrap gap-1">
              {donor.specialization.map((spec, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {spec}
                </Badge>
              ))}
            </div>
          </div>

          {/* Location */}
          <div className="p-2 bg-blue-50 rounded">
            <p className="text-sm text-blue-700">{donor.location}</p>
          </div>

          {/* Action Button */}
          <Button 
            onClick={() => onContactDonor(donor.id)}
            className={`w-full ${rank === 1 
              ? 'bg-gradient-to-r from-destructive to-destructive/80 hover:from-destructive/90 hover:to-destructive/70' 
              : 'bg-gradient-to-r from-gray-600 to-gray-700 hover:from-gray-700 hover:to-gray-800'
            } text-white`}
          >
            <Phone className="h-4 w-4 mr-2" />
            Contact Donor - {donor.phone}
          </Button>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-6">
      {/* AI Assistant Prompt */}
      <Card className="border-destructive/30 shadow-lg bg-gradient-to-r from-destructive/10 to-destructive/5">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <div className="bg-destructive/20 p-2 rounded-full">
              <Zap className="h-5 w-5 text-destructive" />
            </div>
            <div className="space-y-2">
              <h4 className="font-semibold text-destructive">AI Blood Match Assistant</h4>
              <p className="text-sm text-destructive/80">
                🎯 <strong>Perfect Match Found!</strong> Based on your requirement for <strong>{requiredComponent}</strong> with blood type <strong>{requiredBloodType}</strong>, 
                I've identified 2 highly compatible donors within 5km radius.
              </p>
              <p className="text-sm text-destructive/70">
                💡 <strong>Recommendation:</strong> Raj Kumar has the highest platelet compatibility (96%) and is closest (2.3km). 
                He's specialized in Single Donor Platelet donations with excellent reliability.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Search Results Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-destructive">Available Donors</h3>
        <Badge className="bg-destructive/20 text-destructive border-destructive/30">
          2 Matches Found
        </Badge>
      </div>

      {/* Donor Cards */}
      <div className="space-y-4">
        {mockDonors.map((donor, index) => renderDonorCard(donor, index + 1))}
      </div>

      {/* Summary Stats */}
      <Card className="border-destructive/20 shadow-lg">
        <CardContent className="pt-6">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="space-y-1">
              <p className="text-2xl font-bold text-destructive">96%</p>
              <p className="text-sm text-gray-600">Best Compatibility</p>
            </div>
            <div className="space-y-1">
              <p className="text-2xl font-bold text-destructive">2.3km</p>
              <p className="text-sm text-gray-600">Nearest Donor</p>
            </div>
            <div className="space-y-1">
              <p className="text-2xl font-bold text-destructive">&lt; 5min</p>
              <p className="text-sm text-gray-600">Fastest Response</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default MockDonorResponse;