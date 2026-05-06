// ============================================================================
// EXHIBITION BOOTH 3D CONFIGURATOR – CORRECTED & MULTILINGUAL
// ============================================================================

const CONFIG = {
    construction: {
        standard: { name: 'Standard', price: 500 },
        exclusive: { name: 'Exclusive', price: 800 }
    },
    materials: {
        plastic: { name: 'Plastic', pricePerM2: 50 },
        wood: { name: 'Wood', pricePerM2: 150 },
        metal: { name: 'Metal', pricePerM2: 200 }
    },
    equipment: {
        lighting: { name: 'Lighting', price: 300 },
        furniture: { name: 'Furniture', price: 400 },
        monitor: { name: 'Monitor', price: 800 }
    }
};

// Переводы для сообщений
const i18n = {
    ru: {
        saved: '✅ Конфигурация сохранена',
        reset: '🔄 Конфигурация сброшена',
        copySuccess: '🔗 Ссылка скопирована в буфер обмена',
        share: 'Поделиться: '
    },
    en: {
        saved: '✅ Configuration saved',
        reset: '🔄 Configuration reset',
        copySuccess: '🔗 Link copied to clipboard',
        share: 'Share: '
    },
    lv: {
        saved: '✅ Konfigurācija saglabāta',
        reset: '🔄 Konfigurācija atiestatīta',
        copySuccess: '🔗 Saite nokopēta starpliktuvē',
        share: 'Dalīties: '
    }
};

// Текущий язык (можно менять глобально)
let currentLanguage = 'en';

// ============================================================================
// STATE MANAGEMENT
// ============================================================================
let state = {
    length: 3,
    width: 3,
    construction: 'standard',
    wallColor: '#FF6B6B',
    materials: [],
    equipment: []
};

// ============================================================================
// THREE.JS SETUP
// ============================================================================
let scene, camera, renderer, boothGroup;
const canvasContainer = document.getElementById('canvas');

function initThreeJS() {
    if (!canvasContainer) return;

    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf0f0f0);
    scene.fog = new THREE.Fog(0xf0f0f0, 100, 1000);

    const width = canvasContainer.clientWidth;
    const height = canvasContainer.clientHeight;
    camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.set(8, 6, 8);
    camera.lookAt(0, 0, 0);

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    canvasContainer.appendChild(renderer.domElement);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 15, 10);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    directionalLight.shadow.camera.left = -20;
    directionalLight.shadow.camera.right = 20;
    directionalLight.shadow.camera.top = 20;
    directionalLight.shadow.camera.bottom = -20;
    directionalLight.shadow.camera.far = 50;
    scene.add(directionalLight);

    // Ground
    const groundGeometry = new THREE.PlaneGeometry(50, 50);
    const groundMaterial = new THREE.MeshStandardMaterial({ color: 0xcccccc });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);

    // Booth Group
    boothGroup = new THREE.Group();
    scene.add(boothGroup);

    setupControls();
    createBooth();
    animate();

    window.addEventListener('resize', onWindowResize);
}

function createBooth() {
    while (boothGroup.children.length > 0) {
        boothGroup.remove(boothGroup.children[0]);
    }

    const length = state.length;
    const width = state.width;
    const height = 2.5;

    const wallColor = new THREE.Color(state.wallColor);
    const wallMaterial = new THREE.MeshStandardMaterial({
        color: wallColor,
        roughness: 0.7,
        metalness: 0.1
    });

    // Back wall
    const backWallGeometry = new THREE.BoxGeometry(length, height, 0.1);
    const backWall = new THREE.Mesh(backWallGeometry, wallMaterial);
    backWall.position.z = -width / 2;
    backWall.castShadow = true;
    backWall.receiveShadow = true;
    boothGroup.add(backWall);

    // Left wall
    const leftWallGeometry = new THREE.BoxGeometry(0.1, height, width);
    const leftWall = new THREE.Mesh(leftWallGeometry, wallMaterial);
    leftWall.position.x = -length / 2;
    leftWall.castShadow = true;
    leftWall.receiveShadow = true;
    boothGroup.add(leftWall);

    // Right wall
    const rightWall = new THREE.Mesh(leftWallGeometry, wallMaterial);
    rightWall.position.x = length / 2;
    rightWall.castShadow = true;
    rightWall.receiveShadow = true;
    boothGroup.add(rightWall);

    // Floor
    const floorGeometry = new THREE.BoxGeometry(length, 0.05, width);
    const floorMaterial = new THREE.MeshStandardMaterial({
        color: 0x888888,
        roughness: 0.8
    });
    const floor = new THREE.Mesh(floorGeometry, floorMaterial);
    floor.position.y = -0.025;
    floor.castShadow = true;
    floor.receiveShadow = true;
    boothGroup.add(floor);

    addEquipment();
    boothGroup.position.y = 0;
}

