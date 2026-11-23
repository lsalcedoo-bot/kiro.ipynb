#!/usr/bin/env node
/*
 Rasterizador SVG -> PNG minimalista, en Node puro (solo usa zlib).
 Soporta las primitivas que emiten flow_net_svg.py y subpresiones_svg.py:
   <rect>, <line>, <polyline>, <polygon>, <circle>, <text>
 con atributos fill, stroke, stroke-width, opacity/fill-opacity,
 stroke-dasharray (se ignora el guion y se pinta continuo), text-anchor,
 font-size, font-weight y transform="rotate(a cx cy)".
 El texto se dibuja con una fuente de trazos (stroke font) sencilla.

 Uso: node svg2png.js entrada.svg salida.png [escala]
*/
const fs = require("fs");
const zlib = require("zlib");

const [, , inPath, outPath, scaleArg] = process.argv;
const SS = Math.max(1, parseFloat(scaleArg || "2")); // supersampling para antialias
const svg = fs.readFileSync(inPath, "utf8");

// ---------- tamano del lienzo ----------
const mW = svg.match(/<svg[^>]*\bwidth="([\d.]+)"/);
const mH = svg.match(/<svg[^>]*\bheight="([\d.]+)"/);
const W0 = Math.round(parseFloat(mW[1]));
const H0 = Math.round(parseFloat(mH[1]));
const W = W0 * SS, H = H0 * SS;

// framebuffer RGBA, fondo blanco
const buf = new Uint8ClampedArray(W * H * 4).fill(255);

function px(x, y, [r, g, b], a = 1) {
  x = Math.round(x); y = Math.round(y);
  if (x < 0 || y < 0 || x >= W || y >= H) return;
  const i = (y * W + x) * 4;
  buf[i]   = buf[i]   * (1 - a) + r * a;
  buf[i+1] = buf[i+1] * (1 - a) + g * a;
  buf[i+2] = buf[i+2] * (1 - a) + b * a;
  buf[i+3] = 255;
}

function hex(c) {
  if (!c || c === "none") return null;
  c = c.trim();
  if (c[0] === "#") {
    if (c.length === 4) c = "#" + [...c.slice(1)].map(ch => ch + ch).join("");
    return [parseInt(c.slice(1,3),16), parseInt(c.slice(3,5),16), parseInt(c.slice(5,7),16)];
  }
  const named = { white:[255,255,255], black:[0,0,0], blue:[0,0,255], red:[255,0,0] };
  return named[c] || [0,0,0];
}

function disk(cx, cy, r, col, a=1){
  for (let y=-r-1; y<=r+1; y++)
    for (let x=-r-1; x<=r+1; x++){
      const d = Math.hypot(x,y);
      if (d <= r+0.5){
        const edge = Math.min(1, r+0.5 - d);
        px(cx+x, cy+y, col, a*edge);
      }
    }
}

function thickLine(x0,y0,x1,y1,wdt,col,a=1){
  const r = Math.max(0.5, wdt/2);
  const dx=x1-x0, dy=y1-y0, len=Math.hypot(dx,dy)||1;
  const n=Math.ceil(len);
  for(let k=0;k<=n;k++){
    const t=k/n;
    disk(x0+dx*t, y0+dy*t, r, col, a);
  }
}

function fillPolygon(pts, col, a=1){
  let minY=Infinity, maxY=-Infinity;
  for(const [,y] of pts){ if(y<minY)minY=y; if(y>maxY)maxY=y; }
  minY=Math.floor(minY); maxY=Math.ceil(maxY);
  for(let y=minY;y<=maxY;y++){
    const xs=[];
    for(let i=0;i<pts.length;i++){
      const [x1,y1]=pts[i], [x2,y2]=pts[(i+1)%pts.length];
      if((y1<=y&&y2>y)||(y2<=y&&y1>y)){
        xs.push(x1+(y-y1)/(y2-y1)*(x2-x1));
      }
    }
    xs.sort((p,q)=>p-q);
    for(let i=0;i+1<xs.length;i+=2){
      for(let x=Math.round(xs[i]);x<=Math.round(xs[i+1]);x++) px(x,y,col,a);
    }
  }
}

