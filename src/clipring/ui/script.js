// --- BACKGROUND PARTICLES ---
const canvas = document.getElementById('bg-canvas');
const ctx = canvas.getContext('2d');
let width, height;
let particles = [];

function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
}
window.addEventListener('resize', resize);
resize();

class Particle {
    constructor() {
        this.x = Math.random() * width;
        this.y = Math.random() * height;
        this.vx = (Math.random() - 0.5) * 2;
        this.vy = (Math.random() - 0.5) * 2;
        this.size = Math.random() * 2 + 1;
        this.color = Math.random() > 0.5 ? '#0ff' : '#f0f';
    }
    update() {
        this.x += this.vx; this.y += this.vy;
        if (this.x < 0 || this.x > width) this.vx *= -1;
        if (this.y < 0 || this.y > height) this.vy *= -1;
    }
    draw() {
        ctx.fillStyle = this.color;
        ctx.shadowBlur = 10; ctx.shadowColor = this.color;
        ctx.beginPath(); ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2); ctx.fill();
    }
}
for(let i=0; i<80; i++) particles.push(new Particle());

function animateBg() {
    ctx.clearRect(0, 0, width, height);
    particles.forEach(p => { p.update(); p.draw(); });
    ctx.lineWidth = 0.5;
    for(let i=0; i<particles.length; i++) {
        for(let j=i+1; j<particles.length; j++) {
            const dx = particles[i].x - particles[j].x;
            const dy = particles[i].y - particles[j].y;
            const dist = Math.sqrt(dx*dx + dy*dy);
            if(dist < 150) {
                ctx.strokeStyle = `rgba(0, 255, 255, ${1 - dist/150})`;
                ctx.beginPath(); ctx.moveTo(particles[i].x, particles[i].y);
                ctx.lineTo(particles[j].x, particles[j].y); ctx.stroke();
            }
        }
    }
    requestAnimationFrame(animateBg);
}
animateBg();

// --- SCROLL ANIMATIONS (INTERSECTION OBSERVER) ---
const observerOptions = { threshold: 0.1 };
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if(entry.isIntersecting) {
            entry.target.classList.add('in-view');
        }
    });
}, observerOptions);

document.querySelectorAll('.feature-card').forEach(card => {
    observer.observe(card);
});

// --- 3D TILT EFFECT ---
document.querySelectorAll('[data-tilt]').forEach(el => {
    el.addEventListener('mousemove', e => {
        const rect = el.getBoundingClientRect();
        const x = e.clientX - rect.left; const y = e.clientY - rect.top;
        const centerX = rect.width / 2; const centerY = rect.height / 2;
        const tiltX = (y - centerY) / 10; const tiltY = (centerX - x) / 10;
        el.style.transform = `perspective(1000px) rotateX(${tiltX}deg) rotateY(${tiltY}deg) scale3d(1.02, 1.02, 1.02)`;
    });
    el.addEventListener('mouseleave', () => {
        el.style.transform = `perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)`;
    });
});

// --- LAUNCH SEQUENCE ---
const initBtn = document.getElementById('initialize-btn');
const launchBox = document.querySelector('.launch-box');
const progressBarCtx = document.getElementById('boot-progress');
const progressBarFill = document.querySelector('.progress-bar-fill');
const landingView = document.getElementById('landing-view');
const navbar = document.getElementById('navbar');
const dashboardView = document.getElementById('dashboard-view');
const glitchOverlay = document.getElementById('screen-glitch');

initBtn.addEventListener('click', () => {
    // 1. Shake and Load
    initBtn.classList.add('hidden');
    progressBarCtx.classList.remove('hidden');
    launchBox.classList.add('shake');
    
    // Simulate loading
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if(progress > 100) progress = 100;
        progressBarFill.style.width = `${progress}%`;
        
        if(progress === 100) {
            clearInterval(interval);
            // Flash screen
            glitchOverlay.classList.remove('hidden');
            setTimeout(() => {
                // Swap views
                landingView.classList.add('hidden');
                navbar.classList.add('hidden');
                dashboardView.classList.remove('hidden');
                glitchOverlay.classList.add('hidden');
                startDashboardSimulation();
            }, 500);
        }
    }, 200);
});

// --- DASHBOARD SIMULATION ---
const savedCount = document.getElementById('saved-count');
const tokenCount = document.getElementById('token-count');
const consoleOutput = document.getElementById('console-output');
const simCopyBtn = document.getElementById('sim-copy-btn');
const toggleWebp = document.getElementById('toggle-webp');
const modelSelect = document.getElementById('model-select');

