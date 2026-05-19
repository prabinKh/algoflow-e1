import { useRef, useState } from "react";
import { useGSAPReveal } from "@/hooks/useGSAP";
import { Header } from "@/frontend/components/Header";
import { Footer } from "@/frontend/components/Footer";
import { Mail, Lock, LogIn } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { authService } from "@/api/authService";
import { useAuth } from "@/context/AuthContext";
import { toast } from "sonner";

const SignInPage = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const { login } = useAuth();
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState("admin@gmail.com");
  const [password, setPassword] = useState("admin");
  useGSAPReveal(containerRef, ".gsap-reveal", { opacity: 0, y: 30, duration: 0.8, stagger: 0.1 });

  const handleGoogleSignIn = async () => {
    toast.error("Google sign in is currently disabled.");
  };

  const handleEmailSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await authService.login(email, password);
      login(data);
      toast.success(data.message || "Successfully signed in!");
      if (data.user?.is_staff || data.user?.is_superuser) {
        navigate("/admin");
      } else {
        navigate("/");
      }
    } catch (error: any) {
      toast.error(error.message || "Failed to sign in. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background" ref={containerRef}>
      <Header />
      <main className="neo-container py-10 sm:py-16 flex justify-center">
        <div className="w-full max-w-sm space-y-8">
          <div className="text-center gsap-reveal">
            <div className="text-3xl font-display font-bold tracking-tighter text-primary mb-2">neo</div>
            <h1 className="text-xl sm:text-2xl font-display font-bold">Welcome Back</h1>
            <p className="text-xs sm:text-sm text-muted-foreground mt-2">Sign in to your NeoStore account</p>
          </div>

          <div className="bg-card border border-border rounded-xl p-6 shadow-[var(--shadow-md)] gsap-reveal">
            <div className="space-y-4">
              <button 
                onClick={handleGoogleSignIn}
                type="button"
                disabled={loading}
                className="w-full flex items-center justify-center gap-3 bg-white text-black border border-border rounded-lg py-2.5 text-sm font-medium hover:bg-gray-50 transition-all disabled:opacity-50"
              >
                <img src="https://www.google.com/favicon.ico" alt="Google" className="w-4 h-4" />
                Continue with Google
              </button>

              <div className="relative py-2">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t border-border"></span>
                </div>
                <div className="relative flex justify-center text-[10px] uppercase tracking-widest font-bold">
                  <span className="bg-card px-2 text-muted-foreground">Or continue with email</span>
                </div>
              </div>

              <form className="space-y-4" onSubmit={handleEmailSignIn}>
              <div>
                <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1.5 block">Email</label>
                <div className="relative">
                  <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@email.com"
                    className="w-full h-10 pl-10 pr-4 bg-accent border border-border rounded-lg text-sm
                             placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                  />
                </div>
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1.5 block">Password</label>
                <div className="relative">
                  <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full h-10 pl-10 pr-4 bg-accent border border-border rounded-lg text-sm
                             placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                  />
                </div>
              </div>
              <button type="submit" className="btn-primary w-full justify-center py-2.5">
                Sign In
              </button>
            </form>
          </div>
        </div>

          <p className="text-center text-xs sm:text-sm text-muted-foreground gsap-reveal">
            Don't have an account?{" "}
            <Link to="/signup" className="text-primary hover:underline font-medium">Sign Up</Link>
          </p>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default SignInPage;