function addEquipment() {
    // Lighting
    if (state.equipment.includes('lighting')) {
        const lightGeometry = new THREE.SphereGeometry(0.15, 8, 8);
        const lightMaterial = new THREE.MeshStandardMaterial({
            color: 0xffff00,
            emissive: 0xffff00,
            emissiveIntensity: 0.5
        });
        const light1 = new THREE.Mesh(lightGeometry, lightMaterial);
        light1.position.set(-state.length / 3, 2, -state.width / 3);
        boothGroup.add(light1);

        const light2 = new THREE.Mesh(lightGeometry, lightMaterial);
        light2.position.set(state.length / 3, 2, -state.width / 3);
        boothGroup.add(light2);
    }

    // Furniture
    if (state.equipment.includes('furniture')) {
        const furnitureGeometry = new THREE.BoxGeometry(0.8, 0.8, 0.4);
        const furnitureMaterial = new THREE.MeshStandardMaterial({
            color: 0x8B4513,
            roughness: 0.6
        });
        const furniture1 = new THREE.Mesh(furnitureGeometry, furnitureMaterial);
        furniture1.position.set(-state.length / 3, 0.4, 0);
        furniture1.castShadow = true;
        furniture1.receiveShadow = true;
        boothGroup.add(furniture1);

        const furniture2 = new THREE.Mesh(furnitureGeometry, furnitureMaterial);
        furniture2.position.set(state.length / 3, 0.4, 0);
        furniture2.castShadow = true;
        furniture2.receiveShadow = true;
        boothGroup.add(furniture2);
    }

    // Monitor
    if (state.equipment.includes('monitor')) {
        const monitorGeometry = new THREE.BoxGeometry(0.6, 0.4, 0.05);
        const monitorMaterial = new THREE.MeshStandardMaterial({
            color: 0x000000,
            roughness: 0.3,
            metalness: 0.8
        });
        const monitor = new THREE.Mesh(monitorGeometry, monitorMaterial);
        monitor.position.set(0, 1.2, -state.width / 2 + 0.1);
        monitor.castShadow = true;
        monitor.receiveShadow = true;
        boothGroup.add(monitor);

        const screenGeometry = new THREE.BoxGeometry(0.55, 0.35, 0.02);
        const screenMaterial = new THREE.MeshStandardMaterial({
            color: 0x00ff00,
            emissive: 0x00ff00,
            emissiveIntensity: 0.3
        });
        const screen = new THREE.Mesh(screenGeometry, screenMaterial);
        screen.position.z += 0.04;
        monitor.add(screen);
    }
}

function setupControls() {
    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };

    renderer.domElement.addEventListener('mousedown', (e) => {
        isDragging = true;
        previousMousePosition = { x: e.clientX, y: e.clientY };
    });

    renderer.domElement.addEventListener('mousemove', (e) => {
        if (isDragging && e.buttons === 1) {
            const deltaX = e.clientX - previousMousePosition.x;
            const deltaY = e.clientY - previousMousePosition.y;

            boothGroup.rotation.y += deltaX * 0.01;
            boothGroup.rotation.x += deltaY * 0.01;

            previousMousePosition = { x: e.clientX, y: e.clientY };
        }
    });

    renderer.domElement.addEventListener('mouseup', () => {
        isDragging = false;
    });

    // Прокрутка – изменение расстояния до центра
    renderer.domElement.addEventListener('wheel', (e) => {
        e.preventDefault();
        const direction = new THREE.Vector3();
        camera.getWorldDirection(direction);
        camera.position.addScaledVector(direction, e.deltaY * 0.01);
    });

    renderer.domElement.addEventListener('contextmenu', (e) => {
        e.preventDefault();
    });
}