function writeConsole(text, color="#0f0") {
    consoleOutput.innerHTML += `> <span style="color:${color}">${text}</span><br>`;
    consoleOutput.scrollTop = consoleOutput.scrollHeight;
}

let dashStatsIntervals = [];

function startDashboardSimulation() {
    let s = 0; let t = 0;
    
    dashStatsIntervals.push(setInterval(() => {
        s += Math.floor(Math.random() * 2);
        savedCount.innerText = s;
    }, 5000));

    dashStatsIntervals.push(setInterval(() => {
        t += Math.floor(Math.random() * 100) + 10;
        tokenCount.innerText = t.toLocaleString();
    }, 800));

    dashStatsIntervals.push(setInterval(() => {
        const events = [
            "Scanning clipboard payload...", 
            "Nothing new detected.", 
            "System nominal."
        ];
        writeConsole(events[Math.floor(Math.random() * events.length)], "#888");
    }, 4000));
}

// Config interact
toggleWebp.addEventListener('change', (e) => {
    writeConsole(`[CONFIG] WebP to GIF Recovery: ${e.target.checked ? 'ENABLED' : 'DISABLED'}`, "#0ff");
});

modelSelect.addEventListener('change', (e) => {
    writeConsole(`[CONFIG] Neural core switched to: ${e.target.value}`, "#f0f");
});

// Sim Copy Button
simCopyBtn.addEventListener('click', () => {
    // Flash green
    document.body.style.boxShadow = "inset 0 0 100px #39ff14";
    setTimeout(() => document.body.style.boxShadow = "none", 300);
    
    writeConsole(`[ACTION] Manual Clipboard Trigger Sent.`, "#39ff14");
    
    setTimeout(() => {
        writeConsole(`[AUTO-SAVER] Detected 1 new image artifact.`, "#0ff");
        savedCount.innerText = parseInt(savedCount.innerText) + 1;
    }, 500);
    
    setTimeout(() => {
        writeConsole(`[LLM CORE] Streaming inference...`, "#f0f");
        tokenCount.innerText = (parseInt(tokenCount.innerText.replace(/,/g, '')) + 450).toLocaleString();
    }, 1500);
});

// --- MINI GAME ---
const catchBtn = document.getElementById('catch-btn');
const minigame = document.getElementById('minigame');
const endGameBtn = document.getElementById('end-game');
const gameArea = document.getElementById('game-area');
const scoreDisplay = document.getElementById('game-score');

let gameInterval;
let score = 0;

catchBtn.addEventListener('click', () => {
    minigame.classList.remove('hidden');
    score = 0;
    scoreDisplay.innerText = score;
    startGame();
});

endGameBtn.addEventListener('click', () => {
    minigame.classList.add('hidden');
    clearInterval(gameInterval);
    gameArea.innerHTML = '';
});

function startGame() {
    gameInterval = setInterval(() => {
        const item = document.createElement('div');
        item.classList.add('falling-item');
        // using ion icons for falling items
        const icons = ['image-outline', 'document-text-outline', 'code-outline', 'planet-outline'];
        item.innerHTML = `<ion-icon name="${icons[Math.floor(Math.random()*icons.length)]}"></ion-icon>`;
        
        const startX = Math.random() * (window.innerWidth - 60);
        item.style.left = `${startX}px`;
        item.style.top = `-60px`;
        gameArea.appendChild(item);
        
        let y = -60;
        const speed = Math.random() * 4 + 2;
        
        function fall() {
            y += speed;
            item.style.top = `${y}px`;
            if(y > window.innerHeight) {
                if(item.parentElement) item.remove();
            } else {
                requestAnimationFrame(fall);
            }
        }
        fall();
        
        item.addEventListener('mousedown', () => {
            score += 15;
            scoreDisplay.innerText = score;
            item.style.transform = 'scale(0) rotate(180deg)';
            item.style.opacity = '0';
            setTimeout(() => item.remove(), 200);
            
            const pop = document.createElement('div');
            pop.innerText = '+15';
            pop.style.position = 'absolute';
            pop.style.left = item.style.left;
            pop.style.top = item.style.top;
            pop.style.color = '#39ff14';
            pop.style.fontFamily = 'Orbitron, sans-serif';
            pop.style.fontSize = '24px';
            pop.style.animation = 'slideInUp 0.5s forwards';
            gameArea.appendChild(pop);
            setTimeout(()=>pop.remove(), 500);
        });
        
    }, 1000);
}
