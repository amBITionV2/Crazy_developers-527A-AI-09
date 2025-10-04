import { useState } from 'react';
import { Heart, Activity, History, Calendar, AlertCircle, MessageCircle, Users, LogOut } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { BloodCells } from '@/components/BloodCells';
import { LanguageSelector } from '@/components/LanguageSelector';
import { VoiceAssistant } from '@/components/VoiceAssistant';
import { useLanguage } from '@/contexts/LanguageContext';
import { useNavigate } from 'react-router-dom';

export const DonorDashboard = () => {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('health');
  const [scheduledRequests, setScheduledRequests] = useState([
    { patient: 'Thalassemia Patient', hospital: 'Children\'s Hospital', date: '2024-11-05', status: 'pending' },
    { patient: 'Dialysis Patient', hospital: 'Kidney Care Center', date: '2024-11-12', status: 'pending' },
  ]);

  const healthScore = 85;

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      <BloodCells />
      
      {/* Header */}
      <header className="relative z-10 bg-card/30 backdrop-blur-sm border-b border-primary/20">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-primary/50 flex items-center justify-center">
              <Heart className="w-5 h-5 text-white fill-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-primary">{t('appName')}</h1>
              <p className="text-sm text-muted-foreground">{t('donor')} {t('dashboard')}</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <LanguageSelector />
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => navigate('/')}
              className="border-primary/20 hover:bg-primary/10"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Dashboard Content */}
      <div className="relative z-10 container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="bg-card/50 backdrop-blur-sm border border-primary/20 p-1 grid grid-cols-3 lg:grid-cols-6 gap-2">
            <TabsTrigger value="health" className="data-[state=active]:bg-primary data-[state=active]:text-white">
              <Activity className="w-4 h-4 mr-2" />
              {t('healthStatus')}
            </TabsTrigger>
            <TabsTrigger value="history" className="data-[state=active]:bg-primary data-[state=active]:text-white">
              <History className="w-4 h-4 mr-2" />
              {t('history')}
            </TabsTrigger>
            <TabsTrigger value="schedule" className="data-[state=active]:bg-primary data-[state=active]:text-white">
              <Calendar className="w-4 h-4 mr-2" />
              {t('schedule')}
            </TabsTrigger>
            <TabsTrigger value="emergency" className="data-[state=active]:bg-primary data-[state=active]:text-white">
              <AlertCircle className="w-4 h-4 mr-2" />
              {t('emergency')}
            </TabsTrigger>
            <TabsTrigger value="chat" className="data-[state=active]:bg-primary data-[state=active]:text-white">
              <MessageCircle className="w-4 h-4 mr-2" />
              AI Chat
            </TabsTrigger>
            <TabsTrigger value="community" className="data-[state=active]:bg-primary data-[state=active]:text-white">
              <Users className="w-4 h-4 mr-2" />
              {t('community')}
            </TabsTrigger>
          </TabsList>

          {/* Health Status Tab */}
          <TabsContent value="health" className="space-y-6 animate-fade-in">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="bg-card/50 backdrop-blur-sm border-primary/20">
                <CardHeader>
                  <CardTitle>Health Score</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-center">
                    <div className="text-5xl font-bold text-primary mb-2">{healthScore}%</div>
                    <Progress value={healthScore} className="h-3" />
                  </div>
                  <div className="grid grid-cols-2 gap-4 mt-6">
                    <div className="text-center p-4 bg-background/50 rounded-lg">
                      <div className="text-2xl font-bold text-primary">120/80</div>
                      <div className="text-sm text-muted-foreground">Blood Pressure</div>
                      <Badge className="mt-2 bg-primary">Normal</Badge>
                    </div>
                    <div className="text-center p-4 bg-background/50 rounded-lg">
                      <div className="text-2xl font-bold text-primary">14.5</div>
                      <div className="text-sm text-muted-foreground">Hemoglobin (g/dL)</div>
                      <Badge className="mt-2 bg-primary">Normal</Badge>
                    </div>
                    <div className="text-center p-4 bg-background/50 rounded-lg">
                      <div className="text-2xl font-bold text-primary">95</div>
                      <div className="text-sm text-muted-foreground">Sugar (mg/dL)</div>
                      <Badge className="mt-2 bg-primary">Normal</Badge>
                    </div>
                    <div className="text-center p-4 bg-background/50 rounded-lg">
                      <div className="text-2xl font-bold text-primary">72</div>
                      <div className="text-sm text-muted-foreground">Heart Rate (bpm)</div>
                      <Badge className="mt-2 bg-primary">Normal</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-card/50 backdrop-blur-sm border-primary/20">
                <CardHeader>
                  <CardTitle>Donation Eligibility</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-primary/10 rounded-lg">
                    <span>Status</span>
                    <Badge className="bg-primary">Eligible</Badge>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Last Donation</span>
                      <span>45 days ago</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Next Eligible</span>
                      <span>Now</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Total Donations</span>
                      <span className="font-semibold">12</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* History Tab */}
          <TabsContent value="history" className="animate-fade-in">
            <Card className="bg-card/50 backdrop-blur-sm border-primary/20">
              <CardHeader>
                <CardTitle>Donation History</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { patient: 'John Doe', hospital: 'City Hospital', bloodGroup: 'O+', date: '2024-08-15' },
                    { patient: 'Jane Smith', hospital: 'General Hospital', bloodGroup: 'O+', date: '2024-06-20' },
                    { patient: 'Robert Johnson', hospital: 'Medical Center', bloodGroup: 'O+', date: '2024-04-10' },
                  ].map((donation, index) => (
                    <div key={index} className="p-4 bg-background/50 rounded-lg border border-primary/10">
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="font-semibold">{donation.patient}</h4>
                          <p className="text-sm text-muted-foreground">{donation.hospital}</p>
                        </div>
                        <Badge variant="outline" className="border-primary text-primary">{donation.bloodGroup}</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mt-2">{donation.date}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Schedule Tab */}
          <TabsContent value="schedule" className="animate-fade-in">
            <Card className="bg-card/50 backdrop-blur-sm border-primary/20">
              <CardHeader>
                <CardTitle>Upcoming Donations</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {scheduledRequests.length === 0 ? (
                    <p className="text-center text-muted-foreground py-8">No scheduled donations</p>
                  ) : (
                    scheduledRequests.map((schedule, index) => (
                      <div key={index} className="p-4 bg-background/50 rounded-lg border border-primary/10">
                        <div className="flex justify-between items-start mb-3">
                          <div>
                            <h4 className="font-semibold">{schedule.patient}</h4>
                            <p className="text-sm text-muted-foreground">{schedule.hospital}</p>
                          </div>
                          <Badge variant="outline">{schedule.date}</Badge>
                        </div>
                        {schedule.status === 'pending' && (
                          <div className="flex gap-2">
                            <Button 
                              size="sm" 
                              className="bg-primary hover:bg-primary/90"
                              onClick={() => {
                                const updated = [...scheduledRequests];
                                updated[index].status = 'accepted';
                                setScheduledRequests(updated);
                              }}
                            >
                              Accept
                            </Button>
                            <Button 
                              size="sm" 
                              variant="outline" 
                              className="border-primary/20"
                              onClick={() => {
                                setScheduledRequests(scheduledRequests.filter((_, i) => i !== index));
                              }}
                            >
                              Decline
                            </Button>
                          </div>
                        )}
                        {schedule.status === 'accepted' && (
                          <Badge className="bg-primary">Accepted</Badge>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Emergency Tab */}
          <TabsContent value="emergency" className="animate-fade-in">
            <Card className="bg-card/50 backdrop-blur-sm border-primary/20">
              <CardHeader>
                <CardTitle className="text-destructive">Emergency Requests</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { patient: 'Emergency Case #1', hospital: 'Trauma Center', bloodGroup: 'O+', distance: '2.3 km', urgency: 'Critical', area: 'Jayanagar' },
                    { patient: 'Emergency Case #2', hospital: 'City Hospital', bloodGroup: 'O+', distance: '4.1 km', urgency: 'High', area: 'Koramangala' },
                  ].map((emergency, index) => (
                    <div key={index} className="p-4 bg-destructive/10 rounded-lg border border-destructive/20 animate-pulse-glow">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h4 className="font-semibold text-destructive">{emergency.patient}</h4>
                          <p className="text-sm text-muted-foreground">{emergency.hospital}</p>
                          <p className="text-sm mt-1">📍 {emergency.area} • {emergency.distance}</p>
                        </div>
                        <div className="text-right">
                          <Badge className="bg-destructive mb-2">{emergency.bloodGroup}</Badge>
                          <Badge variant="outline" className="block">{emergency.urgency}</Badge>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button 
                          size="sm" 
                          className="bg-destructive hover:bg-destructive/90"
                          onClick={() => {
                            setScheduledRequests([...scheduledRequests, {
                              patient: emergency.patient,
                              hospital: emergency.hospital,
                              date: new Date().toISOString().split('T')[0],
                              status: 'accepted'
                            }]);
                          }}
                        >
                          Accept
                        </Button>
                        <Button size="sm" variant="outline" className="border-destructive/20">Decline</Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* AI Chat Tab */}
          <TabsContent value="chat" className="animate-fade-in">
            <Card className="bg-card/50 backdrop-blur-sm border-primary/20">
              <CardHeader>
                <CardTitle>AI Health Assistant</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-96 flex flex-col justify-center items-center text-center space-y-4">
                  <MessageCircle className="w-16 h-16 text-primary/50" />
                  <p className="text-muted-foreground">Ask me anything about blood donation, health, or eligibility!</p>
                  <p className="text-sm text-muted-foreground">AI chatbot will be integrated with backend</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Community Tab */}
          <TabsContent value="community" className="animate-fade-in">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="bg-card/50 backdrop-blur-sm border-primary/20">
                <CardHeader>
                  <CardTitle>Leaderboard</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {[
                      { name: 'Rajesh Kumar', donations: 25, rank: 1 },
                      { name: 'Priya Sharma', donations: 22, rank: 2 },
                      { name: 'You', donations: 12, rank: 5 },
                    ].map((donor) => (
                      <div key={donor.rank} className="flex items-center justify-between p-3 bg-background/50 rounded-lg">
                        <div className="flex items-center gap-3">
                          <Badge className="bg-primary">{donor.rank}</Badge>
                          <span className={donor.name === 'You' ? 'font-bold text-primary' : ''}>{donor.name}</span>
                        </div>
                        <span className="text-sm text-muted-foreground">{donor.donations} donations</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-card/50 backdrop-blur-sm border-primary/20">
                <CardHeader>
                  <CardTitle>Nearby Donors</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {[
                      { name: 'Amit Patel', distance: '1.2 km', bloodGroup: 'O+' },
                      { name: 'Sneha Reddy', distance: '2.5 km', bloodGroup: 'O+' },
                      { name: 'Karthik Rao', distance: '3.8 km', bloodGroup: 'O+' },
                    ].map((donor, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-background/50 rounded-lg">
                        <div>
                          <div className="font-semibold">{donor.name}</div>
                          <div className="text-sm text-muted-foreground">{donor.distance}</div>
                        </div>
                        <Badge variant="outline" className="border-primary text-primary">{donor.bloodGroup}</Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
      
      <VoiceAssistant />
    </div>
  );
};
