const mv = document.getElementById('mv');
const explode = document.getElementById('explode');
const legend = document.getElementById('legend');
const dark = document.getElementById('dark');
const play = document.getElementById('play');
let nodes = [];

mv.addEventListener('load', () => {
  const scene = mv.model?.scene;
  if (!scene) return;
  nodes = scene.children;
  legend.innerHTML = '';
  nodes.forEach((n, i) => {
    const li = document.createElement('li');
    const btn = document.createElement('button');
    btn.className = 'part';
    btn.textContent = n.name || `part-${i}`;
    btn.addEventListener('click', () => {
      if (btn.classList.toggle('hidden')) {
        n.visible = false;
      } else {
        const solo = legend.querySelector('.solo');
        if (solo && solo !== btn) {
          nodes.forEach((m) => (m.visible = true));
          solo.classList.remove('solo');
        }
        if (btn.classList.toggle('solo')) {
          nodes.forEach((m, j) => (m.visible = j === i));
        } else {
          nodes.forEach((m) => (m.visible = true));
        }
      }
    });
    li.appendChild(btn);
    legend.appendChild(li);
  });
});

explode.addEventListener('input', () => {
  const f = parseFloat(explode.value);
  nodes.forEach((n, i) => {
    n.position.z = i * f * 10;
  });
});

dark.addEventListener('click', () => {
  document.body.classList.toggle('dark');
});

play.addEventListener('click', () => {
  if (mv.paused) {
    mv.play();
    play.textContent = 'Pause';
  } else {
    mv.pause();
    play.textContent = 'Play';
  }
});
