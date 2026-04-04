const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

canvas.width = 1000;
canvas.height = 700;

const systemDiv = document.getElementById("system");
const agentDiv = document.getElementById("agent");
const metricsDiv = document.getElementById("metrics");
const messagesDiv = document.getElementById("messages");

const N = 5;
let drones = [];
let target = { x: canvas.width/2, y: canvas.height/2 };

let state = "SEARCH";
let leader = null;

let messages = [];
function log(msg) {
  messages.unshift(msg);
  if (messages.length > 12) messages.pop();
}

// -------- DRONE --------
class Drone {
  constructor(id) {
    this.id = id;
    this.x = Math.random() * canvas.width;
    this.y = Math.random() * canvas.height;

    this.vx = 0;
    this.vy = 0;

    this.target = null;
    this.arrived = false;
    this.received = false;

    this.dirTimer = 0;
    this.dir = { x: 0, y: 0 };
  }

  search() {
    if (this.dirTimer <= 0) {
      let a = Math.random()*Math.PI*2;
      this.dir = {x:Math.cos(a), y:Math.sin(a)};
      this.dirTimer = 80 + Math.random()*120;
    }
    this.dirTimer--;

    this.vx += this.dir.x * 0.15;
    this.vy += this.dir.y * 0.15;
  }

  avoid(drones) {
    drones.forEach(o=>{
      if(o.id===this.id) return;
      let dx=this.x-o.x;
      let dy=this.y-o.y;
      let dist=Math.hypot(dx,dy);

      if(dist<30 && dist>0){
        this.vx += dx/dist * 0.4;
        this.vy += dy/dist * 0.4;
      }
    });
  }

  applyBoundary() {
    let m=60,f=0.5;

    if(this.x<m) this.vx+=f;
    if(this.x>canvas.width-m) this.vx-=f;
    if(this.y<m) this.vy+=f;
    if(this.y>canvas.height-m) this.vy-=f;
  }

  moveToTarget() {
    let dx=this.target.x-this.x;
    let dy=this.target.y-this.y;
    let dist=Math.hypot(dx,dy);

    if(dist<10){
      this.arrived=true;
      this.vx*=0.7;
      this.vy*=0.7;
      return;
    }

    this.arrived=false;

    this.vx += (dx/dist)*0.2;
    this.vy += (dy/dist)*0.2;
  }

  update(mode,drones){
    if(mode==="SEARCH") this.search();
    if(mode==="FORMATION" && this.target) this.moveToTarget();

    this.avoid(drones);
    this.applyBoundary();

    let speed=Math.hypot(this.vx,this.vy);
    let max=2.5;

    if(speed>max){
      this.vx=(this.vx/speed)*max;
      this.vy=(this.vy/speed)*max;
    }

    this.vx*=0.92;
    this.vy*=0.92;

    this.x+=this.vx;
    this.y+=this.vy;
  }

  draw(){
    // leader pulse
    if(this.id===leader){
      let pulse = 10 + Math.sin(Date.now()*0.01)*4;
      ctx.beginPath();
      ctx.arc(this.x,this.y,pulse,0,Math.PI*2);
      ctx.strokeStyle="yellow";
      ctx.stroke();
    }

    ctx.fillStyle =
      this.id===leader ? "yellow" :
      this.arrived ? "lime" :
      this.received ? "cyan" : "gray";

    ctx.beginPath();
    ctx.arc(this.x,this.y,6,0,Math.PI*2);
    ctx.fill();
  }
}

// -------- AGENT --------
let radius=100;
let agentMode="IDLE";

function agentDecision(avg,spread,arrived){
  if(spread>120){
    radius-=0.8;
    agentMode="CONTRACTING";
  }
  else if(avg>200){
    radius-=0.5;
    agentMode="APPROACHING";
  }
  else if(arrived>3){
    radius-=0.3;
    agentMode="STABILIZING";
  }
  else{
    agentMode="HOLD";
  }

  radius=Math.max(60,Math.min(150,radius));
}

// -------- INIT --------
for(let i=0;i<N;i++) drones.push(new Drone(i));

// -------- COMM --------
let pending={};
let received=new Set();

let packetLoss=0.3;
let delayRange=[300,1200];

let broadcastTime=0;
let lastRetry=0;