function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}

function onWindowResize() {
    if (!camera || !renderer) return;
    const width = canvasContainer.clientWidth;
    const height = canvasContainer.clientHeight;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
}

// ============================================================================
// COST CALCULATION
// ============================================================================
function calculateCost() {
    const area = state.length * state.width;
    
    const basePrice = CONFIG.construction[state.construction].price * area;
    
    let materialsPrice = 0;
    state.materials.forEach(material => {
        materialsPrice += CONFIG.materials[material].pricePerM2 * area;
    });
    
    let equipmentPrice = 0;
    state.equipment.forEach(equipment => {
        equipmentPrice += CONFIG.equipment[equipment].price;
    });
    
    return {
        base: basePrice,
        materials: materialsPrice,
        equipment: equipmentPrice,
        total: basePrice + materialsPrice + equipmentPrice
    };
}

function updateCostDisplay() {
    const costs = calculateCost();
    
    const baseEl = document.getElementById('costBase');
    const matEl = document.getElementById('costMaterials');
    const equipEl = document.getElementById('costEquipment');
    const totalEl = document.getElementById('costTotal');
    if (baseEl) baseEl.textContent = `${costs.base.toFixed(2)}€`;
    if (matEl) matEl.textContent = `${costs.materials.toFixed(2)}€`;
    if (equipEl) equipEl.textContent = `${costs.equipment.toFixed(2)}€`;
    if (totalEl) totalEl.textContent = `${costs.total.toFixed(2)}€`;
}

// ============================================================================
// UI EVENT HANDLERS
// ============================================================================
document.getElementById('lengthInput')?.addEventListener('change', (e) => {
    state.length = parseFloat(e.target.value);
    createBooth();
    updateCostDisplay();
});

document.getElementById('widthInput')?.addEventListener('change', (e) => {
    state.width = parseFloat(e.target.value);
    createBooth();
    updateCostDisplay();
});

document.querySelectorAll('[data-construction]').forEach(btn => {
    btn.addEventListener('click', (e) => {
        document.querySelectorAll('[data-construction]').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        state.construction = e.target.dataset.construction;
        updateCostDisplay();
    });
});

document.querySelectorAll('.color-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        document.querySelectorAll('.color-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        state.wallColor = e.target.dataset.color;
        createBooth();
    });
});

document.querySelectorAll('[data-material]').forEach(checkbox => {
    checkbox.addEventListener('change', (e) => {
        if (e.target.checked) {
            state.materials.push(e.target.dataset.material);
        } else {
            state.materials = state.materials.filter(m => m !== e.target.dataset.material);
        }
        createBooth();
        updateCostDisplay();
    });
});

document.querySelectorAll('[data-equipment]').forEach(checkbox => {
    checkbox.addEventListener('change', (e) => {
        if (e.target.checked) {
            state.equipment.push(e.target.dataset.equipment);
        } else {
            state.equipment = state.equipment.filter(eq => eq !== e.target.dataset.equipment);
        }
        createBooth();
        updateCostDisplay();
    });
});

// ============================================================================
// MULTILINGUAL SAVE/RESET/SHARE
// ============================================================================
function saveConfiguration() {
    const config = {
        length: state.length,
        width: state.width,
        construction: state.construction,
        wallColor: state.wallColor,
        materials: state.materials,
        equipment: state.equipment,
        cost: calculateCost()
    };

    localStorage.setItem('boothConfig', JSON.stringify(config));

    const params = new URLSearchParams({
        length: state.length,
        width: state.width,
        construction: state.construction,
        color: state.wallColor,
        materials: state.materials.join(','),
        equipment: state.equipment.join(',')
    });

    const shareLink = `${window.location.origin}${window.location.pathname}?${params.toString()}`;

    // Используем переводы
    const messages = i18n[currentLanguage] || i18n.en;
    alert(`${messages.saved}\n\n${messages.share}${shareLink}`);

    navigator.clipboard.writeText(shareLink).then(() => {
        console.log(messages.copySuccess);
    }).catch(() => {});

    console.log('Configuration saved:', config);
}

