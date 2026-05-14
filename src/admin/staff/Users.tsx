import { useState, useEffect, useRef } from "react";
import { Link, useNavigate, useOutletContext } from "react-router-dom";
import { 
  MoreVertical, 
  Plus, 
  User as UserIcon,
  LayoutGrid,
  List,
  Search,
  ChevronRight,
  Menu
} from "lucide-react";
import { motion } from "motion/react";
import { toast } from "sonner";
import { useStaff } from "@/hooks/useStaff";
import { useGSAPReveal } from "@/hooks/useGSAP";

const Users = () => {
  const { setIsSidebarOpen } = useOutletContext<{ setIsSidebarOpen: (open: boolean) => void }>();
  const containerRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [searchTerm, setSearchTerm] = useState("");
  
  const { members, loading, deleteMember } = useStaff();

  useGSAPReveal(containerRef, ".gsap-reveal", { opacity: 0, y: 20, duration: 0.6, stagger: 0.05 });

  const filteredUsers = members.filter(member => {
    const name = member.user_details?.name || "Unknown";
    const email = member.user_details?.email || "";
    const roleName = member.role_details?.name || "";
    return (
      name.toLowerCase().includes(searchTerm.toLowerCase()) || 
      email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      roleName.toLowerCase().includes(searchTerm.toLowerCase())
    );
  });

  const handleAddUser = () => {
    toast.info("User creation modal would open here.");
  };

  const handleEditUser = (member: any) => {
    toast.info(`Editing ${member.user_details?.name}`);
  };

  const handleDeleteUser = (member: any) => {
    if (confirm(`Are you sure you want to remove ${member.user_details?.name}?`)) {
      deleteMember.mutate(member.id);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"></div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col min-w-0 min-h-screen pb-20 lg:pb-0" ref={containerRef}>
        <main className="flex-1 p-4 md:p-8">
          <div className="max-w-[1600px] mx-auto">
            {/* Header */}
            <div className="flex flex-col gap-1 mb-8 gsap-reveal">
              <h1 className="text-2xl font-bold text-foreground">Users</h1>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Link to="/admin" className="hover:text-emerald-500 transition-colors">Home</Link>
                <ChevronRight size={14} />
                <span>Users</span>
              </div>
            </div>

            {/* Actions */}
            <div className="flex flex-col md:flex-row items-center justify-between gap-4 mb-6 gsap-reveal">
              <div className="flex items-center gap-4 w-full md:w-auto">
                <div className="flex items-center gap-2">
                  <button 
                    onClick={() => setViewMode("list")}
                    className={`p-2 rounded-lg transition-all ${viewMode === "list" ? "bg-emerald-500 text-white shadow-lg shadow-emerald-500/20" : "bg-card text-muted-foreground hover:text-foreground border border-border"}`}
                  >
                    <List size={18} />
                  </button>
                  <button 
                    onClick={() => setViewMode("grid")}
                    className={`p-2 rounded-lg transition-all ${viewMode === "grid" ? "bg-emerald-500 text-white shadow-lg shadow-emerald-500/20" : "bg-card text-muted-foreground hover:text-foreground border border-border"}`}
                  >
                    <LayoutGrid size={18} />
                  </button>
                </div>
                <div className="relative flex-1 md:w-64">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={16} />
                  <input 
                    type="text"
                    placeholder="Search users..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 bg-card border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
                  />
                </div>
              </div>
              <button 
                onClick={handleAddUser}
                className="flex items-center gap-2 bg-emerald-500 text-white px-4 py-2 rounded-lg hover:bg-emerald-600 transition-all shadow-lg shadow-emerald-500/20 w-full md:w-auto justify-center"
              >
                <Plus size={18} />
                <span>Add User</span>
              </button>
            </div>

            {/* Grid View */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 gsap-reveal">
              {filteredUsers.map((user, index) => (
                <motion.div
                  key={user.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="bg-card rounded-2xl p-6 border border-border shadow-sm hover:shadow-md transition-all group relative"
                >
                  <div className="absolute top-4 left-4">
                    <span className="bg-emerald-500 text-white text-[10px] font-bold px-2 py-1 rounded uppercase tracking-wider">
                      {user.role_details?.name || "No Role"}
                    </span>
                  </div>
                  
                  <div className="absolute top-4 right-4 flex items-center gap-1">
                    <button 
                      onClick={() => handleEditUser(user)}
                      className="p-1.5 text-muted-foreground hover:text-emerald-500 transition-colors"
                    >
                      <MoreVertical size={18} />
                    </button>
                  </div>

                  <div className="flex flex-col items-center mt-8">
                    <div className="w-24 h-24 rounded-full bg-blue-50 flex items-center justify-center mb-4 overflow-hidden border-4 border-white shadow-sm">
                      <div className="w-full h-full bg-blue-100 flex items-center justify-center text-blue-600">
                        <UserIcon size={40} />
                      </div>
                    </div>
                    <h3 className="text-lg font-bold text-foreground mb-1 group-hover:text-emerald-500 transition-colors">
                      {user.user_details?.name || "Unknown"}
                    </h3>
                    <p className="text-sm text-muted-foreground">{user.user_details?.email}</p>
                  </div>
                </motion.div>
              ))}

              {/* Create New User Card */}
              <motion.button
                onClick={handleAddUser}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: filteredUsers.length * 0.05 }}
                className="bg-muted/50 rounded-2xl p-6 border-2 border-dashed border-border flex flex-col items-center justify-center gap-4 hover:bg-muted hover:border-emerald-500/50 transition-all group min-h-[280px]"
              >
                <div className="w-12 h-12 rounded-full bg-emerald-500 text-white flex items-center justify-center shadow-lg shadow-emerald-500/20 group-hover:scale-110 transition-transform">
                  <Plus size={24} />
                </div>
                <div className="text-center">
                  <h3 className="text-lg font-bold text-foreground mb-1">Create New User</h3>
                  <p className="text-sm text-muted-foreground">Click here to Create New User</p>
                </div>
              </motion.button>
            </div>
          </div>
        </main>
      </div>
  );
};

export default Users;
