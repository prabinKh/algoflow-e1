import { useState, useRef } from "react";
import { Link, useNavigate, useOutletContext } from "react-router-dom";
import {
  Plus,
  Search,
  Edit2,
  Trash2,
  RotateCcw,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { motion } from "motion/react";
import { toast } from "sonner";
import { useGSAPReveal } from "@/hooks/useGSAP";
import { useStaff } from "@/hooks/useStaff";

const Roles = () => {
  const { setIsSidebarOpen } = useOutletContext<{ setIsSidebarOpen: (open: boolean) => void }>();
  const containerRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState("");
  const [entriesPerPage, setEntriesPerPage] = useState(10);
  
  const { roles, loading, deleteRole } = useStaff();

  useGSAPReveal(containerRef, ".gsap-reveal", { opacity: 0, y: 20, duration: 0.6, stagger: 0.05 });

  const filteredRoles = roles.filter(role => 
    role.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    (role.permissions && Array.isArray(role.permissions) && role.permissions.some(p => p.toLowerCase().includes(searchTerm.toLowerCase())))
  );

  const handleAddRole = () => {
    toast.info("Role creation modal would open here.");
  };

  const handleEditRole = (role: any) => {
    toast.info(`Editing ${role.name}`);
  };

  const handleDeleteRole = (role: any) => {
    if (confirm(`Are you sure you want to delete the role "${role.name}"?`)) {
      deleteRole.mutate(role.id);
    }
  };

  const handleBulkDelete = () => {
    toast.error("Bulk delete initiated");
  };

  const handleReset = () => {
    toast.info("Resetting filters");
    setSearchTerm("");
    setEntriesPerPage(10);
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
              <h1 className="text-2xl font-bold text-foreground">Roles</h1>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Link to="/admin" className="hover:text-emerald-500 transition-colors">Home</Link>
                <ChevronRight size={14} />
                <span>Roles</span>
              </div>
            </div>

            {/* Actions Bar */}
            <div className="bg-card rounded-2xl p-4 border border-border shadow-sm mb-6 flex flex-wrap items-center justify-between gap-4 gsap-reveal">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <select 
                    value={entriesPerPage}
                    onChange={(e) => setEntriesPerPage(Number(e.target.value))}
                    className="bg-muted border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
                  >
                    <option value={10}>10</option>
                    <option value={25}>25</option>
                    <option value={50}>50</option>
                  </select>
                  <span className="text-sm text-muted-foreground">Entries Per Page</span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button 
                  onClick={handleBulkDelete}
                  className="p-2 text-rose-500 hover:bg-rose-50 rounded-lg transition-colors border border-rose-100"
                >
                  <Trash2 size={18} />
                </button>
                <button 
                  onClick={handleReset}
                  className="p-2 text-blue-500 hover:bg-blue-50 rounded-lg transition-colors border border-blue-100"
                >
                  <RotateCcw size={18} />
                </button>
                <button 
                  onClick={() => toast.info("Refreshing data...")}
                  className="p-2 text-amber-500 hover:bg-amber-50 rounded-lg transition-colors border border-amber-100"
                >
                  <RotateCcw size={18} />
                </button>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={16} />
                  <input 
                    type="text"
                    placeholder="Search..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 pr-4 py-2 bg-muted border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 w-64"
                  />
                </div>
                <button 
                  onClick={handleAddRole}
                  className="bg-emerald-500 text-white p-2 rounded-lg hover:bg-emerald-600 transition-all shadow-lg shadow-emerald-500/20"
                >
                  <Plus size={18} />
                </button>
              </div>
            </div>

            {/* Table */}
            <div className="bg-card rounded-2xl border border-border shadow-sm overflow-hidden gsap-reveal">
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-muted/50 border-bottom border-border">
                      <th className="p-4 w-12">
                        <input type="checkbox" className="rounded border-border text-emerald-500 focus:ring-emerald-500" />
                      </th>
                      <th className="p-4 text-xs font-bold text-foreground uppercase tracking-wider">Role</th>
                      <th className="p-4 text-xs font-bold text-foreground uppercase tracking-wider">Permissions</th>
                      <th className="p-4 text-xs font-bold text-foreground uppercase tracking-wider text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {filteredRoles.map((role) => (
                      <tr key={role.id} className="hover:bg-muted/50 transition-colors">
                        <td className="p-4">
                          <input type="checkbox" className="rounded border-border text-emerald-500 focus:ring-emerald-500" />
                        </td>
                        <td className="p-4">
                          <span className="text-sm font-medium text-foreground">{role.name}</span>
                        </td>
                        <td className="p-4">
                          <div className="flex flex-wrap gap-2 max-w-3xl">
                            {role.permissions.map((perm, idx) => (
                              <span 
                                key={idx}
                                className="px-3 py-1 bg-emerald-500 text-white text-[10px] font-medium rounded-md"
                              >
                                {perm}
                              </span>
                            ))}
                            <button 
                              onClick={() => toast.info(`Showing all permissions for ${role.name}`)}
                              className="text-blue-500 text-[10px] font-bold hover:underline"
                            >
                              Show More
                            </button>
                          </div>
                        </td>
                        <td className="p-4">
                          <div className="flex items-center justify-end gap-2">
                            <button 
                              onClick={() => handleEditRole(role)}
                              className="p-2 text-blue-500 hover:bg-blue-50 rounded-lg transition-colors border border-blue-100"
                            >
                              <Edit2 size={16} />
                            </button>
                            <button 
                              onClick={() => handleDeleteRole(role)}
                              className="p-2 text-rose-500 hover:bg-rose-50 rounded-lg transition-colors border border-rose-100"
                            >
                              <Trash2 size={16} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              <div className="p-4 border-t border-border flex items-center justify-between">
                <p className="text-sm text-muted-foreground">Showing 1 to 3 of 3 entries</p>
                <div className="flex items-center gap-2">
                  <button className="p-2 text-muted-foreground hover:bg-accent rounded-lg transition-colors border border-border">
                    <ChevronLeft size={16} />
                  </button>
                  <button className="w-8 h-8 bg-emerald-500 text-white rounded-lg text-sm font-medium shadow-lg shadow-emerald-500/20">1</button>
                  <button className="p-2 text-muted-foreground hover:bg-accent rounded-lg transition-colors border border-border">
                    <ChevronRight size={16} />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
  );
};

export default Roles;