// ---------- fuente de trazos (stroke font) ----------
// Cada glifo: lista de polilineas en una celda 0..5 (x) x 0..7 (y, 0 arriba).
const F = {
  "0":[[[0,1],[0,6],[3,6],[3,1],[0,1]]],
  "1":[[[1,2],[2,1],[2,6]]],
  "2":[[[0,2],[1,1],[2,1],[3,2],[3,3],[0,6],[3,6]]],
  "3":[[[0,1],[3,1],[1,3],[3,4],[3,5],[2,6],[0,6]]],
  "4":[[[2,1],[0,4],[3,4]],[[2,1],[2,6]]],
  "5":[[[3,1],[0,1],[0,3],[2,3],[3,4],[3,5],[2,6],[0,6]]],
  "6":[[[3,1],[1,1],[0,3],[0,6],[3,6],[3,4],[0,4]]],
  "7":[[[0,1],[3,1],[1,6]]],
  "8":[[[0,1],[3,1],[3,6],[0,6],[0,1]],[[0,3.5],[3,3.5]]],
  "9":[[[3,4],[0,4],[0,1],[3,1],[3,6],[1,6]]],
  ".":[[[1,6],[1.3,6]]],
  "-":[[[0,3.5],[3,3.5]]],
  "=":[[[0,3],[3,3]],[[0,4.5],[3,4.5]]],
  "x":[[[0,2],[3,6]],[[3,2],[0,6]]],
  " ":[],
  "A":[[[0,6],[1.5,1],[3,6]],[[0.6,4],[2.4,4]]],
  "B":[[[0,1],[0,6],[2,6],[3,5],[2,3.5],[0,3.5]],[[2,3.5],[3,2.5],[2,1],[0,1]]],
  "C":[[[3,2],[1,1],[0,3],[0,4],[1,6],[3,5]]],
  "D":[[[0,1],[0,6],[2,6],[3,4.5],[3,2.5],[2,1],[0,1]]],
  "E":[[[3,1],[0,1],[0,6],[3,6]],[[0,3.5],[2,3.5]]],
  "F":[[[3,1],[0,1],[0,6]],[[0,3.5],[2,3.5]]],
  "H":[[[0,1],[0,6]],[[3,1],[3,6]],[[0,3.5],[3,3.5]]],
  "I":[[[1.5,1],[1.5,6]]],
  "L":[[[0,1],[0,6],[3,6]]],
  "N":[[[0,6],[0,1],[3,6],[3,1]]],
  "P":[[[0,6],[0,1],[3,1],[3,3.5],[0,3.5]]],
  "R":[[[0,6],[0,1],[3,1],[3,3.5],[0,3.5]],[[1.5,3.5],[3,6]]],
  "S":[[[3,1.5],[1,1],[0,2.5],[2,3.5],[3,4.5],[2,6],[0,5.5]]],
  "T":[[[0,1],[3,1]],[[1.5,1],[1.5,6]]],
  "U":[[[0,1],[0,5],[1.5,6],[3,5],[3,1]]],
  "a":[[[0,3],[3,3],[3,6],[0,6],[0,4.5],[3,4.5]]],
  "b":[[[0,1],[0,6],[3,6],[3,3],[0,3]]],
  "c":[[[3,3.5],[0,3.5],[0,6],[3,6]]],
  "d":[[[3,1],[3,6],[0,6],[0,3],[3,3]]],
  "e":[[[0,4.5],[3,4.5],[3,3],[0,3],[0,6],[3,6]]],
  "f":[[[3,1.5],[2,1],[1.5,2],[1.5,6]],[[0.5,3.5],[2.5,3.5]]],
  "g":[[[3,3],[0,3],[0,4.5],[3,4.5],[3,7],[1,7]]],
  "i":[[[1.5,3],[1.5,6]],[[1.5,1.5],[1.5,2]]],
  "j":[[[2,3],[2,7],[0.5,7]],[[2,1.5],[2,2]]],
  "k":[[[0,1],[0,6]],[[3,3],[0,4.5],[3,6]]],
  "l":[[[1.5,1],[1.5,6]]],
  "m":[[[0,6],[0,3],[1.5,3],[1.5,6]],[[1.5,3],[3,3],[3,6]]],
  "n":[[[0,6],[0,3],[3,3],[3,6]]],
  "o":[[[0,3],[3,3],[3,6],[0,6],[0,3]]],
  "p":[[[0,7],[0,3],[3,3],[3,4.5],[0,4.5]]],
  "q":[[[3,7],[3,3],[0,3],[0,4.5],[3,4.5]]],
  "r":[[[0,6],[0,3],[2.5,3]]],
  "s":[[[3,3],[0,3],[0,4.5],[3,4.5],[3,6],[0,6]]],
  "t":[[[1.5,1.5],[1.5,6],[3,6]],[[0.5,3],[2.5,3]]],
  "u":[[[0,3],[0,6],[3,6],[3,3]]],
  "v":[[[0,3],[1.5,6],[3,3]]],
  "w":[[[0,3],[0.8,6],[1.5,4],[2.2,6],[3,3]]],
  "z":[[[0,3],[3,3],[0,6],[3,6]]],
  "/":[[[3,1],[0,6]],],
  "3H":[[]],
};

