import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { LanguageProvider } from "@/contexts/LanguageContext";
import { Landing } from "./pages/Landing";
import { SelectUser } from "./pages/SelectUser";
import { DonorRegister } from "./pages/donor/DonorRegister";
import { DonorDashboard } from "./pages/donor/DonorDashboard";
import { PatientRegister } from "./pages/patient/PatientRegister";
import { PatientDashboard } from "./pages/patient/PatientDashboard";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <LanguageProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/select-user" element={<SelectUser />} />
            <Route path="/donor/register" element={<DonorRegister />} />
            <Route path="/donor/dashboard" element={<DonorDashboard />} />
            <Route path="/patient/register" element={<PatientRegister />} />
            <Route path="/patient/dashboard" element={<PatientDashboard />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </LanguageProvider>
  </QueryClientProvider>
);

export default App;
