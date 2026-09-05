"use client";

import { useState, useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { ArrowLeft, CheckCircle, Clock, AlertTriangle, BookOpen } from "lucide-react";

const NODE_WIDTH = 220;
const NODE_HEIGHT = 80;
const LEVEL_HEIGHT = 150;

export default function ProgressPage() {
  const router = useRouter();
  const [masteryMap, setMasteryMap] = useState<Record<string, string>>({});
  const [graphData, setGraphData] = useState<{ nodes: any[]; edges: any[] }>({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const studentId = localStorage.getItem("ai_tutor_student_id");
    if (!studentId) {
      router.push("/");
      return;
    }

    const fetchData = async () => {
      try {
        const [progressRes, graphRes] = await Promise.all([
          api.getProgress(studentId),
          api.getCurriculumGraph("mathematics")
        ]);

        const mMap: Record<string, string> = {};
        if (progressRes.mastery) {
          progressRes.mastery.forEach((m: any) => {
            mMap[m.concept_id] = m.mastery_state || m.mastery_level || "unknown";
          });
        }
        setMasteryMap(mMap);
        setGraphData(graphRes);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [router]);

  // Layout calculation
  const layout = useMemo(() => {
    if (!graphData.nodes.length) return null;

    // 1. Calculate in-degrees
    const inDegree: Record<string, number> = {};
    const parents: Record<string, string[]> = {};
    const children: Record<string, string[]> = {};
    
    graphData.nodes.forEach(n => {
      inDegree[n.concept_id] = 0;
      parents[n.concept_id] = [];
      children[n.concept_id] = [];
    });

    graphData.edges.forEach(e => {
      if (inDegree[e.target] !== undefined) {
        inDegree[e.target]++;
        parents[e.target].push(e.source);
        if (children[e.source]) children[e.source].push(e.target);
      }
    });

    // 2. Topological sort to find depth
    const depth: Record<string, number> = {};
    const queue: string[] = [];
    
    Object.keys(inDegree).forEach(id => {
      if (inDegree[id] === 0) {
        depth[id] = 0;
        queue.push(id);
      }
    });

    while (queue.length > 0) {
      const u = queue.shift()!;
      children[u]?.forEach(v => {
        depth[v] = Math.max(depth[v] || 0, depth[u] + 1);
        inDegree[v]--;
        if (inDegree[v] === 0) queue.push(v);
      });
    }

    // Assign max depth to nodes with cycles just in case
    graphData.nodes.forEach(n => {
      if (depth[n.concept_id] === undefined) depth[n.concept_id] = 0;
    });

    // 3. Group by levels
    const levels: Record<number, any[]> = {};
    let maxLevel = 0;
    graphData.nodes.forEach(n => {
      const d = depth[n.concept_id];
      if (!levels[d]) levels[d] = [];
      levels[d].push(n);
      if (d > maxLevel) maxLevel = d;
    });

    // 4. Calculate X and Y coordinates
    const maxNodesInLevel = Math.max(...Object.values(levels).map(l => l.length));
    const width = Math.max(800, maxNodesInLevel * (NODE_WIDTH + 40));
    const height = (maxLevel + 1) * LEVEL_HEIGHT;

    const nodeCoords: Record<string, { cx: number, cy: number }> = {};
    
    Object.keys(levels).forEach(dStr => {
      const d = parseInt(dStr);
      const levelNodes = levels[d];
      
      // Sort nodes in a level for better visual crossing reduction (simple heuristic)
      levelNodes.sort((a, b) => a.concept_id.localeCompare(b.concept_id));
      
      levelNodes.forEach((node, i) => {
        const cx = (i + 1) * (width / (levelNodes.length + 1));
        const cy = (d + 0.5) * LEVEL_HEIGHT;
        nodeCoords[node.concept_id] = { cx, cy };
      });
    });

    return { width, height, nodeCoords, nodes: graphData.nodes, edges: graphData.edges };
  }, [graphData]);

  const getStatusColor = (level: string) => {
    switch (level) {
      case "mastered": return "var(--accent-primary)"; // Sage green
      case "practicing": return "#D9A05B"; // Muted gold
      case "struggling": return "#C45B5B"; // Muted rose
      default: return "var(--text-secondary)"; // Gray
    }
  };

  const getStatusIcon = (level: string) => {
    switch (level) {
      case "mastered": return <CheckCircle size={16} color="var(--accent-primary)" />;
      case "practicing": return <Clock size={16} color="#D9A05B" />;
      case "struggling": return <AlertTriangle size={16} color="#C45B5B" />;
      default: return <BookOpen size={16} color="var(--text-secondary)" />;
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh", backgroundColor: "var(--bg-primary)" }}>
      
      <header style={{ display: "flex", alignItems: "center", gap: "1rem", padding: "2rem" }}>
        <Button variant="secondary" iconOnly onClick={() => router.push("/chat")}>
           <ArrowLeft size={20} />
        </Button>
        <h1 style={{ fontSize: "1.8rem" }}>Concept Graph</h1>
      </header>

      {loading || !layout ? (
        <div style={{ display: "flex", flex: 1, alignItems: "center", justifyContent: "center" }}>
          <p>Loading your curriculum graph...</p>
        </div>
      ) : (
        <main style={{ flex: 1, overflow: "auto", position: "relative" }}>
          <div style={{ width: layout.width, height: layout.height, position: "relative", margin: "0 auto" }}>
            
            {/* SVG Layer for Edges */}
            <svg style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%", zIndex: 0 }}>
              {layout.edges.map((e, idx) => {
                const s = layout.nodeCoords[e.source];
                const t = layout.nodeCoords[e.target];
                if (!s || !t) return null;
                const x1 = s.cx, y1 = s.cy + (NODE_HEIGHT / 2);
                const x2 = t.cx, y2 = t.cy - (NODE_HEIGHT / 2);
                
                // Active edge coloring based on target node mastery
                const targetMastery = masteryMap[e.target] || "unknown";
                const edgeColor = targetMastery !== "unknown" ? "#475569" : "#334155";
                const strokeWidth = targetMastery !== "unknown" ? 2 : 1;
                
                return (
                  <path 
                    key={idx}
                    d={`M ${x1},${y1} C ${x1},${y1 + 40} ${x2},${y2 - 40} ${x2},${y2}`}
                    fill="none"
                    stroke={edgeColor}
                    strokeWidth={strokeWidth}
                  />
                );
              })}
            </svg>

            {/* DOM Layer for Nodes */}
            {layout.nodes.map((n) => {
              const coords = layout.nodeCoords[n.concept_id];
              if (!coords) return null;
              
              const mastery = masteryMap[n.concept_id] || "unknown";
              const color = getStatusColor(mastery);
              
              return (
                <div 
                  key={n.concept_id}
                  className="glass-panel"
                  style={{
                    position: "absolute",
                    left: coords.cx - (NODE_WIDTH / 2),
                    top: coords.cy - (NODE_HEIGHT / 2),
                    width: NODE_WIDTH,
                    height: NODE_HEIGHT,
                    borderLeft: `4px solid ${color}`,
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "center",
                    padding: "0.75rem",
                    zIndex: 10,
                    boxShadow: mastery !== "unknown" ? "0 4px 6px -1px rgba(0, 0, 0, 0.1)" : "none",
                    opacity: mastery === "unknown" ? 0.7 : 1
                  }}
                >
                  <div style={{ fontSize: "0.9rem", fontWeight: 600, color: "#e2e8f0", marginBottom: "0.25rem", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }} title={n.name_en}>
                    {n.name_en}
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.8rem", color: "var(--text-secondary)" }}>
                    {getStatusIcon(mastery)}
                    <span style={{ textTransform: "capitalize" }}>{mastery}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </main>
      )}
    </div>
  );
}