function drawText(x, y, str, size, col, anchor, rot, cx, cy){
  const cellH = 7, scale = size / cellH, gap = size*0.22;
  const cw = 3*scale + gap;
  const total = str.length * cw - gap;
  let ox = x;
  if (anchor === "middle") ox = x - total/2;
  else if (anchor === "end") ox = x - total;
  const baseY = y - size*0.78; // y es baseline aprox
  const rad = rot ? -rot*Math.PI/180 : 0;
  const rc = Math.cos(rad), rs = Math.sin(rad);
  const tf = (px_, py_) => {
    if (!rot) return [px_, py_];
    const dx=px_-cx, dy=py_-cy;
    return [cx+dx*rc-dy*rs, cy+dx*rs+dy*rc];
  };
  for (const ch of str){
    const g = F[ch] !== undefined ? F[ch] : F["."];
    for (const stroke of g){
      for (let i=0;i+1<stroke.length;i++){
        let [ax,ay]=stroke[i], [bx,by]=stroke[i+1];
        let p0=[ox+ax*scale, baseY+ay*scale];
        let p1=[ox+bx*scale, baseY+by*scale];
        p0=tf(p0[0],p0[1]); p1=tf(p1[0],p1[1]);
        thickLine(p0[0],p0[1],p1[0],p1[1], Math.max(1, size*0.09), col, 1);
      }
    }
    ox += cw;
  }
}

// ---------- parser de atributos ----------
function attrs(tag){
  const o={}; let m; const re=/([\w:-]+)="([^"]*)"/g;
  while((m=re.exec(tag))) o[m[1]]=m[2];
  return o;
}
const S = v => parseFloat(v)*SS;