function resetConfiguration() {
    state = {
        length: 3,
        width: 3,
        construction: 'standard',
        wallColor: '#FF6B6B',
        materials: [],
        equipment: []
    };

    // Reset UI
    const lengthInput = document.getElementById('lengthInput');
    const widthInput = document.getElementById('widthInput');
    if (lengthInput) lengthInput.value = 3;
    if (widthInput) widthInput.value = 3;

    document.querySelectorAll('[data-construction]').forEach(b => b.classList.remove('active'));
    document.querySelector('[data-construction="standard"]')?.classList.add('active');

    document.querySelectorAll('.color-btn').forEach(b => b.classList.remove('active'));
    document.querySelector('[data-color="#FF6B6B"]')?.classList.add('active');

    document.querySelectorAll('[data-material], [data-equipment]').forEach(cb => cb.checked = false);

    createBooth();
    updateCostDisplay();

    const messages = i18n[currentLanguage] || i18n.en;
    alert(messages.reset);
}

// ============================================================================
// LOAD FROM URL PARAMETERS
// ============================================================================
function loadFromURL() {
    const params = new URLSearchParams(window.location.search);

    if (params.has('length')) state.length = parseFloat(params.get('length'));
    if (params.has('width')) state.width = parseFloat(params.get('width'));
    if (params.has('construction')) state.construction = params.get('construction');
    if (params.has('color')) state.wallColor = params.get('color');
    if (params.has('materials')) {
        state.materials = params.get('materials').split(',').filter(m => m);
    }
    if (params.has('equipment')) {
        state.equipment = params.get('equipment').split(',').filter(e => e);
    }

    // Update UI
    const lengthInput = document.getElementById('lengthInput');
    const widthInput = document.getElementById('widthInput');
    if (lengthInput) lengthInput.value = state.length;
    if (widthInput) widthInput.value = state.width;

    document.querySelectorAll('[data-construction]').forEach(b => {
        b.classList.toggle('active', b.dataset.construction === state.construction);
    });

    document.querySelectorAll('.color-btn').forEach(b => {
        b.classList.toggle('active', b.dataset.color === state.wallColor);
    });

    state.materials.forEach(material => {
        const checkbox = document.querySelector(`[data-material="${material}"]`);
        if (checkbox) checkbox.checked = true;
    });

    state.equipment.forEach(equipment => {
        const checkbox = document.querySelector(`[data-equipment="${equipment}"]`);
        if (checkbox) checkbox.checked = true;
    });

    createBooth();
    updateCostDisplay();
}

// ============================================================================
// INITIALIZATION
// ============================================================================
window.addEventListener('load', () => {
    initThreeJS();
    loadFromURL();
    updateCostDisplay();
});

// ============================================================================
// PUBLIC: function to change language externally
// ============================================================================
window.setConfiguratorLanguage = function(lang) {
    if (i18n[lang]) {
        currentLanguage = lang;
    }
};
// Обработка кнопок модального окна
document.addEventListener('DOMContentLoaded', () => {
    const newBtn = document.getElementById('newModeBtn');
    const loadBtn = document.getElementById('loadModeBtn');
    const modal = document.getElementById('modeModal');

    if (newBtn) {
        newBtn.onclick = () => {
            console.log("Create New clicked");
            modal.style.display = 'none'; // Закрываем окно
        };
    }

    if (loadBtn) {
        loadBtn.onclick = () => {
            console.log("Load Config clicked");
            // Здесь можно вызвать функцию загрузки, если она есть
            alert("Load function is not implemented in JS yet");
        };
    }
});
