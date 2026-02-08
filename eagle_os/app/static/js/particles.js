class ParticleSystem {
  constructor() {
    this.particles = [];
  }

  emit(x, y, intensity = 6) {
    for (let i = 0; i < intensity; i += 1) {
      this.particles.push({
        x,
        y,
        vx: (Math.random() - 0.5) * 1.5,
        vy: (Math.random() - 0.5) * 1.5,
        life: 1,
      });
    }
  }

  update() {
    this.particles = this.particles.filter((particle) => {
      particle.x += particle.vx;
      particle.y += particle.vy;
      particle.life -= 0.03;
      return particle.life > 0;
    });
  }

  draw(context) {
    this.particles.forEach((particle) => {
      context.fillStyle = `rgba(250, 204, 21, ${particle.life})`;
      context.fillRect(particle.x, particle.y, 2, 2);
    });
  }
}

window.ParticleSystem = ParticleSystem;