// ---------- recorrer elementos en orden ----------
// Un solo regex: captura <text ...>contenido</text> O cualquier primitiva
// autocerrada <rect .../> <line .../> etc.
const tagRe = /<text\b([^>]*)>([\s\S]*?)<\/text>|<(rect|line|polyline|polygon|circle)\b([^>]*?)\/?>/g;
let m;
while((m = tagRe.exec(svg))){
  let name, a, inner;
  if (m[0].startsWith("<text")) { name="text"; a=attrs(m[1]); inner=m[2]; }
  else { name=m[3]; a=attrs(m[4]); inner=undefined; }
  const fill=hex(a.fill), stroke=hex(a.stroke);
  const sw=(parseFloat(a["stroke-width"]||"1"))*SS;
  const op=parseFloat(a["fill-opacity"]||a["opacity"]||"1");

  if(name==="rect"){
    const x=S(a.x), y=S(a.y), w=S(a.width), h=S(a.height);
    if(fill) fillPolygon([[x,y],[x+w,y],[x+w,y+h],[x,y+h]], fill, op);
    if(stroke){ thickLine(x,y,x+w,y,sw,stroke);thickLine(x+w,y,x+w,y+h,sw,stroke);
      thickLine(x+w,y+h,x,y+h,sw,stroke);thickLine(x,y+h,x,y,sw,stroke);}
  } else if(name==="line"){
    if(stroke) thickLine(S(a.x1),S(a.y1),S(a.x2),S(a.y2),sw,stroke,op<1?op:1);
  } else if(name==="polyline"||name==="polygon"){
    const pts=a.points.trim().split(/\s+/).map(p=>p.split(",").map(Number).map(v=>v*SS));
    if(name==="polygon"&&fill) fillPolygon(pts, fill, op);
    if(stroke) for(let i=0;i+1<pts.length;i++) thickLine(pts[i][0],pts[i][1],pts[i+1][0],pts[i+1][1],sw,stroke);
    if(name==="polygon"&&stroke) thickLine(pts[pts.length-1][0],pts[pts.length-1][1],pts[0][0],pts[0][1],sw,stroke);
  } else if(name==="circle"){
    const cx=S(a.cx), cy=S(a.cy), r=S(a.r);
    if(fill) disk(cx,cy,r,fill,1);
    if(stroke){ for(let t=0;t<360;t+=2){const rad=t*Math.PI/180; disk(cx+r*Math.cos(rad),cy+r*Math.sin(rad),sw/2,stroke,1);} }
  } else if(name==="text"){
    const txt=(inner||"").replace(/&amp;/g,"&").replace(/&lt;/g,"<").replace(/&gt;/g,">").trim();
    if(!txt) continue;
    const size=(parseFloat(a["font-size"]||"12"))*SS;
    const col=hex(a.fill)||[0,0,0];
    const anchor=a["text-anchor"]||"start";
    let rot=0,cx=0,cy=0;
    const tr=a.transform&&a.transform.match(/rotate\(([-\d.]+)\s+([\d.]+)\s+([\d.]+)\)/);
    if(tr){ rot=parseFloat(tr[1]); cx=parseFloat(tr[2])*SS; cy=parseFloat(tr[3])*SS; }
    drawText(S(a.x), S(a.y), txt, size, col, anchor, rot, cx, cy);
  }
}

// ---------- downsample (supersampling -> antialias) y PNG ----------
const out = Buffer.alloc(W0*H0*4);
for(let y=0;y<H0;y++) for(let x=0;x<W0;x++){
  let r=0,g=0,b=0;
  for(let j=0;j<SS;j++) for(let i=0;i<SS;i++){
    const k=((y*SS+j)*W + (x*SS+i))*4;
    r+=buf[k]; g+=buf[k+1]; b+=buf[k+2];
  }
  const n=SS*SS, o=(y*W0+x)*4;
  out[o]=r/n; out[o+1]=g/n; out[o+2]=b/n; out[o+3]=255;
}

function crc32(buf){
  let c=~0;
  for(let i=0;i<buf.length;i++){ c^=buf[i];
    for(let k=0;k<8;k++) c = (c>>>1) ^ (0xEDB88320 & -(c&1)); }
  return ~c>>>0;
}
function chunk(type, data){
  const len=Buffer.alloc(4); len.writeUInt32BE(data.length,0);
  const t=Buffer.from(type,"ascii");
  const crc=Buffer.alloc(4); crc.writeUInt32BE(crc32(Buffer.concat([t,data])),0);
  return Buffer.concat([len,t,data,crc]);
}
const sig=Buffer.from([137,80,78,71,13,10,26,10]);
const ihdr=Buffer.alloc(13);
ihdr.writeUInt32BE(W0,0); ihdr.writeUInt32BE(H0,4);
ihdr[8]=8; ihdr[9]=6; // 8-bit, RGBA
const raw=Buffer.alloc((W0*4+1)*H0);
for(let y=0;y<H0;y++){ raw[y*(W0*4+1)]=0; out.copy(raw, y*(W0*4+1)+1, y*W0*4, (y+1)*W0*4); }
const idat=zlib.deflateSync(raw,{level:9});
const png=Buffer.concat([sig,chunk("IHDR",ihdr),chunk("IDAT",idat),chunk("IEND",Buffer.alloc(0))]);
fs.writeFileSync(outPath,png);
console.log(`[OK] ${outPath}  (${W0}x${H0}, supersampling ${SS}x)`);