// -------- LOOP --------
function loop(){
  ctx.clearRect(0,0,canvas.width,canvas.height);

  // target
  ctx.fillStyle="red";
  ctx.beginPath();
  ctx.arc(target.x,target.y,6,0,Math.PI*2);
  ctx.fill();

  // formation circle
  ctx.strokeStyle="#555";
  ctx.beginPath();
  ctx.arc(target.x,target.y,radius,0,Math.PI*2);
  ctx.stroke();

  // -------- SEARCH --------
  if(state==="SEARCH"){
    drones.forEach(d=>{
      d.update("SEARCH",drones);

      let dist=Math.hypot(d.x-target.x,d.y-target.y);
      if(dist<80){
        leader=d.id;
        log("LEADER → Target detected");
        state="BROADCAST";
        broadcastTime=Date.now();
      }
    });
  }

  // -------- BROADCAST --------
  else if(state==="BROADCAST"){

    drones.forEach(d=>d.update("SEARCH",drones));

    // draw communication lines
    if(leader!==null){
      let L=drones[leader];
      drones.forEach(d=>{
        if(d.id!==leader){
          ctx.beginPath();
          ctx.moveTo(L.x,L.y);
          ctx.lineTo(d.x,d.y);
          ctx.strokeStyle="rgba(255,255,0,0.3)";
          ctx.stroke();
        }
      });
    }

    if(Date.now()-broadcastTime>1500){

      log("AGENT → Instructions generated");

      drones.forEach((d,i)=>{
        if(Math.random()<packetLoss){
          log(`COMM ❌ D${d.id}`);
          return;
        }

        let delay=Math.random()*(delayRange[1]-delayRange[0])+delayRange[0];

        pending[d.id]={
          angle:(2*Math.PI*i)/N,
          time:Date.now()+delay
        };

        log(`COMM 📡 D${d.id}`);
      });

      state="FORMATION";
    }
  }

  // -------- FORMATION --------
  else if(state==="FORMATION"){

    for(let id in pending){
      let inst=pending[id];

      if(Date.now()>inst.time){
        drones[id].received=true;

        drones[id].target={
          x:target.x+radius*Math.cos(inst.angle),
          y:target.y+radius*Math.sin(inst.angle)
        };

        received.add(parseInt(id));
        delete pending[id];

        log(`COMM ✅ D${id}`);
      }
    }

    if(Date.now()-lastRetry>1200){
      drones.forEach((d,i)=>{
        if(!received.has(d.id) && !pending[d.id]){
          pending[d.id]={
            angle:(2*Math.PI*i)/N,
            time:Date.now()+500
          };
          log(`COMM 🔁 D${d.id}`);
        }
      });
      lastRetry=Date.now();
    }

    let avg = drones.reduce((s,d)=>s+Math.hypot(d.x-target.x,d.y-target.y),0)/N;
    let spread = drones.reduce((s,d)=>s+(Math.hypot(d.x-target.x,d.y-target.y)-avg)**2,0)/N;
    let arrived = drones.filter(d=>d.arrived).length;

    agentDecision(avg,spread,arrived);

    drones.forEach(d=>d.update("FORMATION",drones));

    let collisions=0;
    for(let i=0;i<N;i++){
      for(let j=i+1;j<N;j++){
        if(Math.hypot(drones[i].x-drones[j].x,
                      drones[i].y-drones[j].y)<10){
          collisions++;
        }
      }
    }

    // -------- UI --------
    systemDiv.innerHTML = `
      <b>State:</b> ${state}<br>
      <b>Leader:</b> ${leader}
    `;

    agentDiv.innerHTML = `
      <b>Mode:</b> ${agentMode}<br>
      <b>Radius:</b> ${radius.toFixed(1)}<br>
      <b>Arrived:</b> ${arrived}
    `;

    let naive=N*2;
    let agentCost=N+2;
    let eff=((naive-agentCost)/naive)*100;

    metricsDiv.innerHTML = `
      <b>Efficiency:</b> <span style="color:lightgreen">${eff.toFixed(1)}%</span><br>
      <b>Collisions:</b> <span style="color:${collisions>0?'red':'lightgreen'}">${collisions}</span>
    `;
  }

  drones.forEach(d=>d.draw());

  messagesDiv.innerHTML = messages.map(m=>`<div>${m}</div>`).join("");

  requestAnimationFrame(loop);
}

loop();