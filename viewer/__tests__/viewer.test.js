const loadViewerModule = () => {
    jest.isolateModules(() => {
        require('../viewer');
    });
};

describe('viewer interactions', () => {
    let mv;
    let explode;
    let legend;
    let dark;
    let start;
    let nodes;

    const dispatchLoad = () => {
        mv.dispatchEvent(new Event('load'));
    };

    beforeEach(() => {
        jest.resetModules();
        document.body.innerHTML = `
      <div id="mv"></div>
      <input id="explode" type="range" value="0" />
      <ul id="legend"></ul>
      <button id="dark"></button>
      <button id="start"></button>
    `;
        mv = document.getElementById('mv');
        explode = document.getElementById('explode');
        legend = document.getElementById('legend');
        dark = document.getElementById('dark');
        start = document.getElementById('start');
        mv.play = jest.fn();
        nodes = [
            { name: 'Frame', visible: true, position: { z: 0 } },
            { name: '', visible: true, position: { z: 0 } },
            { name: 'Panel', visible: true, position: { z: 0 } },
        ];
        mv.model = { scene: { children: nodes } };
    });

    test('renders legend entries and toggles visibility', () => {
        loadViewerModule();
        dispatchLoad();

        const items = legend.querySelectorAll('li');
        expect(items).toHaveLength(nodes.length);

        const [first, second] = items;
        expect(first.querySelector('button').textContent).toBe('Frame');
        expect(second.querySelector('button').textContent).toBe('part-1');

        const firstButton = first.querySelector('button');
        const secondButton = second.querySelector('button');

        firstButton.click();
        expect(first.classList.contains('hidden')).toBe(true);
        expect(nodes[0].visible).toBe(false);

        firstButton.click();
        expect(first.classList.contains('hidden')).toBe(false);
        expect(first.classList.contains('solo')).toBe(true);
        expect(nodes[0].visible).toBe(true);
        expect(nodes[1].visible).toBe(false);
        expect(nodes[2].visible).toBe(false);

        secondButton.click();
        expect(second.classList.contains('hidden')).toBe(true);
        expect(nodes[1].visible).toBe(false);

        secondButton.click();
        expect(first.classList.contains('solo')).toBe(false);
        expect(second.classList.contains('hidden')).toBe(false);
        expect(second.classList.contains('solo')).toBe(true);
        expect(nodes[0].visible).toBe(false);
        expect(nodes[1].visible).toBe(true);
        expect(nodes[2].visible).toBe(false);

        secondButton.click();
        expect(second.classList.contains('hidden')).toBe(true);
        expect(second.classList.contains('solo')).toBe(true);
        expect(nodes[1].visible).toBe(false);

        secondButton.click();
        expect(second.classList.contains('hidden')).toBe(false);
        expect(second.classList.contains('solo')).toBe(false);
        expect(nodes.every((node) => node.visible)).toBe(true);
    });

    test('explode slider offsets meshes along the z axis', () => {
        loadViewerModule();
        dispatchLoad();

        explode.value = '1.25';
        explode.dispatchEvent(new Event('input'));

        expect(nodes[0].position.z).toBeCloseTo(0);
        expect(nodes[1].position.z).toBeCloseTo(12.5);
        expect(nodes[2].position.z).toBeCloseTo(25);
    });

    test('dark mode toggles a class on the body', () => {
        loadViewerModule();

        expect(document.body.classList.contains('dark')).toBe(false);
        dark.click();
        expect(document.body.classList.contains('dark')).toBe(true);
        dark.click();
        expect(document.body.classList.contains('dark')).toBe(false);
    });

    test('start button plays the model viewer animation', () => {
        loadViewerModule();

        start.click();
        expect(mv.play).toHaveBeenCalledTimes(1);
    });
});
