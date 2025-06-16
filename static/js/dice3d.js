class Dice3D {
    constructor(containerId) {
        this.container = document.getElementById(containerId) || document.body;
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        this.world = new CANNON.World();
        this.diceList = [];
        this.rolling = false;
        
        this.dice_body_material = new CANNON.Material();
        this.desk_body_material = new CANNON.Material();
        
        this.sounds = true;
        this.soundPool = [];
        this.textures = {};
        this.shadows = true;
        
        this.init();
    }

    init() {
        // Configuration du renderer pour se superposer au site
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.shadowMap.enabled = this.shadows;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.setClearColor(0x000000, 0); // Fond transparent
        this.renderer.domElement.style.position = 'fixed';
        this.renderer.domElement.style.top = '0';
        this.renderer.domElement.style.left = '0';
        this.renderer.domElement.style.width = '100%';
        this.renderer.domElement.style.height = '100%';
        this.renderer.domElement.style.pointerEvents = 'none'; // Laisser passer les clics
        this.renderer.domElement.style.zIndex = '9999'; // Au-dessus de tout
        this.renderer.domElement.style.display = 'none'; // Caché par défaut
        document.body.appendChild(this.renderer.domElement);

        // Configuration de la caméra avec vue de haut
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.camera.position.set(0, 0, 600);
        this.camera.lookAt(0, 0, 0);

        // Configuration du monde physique
        this.world.gravity.set(0, 0, -9.8 * 800);
        this.world.broadphase = new CANNON.NaiveBroadphase();
        this.world.solver.iterations = 16;
        this.world.allowSleep = true;
        
        // Ajouter un damping global pour ralentir les objets
        this.world.defaultContactMaterial.friction = 0.9;
        this.world.defaultContactMaterial.restitution = 0.1;

        // Éclairage amélioré
        const ambientLight = new THREE.AmbientLight(0x404040, 0.8);
        this.scene.add(ambientLight);

        this.light = new THREE.DirectionalLight(0xffffff, 1.2);
        this.light.position.set(200, 200, 400);
        this.light.castShadow = this.shadows;
        this.light.shadow.mapSize.width = 2048;
        this.light.shadow.mapSize.height = 2048;
        this.light.shadow.camera.left = -800;
        this.light.shadow.camera.right = 800;
        this.light.shadow.camera.top = 600;
        this.light.shadow.camera.bottom = -600;
        this.scene.add(this.light);

        // Surface invisible pour physique seulement
        this.createInvisibleFloor();
        
        // Matériaux de contact
        this.world.addContactMaterial(new CANNON.ContactMaterial(
            this.desk_body_material, 
            this.dice_body_material, 
            { friction: 0.9, restitution: 0.1 }
        ));

        // Charger les sons
        this.loadSounds();

        // Gérer le redimensionnement
        window.addEventListener('resize', () => {
            this.handleResize();
        });

        // Démarrer la boucle d'animation
        this.animate();
    }

    createInvisibleFloor() {
        // Surface physique invisible (pas de rendu)
        const deskShape = new CANNON.Plane();
        const deskBody = new CANNON.Body({ mass: 0, material: this.desk_body_material });
        deskBody.addShape(deskShape);
        this.world.add(deskBody);

        // Murs invisibles pour les limites d'écran
        this.createWalls();
    }

    createWalls() {
        const screenWidth = window.innerWidth;
        const screenHeight = window.innerHeight;
        
        const wallPositions = [
            { x: 0, y: screenHeight/2, z: 0, rotX: Math.PI / 2, rotY: 0, rotZ: 0 },
            { x: 0, y: -screenHeight/2, z: 0, rotX: -Math.PI / 2, rotY: 0, rotZ: 0 },
            { x: screenWidth/2, y: 0, z: 0, rotX: 0, rotY: -Math.PI / 2, rotZ: 0 },
            { x: -screenWidth/2, y: 0, z: 0, rotX: 0, rotY: Math.PI / 2, rotZ: 0 }
        ];

        wallPositions.forEach(wall => {
            const wallBody = new CANNON.Body({ mass: 0 });
            wallBody.addShape(new CANNON.Plane());
            wallBody.position.set(wall.x, wall.y, wall.z);
            
            if (wall.rotX !== 0) {
                wallBody.quaternion.setFromAxisAngle(new CANNON.Vec3(1, 0, 0), wall.rotX);
            } else if (wall.rotY !== 0) {
                wallBody.quaternion.setFromAxisAngle(new CANNON.Vec3(0, 1, 0), wall.rotY);
            }
            
            this.world.add(wallBody);
        });
    }

    handleResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }

    show() {
        this.renderer.domElement.style.display = 'block';
    }

    hide() {
        this.renderer.domElement.style.display = 'none';
    }

    loadTextures() {
        // Textures pas nécessaires pour l'instant
    }

    loadSounds() {
        for (let i = 1; i <= 15; i++) {
            const audio = new Audio(`/static/sounds/dicehit${i}.wav`);
            audio.volume = 0.3;
            this.soundPool.push(audio);
        }
    }

    createDie(type, position = { x: 0, y: 0, z: 50 }) {
        let geometry;
        const sides = parseInt(type.substring(1));

        // Géométries correctes pour chaque type de dé
        switch (type) {
            case 'd4':
                geometry = new THREE.TetrahedronGeometry(25);
                break;
            case 'd6':
                geometry = new THREE.BoxGeometry(25, 25, 25);
                break;
            case 'd8':
                geometry = new THREE.OctahedronGeometry(25);
                break;
            case 'd10':
                // Créer un vrai d10 (bipyramide pentagonale)
                geometry = new THREE.ConeGeometry(20, 35, 5);
                // Rotation pour que ce soit plus stable
                geometry.rotateX(Math.PI);
                break;
            case 'd12':
                geometry = new THREE.DodecahedronGeometry(25);
                break;
            case 'd20':
                geometry = new THREE.IcosahedronGeometry(25);
                break;
            case 'd100':
                // D100 sous forme de sphère avec facettes
                geometry = new THREE.SphereGeometry(25, 16, 12);
                break;
            default:
                geometry = new THREE.BoxGeometry(25, 25, 25);
        }

        const material = new THREE.MeshLambertMaterial({ 
            color: this.getRandomColor(),
            transparent: true,
            opacity: 0.9
        });

        const die = new THREE.Mesh(geometry, material);
        die.position.set(position.x, position.y, position.z);
        die.castShadow = true;
        die.userData = { type: type, sides: sides };
        
        this.scene.add(die);

        // Corps physique adapté par type - utiliser des boîtes pour éviter le roulement infini
        let shape;
        switch (type) {
            case 'd4':
                shape = new CANNON.Box(new CANNON.Vec3(15, 15, 15));
                break;
            case 'd6':
                shape = new CANNON.Box(new CANNON.Vec3(12.5, 12.5, 12.5));
                break;
            case 'd8':
                // Boîte légèrement aplatie pour simuler l'octaèdre
                shape = new CANNON.Box(new CANNON.Vec3(15, 15, 12));
                break;
            case 'd10':
                // Cône pour correspondre à la géométrie
                shape = new CANNON.Box(new CANNON.Vec3(12, 12, 17));
                break;
            case 'd12':
                // Boîte arrondie pour dodécaèdre
                shape = new CANNON.Box(new CANNON.Vec3(14, 14, 14));
                break;
            case 'd20':
                // Boîte pour icosaèdre
                shape = new CANNON.Box(new CANNON.Vec3(13, 13, 13));
                break;
            case 'd100':
                // Sphère mais avec plus de friction pour s'arrêter
                shape = new CANNON.Sphere(20);
                break;
            default:
                shape = new CANNON.Box(new CANNON.Vec3(12.5, 12.5, 12.5));
        }

        const body = new CANNON.Body({ 
            mass: 1, 
            material: this.dice_body_material 
        });
        body.addShape(shape);
        body.position.set(position.x, position.y, position.z);
        body.userData = { mesh: die, type: type, sides: sides };
        
        // Ajouter de la friction spécialement pour éviter le roulement infini
        body.material.friction = 0.8;
        body.material.restitution = 0.2;
        body.linearDamping = 0.4;  // Ralentissement linéaire
        body.angularDamping = 0.4; // Ralentissement angulaire
        
        this.world.add(body);
        this.diceList.push({ mesh: die, body: body });

        return { mesh: die, body: body };
    }

    getRandomColor() {
        const colors = [0xff4757, 0x2ed573, 0x1e90ff, 0xffa502, 0xff6348, 0x7bed9f, 0x70a1ff, 0x5f27cd, 0x00d2d3, 0xff9ff3];
        return colors[Math.floor(Math.random() * colors.length)];
    }

    rollDice(count, type) {
        return new Promise((resolve) => {
            // Permettre de relancer même si des dés roulent encore
            this.rolling = true;
            this.clearDice(); // Toujours effacer les dés précédents

            this.show(); // Afficher le canvas 3D

            const results = [];
            const diceObjects = [];

            for (let i = 0; i < count; i++) {
                // Position aléatoire sur l'écran
                const position = {
                    x: (Math.random() - 0.5) * (window.innerWidth * 0.6),
                    y: (Math.random() - 0.5) * (window.innerHeight * 0.6),
                    z: 200 + Math.random() * 200
                };

                const die = this.createDie(type, position);
                
                // Vitesse plus réaliste
                die.body.velocity.set(
                    (Math.random() - 0.5) * 300,
                    (Math.random() - 0.5) * 300,
                    Math.random() * 100 + 50
                );
                
                die.body.angularVelocity.set(
                    Math.random() * 20 - 10,
                    Math.random() * 20 - 10,
                    Math.random() * 20 - 10
                );

                diceObjects.push(die);
            }

            // Jouer un son
            if (this.sounds && this.soundPool.length > 0) {
                const randomSound = this.soundPool[Math.floor(Math.random() * this.soundPool.length)];
                randomSound.currentTime = 0;
                randomSound.play().catch(() => {});
            }

            // Meilleure détection d'arrêt avec timeout
            let checkCount = 0;
            const maxChecks = 150; // 15 secondes max

            const checkIfStopped = () => {
                checkCount++;

                const stopped = diceObjects.every(die => {
                    const vel = die.body.velocity;
                    const angVel = die.body.angularVelocity;
                    const totalVel = Math.sqrt(vel.x*vel.x + vel.y*vel.y + vel.z*vel.z);
                    const totalAngVel = Math.sqrt(angVel.x*angVel.x + angVel.y*angVel.y + angVel.z*angVel.z);
                    
                    return totalVel < 2 && totalAngVel < 1; // Seuils encore plus stricts mais pas trop
                });

                // Forcer l'arrêt seulement après un bon délai
                const forceStop = checkCount >= maxChecks || checkCount >= 80; // Force après 8 secondes minimum

                if (stopped || forceStop) {
                    // Arrêter complètement les dés
                    diceObjects.forEach(die => {
                        die.body.velocity.set(0, 0, 0);
                        die.body.angularVelocity.set(0, 0, 0);
                        die.body.sleep(); // Forcer le sommeil
                        
                        // Forcer la position au sol si besoin
                        if (die.body.position.z < 15) {
                            die.body.position.z = 15;
                        }
                    });

                    // Générer les résultats
                    diceObjects.forEach((die, index) => {
                        const sides = die.body.userData.sides;
                        const result = Math.floor(Math.random() * sides) + 1;
                        results.push(result);
                        
                        // Afficher le résultat
                        setTimeout(() => {
                            this.showDiceResult(die.mesh, result);
                        }, index * 100);
                    });

                    this.rolling = false;
                    
                    // Cacher automatiquement après 8 secondes (plus long)
                    setTimeout(() => {
                        this.hide();
                    }, 8000);

                    resolve(results);
                } else {
                    setTimeout(checkIfStopped, 100);
                }
            };

            // Commencer à vérifier après 1 seconde (laisser plus de temps)
            setTimeout(checkIfStopped, 1000);
        });
    }

    showDiceResult(diceMesh, result) {
        // Créer un texte 3D pour afficher le résultat avec de meilleurs styles
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = 128;
        canvas.height = 128;
        
        // Background avec gradient plus visible
        const gradient = context.createRadialGradient(64, 64, 10, 64, 64, 64);
        gradient.addColorStop(0, 'rgba(255, 255, 255, 0.95)');
        gradient.addColorStop(0.8, 'rgba(255, 255, 255, 0.85)');
        gradient.addColorStop(1, 'rgba(200, 200, 200, 0.8)');
        
        context.fillStyle = gradient;
        context.beginPath();
        context.arc(64, 64, 60, 0, Math.PI * 2);
        context.fill();
        
        // Border plus visible
        context.strokeStyle = '#000';
        context.lineWidth = 4;
        context.stroke();
        
        // Text plus gros et plus visible
        context.fillStyle = '#000';
        context.font = 'bold 52px Arial';
        context.textAlign = 'center';
        context.textBaseline = 'middle';
        context.fillText(result.toString(), 64, 64);
        
        const texture = new THREE.CanvasTexture(canvas);
        const spriteMaterial = new THREE.SpriteMaterial({ 
            map: texture,
            transparent: true,
            alphaTest: 0.1
        });
        const sprite = new THREE.Sprite(spriteMaterial);
        
        sprite.position.copy(diceMesh.position);
        sprite.position.z += 30; // Plus proche pour vue de haut
        sprite.scale.set(40, 40, 1); // Plus petit pour être proportionnel
        
        this.scene.add(sprite);
        
        // Animation d'apparition plus rapide
        sprite.material.opacity = 0;
        const fadeIn = () => {
            sprite.material.opacity += 0.1;
            if (sprite.material.opacity < 1) {
                requestAnimationFrame(fadeIn);
            }
        };
        fadeIn();
        
        // Supprimer le sprite après quelques secondes avec animation
        setTimeout(() => {
            const fadeOut = () => {
                sprite.material.opacity -= 0.05;
                if (sprite.material.opacity > 0) {
                    requestAnimationFrame(fadeOut);
                } else {
                    this.scene.remove(sprite);
                }
            };
            fadeOut();
        }, 3000); // Affiché moins longtemps
    }

    clearDice() {
        this.diceList.forEach(dice => {
            this.scene.remove(dice.mesh);
            this.world.remove(dice.body);
        });
        this.diceList = [];
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        
        this.world.step(1/60);
        
        // Synchroniser les meshes avec les corps physiques
        this.diceList.forEach(dice => {
            dice.mesh.position.copy(dice.body.position);
            dice.mesh.quaternion.copy(dice.body.quaternion);
        });
        
        this.renderer.render(this.scene, this.camera);
    }

    enableShadows() {
        this.shadows = true;
        if (this.renderer) this.renderer.shadowMap.enabled = this.shadows;
        if (this.light) this.light.castShadow = this.shadows;
    }
    
    disableShadows() {
        this.shadows = false;
        if (this.renderer) this.renderer.shadowMap.enabled = this.shadows;
        if (this.light) this.light.castShadow = this.shadows;
    }
}

// Export pour utilisation globale
window.Dice3D = Dice3D; 