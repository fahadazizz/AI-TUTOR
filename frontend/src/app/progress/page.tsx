"use client";

import { useState, useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { ArrowLeft, CheckCircle, Clock, AlertTriangle, BookOpen } from "lucide-react";
import { ReactFlow, Background, Controls, Node, Edge, Position } from "@xyflow/react";
import '@xyflow/react/dist/style.css';

const NODE_WIDTH = 240;
const NODE_HEIGHT = 80;
const LEVEL_HEIGHT = 150;

// Custom Node Component for beautifully displaying mastery
const CustomNode = ({ data }: any) => {
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

  const color = getStatusColor(data.mastery);
  
  return (
    <div 
      className="glass-panel"
      style={{
        width: NODE_WIDTH,
        height: NODE_HEIGHT,
        backgroundColor: "#1e293b", 
        borderLeft: `4px solid ${color}`,
        borderRadius: "8px",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        padding: "0.75rem",
        boxShadow: data.mastery !== "unknown" ? "0 4px 12px -2px rgba(0, 0, 0, 0.4)" : "none",
        opacity: data.mastery === "unknown" ? 0.8 : 1,
        color: "#f8fafc"
      }}
    >
      <div style={{ fontSize: "0.95rem", fontWeight: 600, marginBottom: "0.4rem", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }} title={data.name}>
        {data.name}
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.85rem", color: "var(--text-secondary)" }}>
        {getStatusIcon(data.mastery)}
        <span style={{ textTransform: "capitalize" }}>{data.mastery}</span>
      </div>
    </div>
  );
};

const nodeTypes = {
  custom: CustomNode,
};

export default function ProgressPage() {
  const router = useRouter();
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
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
        
        // Compute topological layout
        const layoutNodes: Node[] = [];
        const layoutEdges: Edge[] = [];
        
        if (graphRes.nodes.length) {
          // 1. Calculate in-degrees and hierarchy
          const inDegree: Record<string, number> = {};
          const children: Record<string, string[]> = {};
          
          graphRes.nodes.forEach((n: any) => {
            inDegree[n.concept_id] = 0;
            children[n.concept_id] = [];
          });
          
          graphRes.edges.forEach((e: any) => {
            if (inDegree[e.target] !== undefined) {
              inDegree[e.target]++;
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
          
          // Group by levels
          const levels: Record<number, any[]> = {};
          graphRes.nodes.forEach((n: any) => {
            const d = depth[n.concept_id] || 0;
            if (!levels[d]) levels[d] = [];
            levels[d].push(n);
          });
          
          // Build React Flow Nodes
          Object.keys(levels).forEach(dStr => {
            const d = parseInt(dStr);
            const levelNodes = levels[d];
            levelNodes.sort((a: any, b: any) => a.concept_id.localeCompare(b.concept_id));
            
            const totalWidth = levelNodes.length * (NODE_WIDTH + 50);
            
            levelNodes.forEach((node: any, i: number) => {
              const xPos = (i * (NODE_WIDTH + 50)) - (totalWidth / 2) + 400; // Center offset
              const yPos = d * LEVEL_HEIGHT;
              
              layoutNodes.push({
                id: node.concept_id,
                type: 'custom',
                position: { x: xPos, y: yPos },
                data: {
                  name: node.name_en,
                  mastery: mMap[node.concept_id] || "unknown"
                },
                sourcePosition: Position.Bottom,
                targetPosition: Position.Top
              });
            });
          });
          
          // Build React Flow Edges
          graphRes.edges.forEach((e: any, i: number) => {
            const targetMastery = mMap[e.target] || "unknown";
            layoutEdges.push({
              id: `e-${e.source}-${e.target}`,
              source: e.source,
              target: e.target,
              animated: targetMastery !== "unknown",
              style: { 
                stroke: targetMastery !== "unknown" ? "#94a3b8" : "#334155", 
                strokeWidth: targetMastery !== "unknown" ? 2 : 1 
              }
            });
          });
        }
        
        setNodes(layoutNodes);
        setEdges(layoutEdges);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [router]);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh", backgroundColor: "var(--bg-primary)" }}>
      
      <header style={{ display: "flex", alignItems: "center", gap: "1rem", padding: "1.5rem 2rem", borderBottom: "1px solid var(--bg-tertiary)", zIndex: 10 }}>
        <Button variant="secondary" iconOnly onClick={() => router.push("/chat")}>
           <ArrowLeft size={20} />
        </Button>
        <h1 style={{ fontSize: "1.5rem", fontWeight: 600 }}>Concept Mastery Graph</h1>
      </header>

      {loading ? (
        <div style={{ display: "flex", flex: 1, alignItems: "center", justifyContent: "center" }}>
          <p className="text-slate-400 animate-pulse">Loading curriculum map...</p>
        </div>
      ) : (
        <main style={{ flex: 1, width: "100%", height: "100%" }}>
          <ReactFlow 
            nodes={nodes} 
            edges={edges}
            nodeTypes={nodeTypes}
            fitView
            minZoom={0.5}
            maxZoom={2}
            className="bg-slate-950"
          >
            <Background color="#334155" gap={16} size={1} />
            <Controls style={{ background: "#1e293b", borderColor: "#334155", fill: "#94a3b8" }} />
          </ReactFlow>
        </main>
      )}
    </div>
  );
}
