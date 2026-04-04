# Team Name: Byte Me

## Members:
- Abhiram Vikramaditya
- Tanmaya Kumar
- Samriddhi Verma

## Problem Statement:
Swarm Coordination "Linguist" (AgenticAI + Collaboration) 
The Problem: In a swarm of 5 drones, if Drone A finds the target, how does it tell Drones B-E to 
reposition without overwhelming the radio link? 
• The Task: Develop a Swarm-Comm Agent that translates a "Leader" drone's discovery into 
"Follower" instructions. 
• Goal: Create a script where Drone 1 detects an "Object of Interest." The Agent must then 
generate unique, non-conflicting mission updates for the other 4 drones to surround the 
object. 
• Success Metric: Collision-free path distribution and speed of swarm reconfiguration. 

## Tech Stack:
- HTML, CSS, JavaScript
- Canvas API

## Description:
Agent-based swarm coordination system with efficient communication and collision avoidance.

- Agent compresses instructions to reduce communication load  
- Broadcast-based coordination avoids O(N²) messaging  
- Parametric instructions (radius and angle) enable efficient execution  
- Communication layer handles delay, packet loss, and retries  
- Collision-free formation with stable and fast convergence  

---

## Approach

We designed a Swarm Communication Agent ("Linguist") that transforms a leader drone’s detection into minimal, structured instructions for follower drones.

The system focuses on efficient translation and distribution of information under communication constraints, rather than relying on heavy data exchange.

---

## Communication-Centric Design

### Naive Approach
Each drone receives full positional data:
- (x, y) coordinates for every drone  
- High bandwidth usage  
- Poor scalability  

---

### Proposed Approach (Compressed Instructions)

We transmit:
- Formation radius (R)  
- Unique angular assignment (θ) for each drone  

Each drone computes its own position locally:
- x = Tx + R × cos(θ)  
- y = Ty + R × sin(θ)  

This shifts computation from communication to the drones, significantly reducing network load.

---

## Communication Efficiency

| Method | Complexity |
|--------|-----------|
| Peer-to-peer communication | O(N²) |
| Naive broadcast | O(2N) |
| Proposed system | O(N + 2) |

This results in approximately 30% reduction in communication overhead.

---

## Communication Pipeline

1. A drone detects the target  
2. The detecting drone becomes the leader  
3. The agent generates compressed instructions  
4. Instructions are broadcast to all drones  
5. Drones receive instructions (with delay/loss simulation)  
6. Drones compute positions locally  
7. Formation is achieved  

---

## Communication Robustness

To simulate real-world conditions, the system includes:

- Packet loss (random message drops)  
- Transmission delay (latency simulation)  
- Retry mechanism for failed deliveries  

This ensures reliable coordination even under imperfect communication.

---

## Agentic AI (Decision Layer)

The agent acts as a decision-making module that translates swarm state into actionable instructions.

### Inputs:
- Average distance to the target  
- Spread (variance of drone distances)  
- Number of drones that have reached formation  

### Outputs:
- Formation radius  
- Behavioral mode:
  - Approach  
  - Contract  
  - Stabilize  

The agent defines global strategy rather than controlling individual drone paths.

---

## Leader-Based Coordination

- The first drone detecting the target becomes the leader  
- No predefined leader is required  
- Selection is event-driven  

This enables adaptive and fast coordination.

---

## Collision-Free Path Distribution

Collision avoidance is achieved through:

- Unique angular assignment for each drone  
- Structured circular formation  
- Local repulsion-based avoidance mechanism  

This ensures non-overlapping paths and stable convergence.

---

## System Architecture

Leader Detection  
→ Agent Decision (Global Strategy)  
→ Communication Layer (Broadcast)  
→ Local Drone Execution  
→ Formation Stabilization  

---

## Performance Metrics

- Communication Complexity: O(N)  
- Collision Handling Complexity: O(N²)  
- Communication Efficiency Gain: ~30%  
- Stable formation achieved  
- Robust under delay and packet loss  

---

## Key Insight

Instead of increasing communication, the system reduces it by encoding intelligence into compact, interpretable instructions.

---

## Tech Stack

- HTML, CSS, JavaScript  
- Canvas API  
- Vercel (Deployment)

---

## Links (To be updated)

- Live Demo: <Add Vercel Link>  
- Video Demo: <Add Drive Link>  
- Presentation: <Add PPT Link>  

---

## Conclusion

This project presents a communication-first approach to swarm coordination, where agent-driven instruction compression enables scalable, efficient, and reliable multi-agent collaboration under real-world constraints.