import * as THREE from "three";

export function setPoolMaterial (sewageModel) {
    const loader = new THREE.TextureLoader();
    const texture = loader.load("./Bricks066_2K-JPG_Color.jpg", (texture) => {
        texture.wrapS = THREE.RepeatWrapping;
        texture.wrapT = THREE.RepeatWrapping;
        // texture.flipY = false;
        texture.repeat.set(50, 50);
        // texture.offset.set(0.5, 0.5);
    });
    const normalMap = loader.load(
        "./Bricks066_2K-JPG_NormalDX.jpg",
        (texture) => {
            texture.wrapS = THREE.RepeatWrapping;
            texture.wrapT = THREE.RepeatWrapping;
            // texture.flipY = false;
            texture.repeat.set(50, 50);
            // texture.offset.set(0.5, 0.5);
        }
    );
    const roughnessMap = loader.load(
        "./Bricks066_2K-JPG_Roughness.jpg",
        (texture) => {
            texture.wrapS = THREE.RepeatWrapping;
            texture.wrapT = THREE.RepeatWrapping;
            // texture.flipY = false;
            texture.repeat.set(50, 50);
            // texture.offset.set(0.5, 0.5);
        }
    );
    const aoMap = loader.load(
        "./Bricks066_2K-JPG_AmbientOcclusion.jpg",
        (texture) => {
            texture.wrapS = THREE.RepeatWrapping;
            texture.wrapT = THREE.RepeatWrapping;
            // texture.flipY = false;
            texture.repeat.set(50, 50);
            // texture.offset.set(0.5, 0.5);
        }
    );


    let poolMeshNameArr = ['南北生物池蓝色', '南北生物池蓝色外', '南北生物池水泥', '西生物池外墙004'];

    poolMeshNameArr.forEach(name => {
        const mesh = sewageModel.getObjectByName(name);
        if (mesh.children.length > 0) {
            mesh.children.map((item, index) => {
                item.material.map = texture;
                item.material.normalMap = normalMap;
                item.material.roughnessMap = roughnessMap;
                item.material.aoMap = aoMap;
                item.material.displacementScale = 0.1;
                item.material.roughness = 0.5;
                item.material.metalness = 0.2;
                item.material.reflectivity = 0.5;
                item.material.clearcoat = 1.0;
                item.material.clearcoatRoughness = 0.1;
                // item.material.color = new THREE.Color("#9C9C9C");

            })
        } else if (name.includes('外墙')) {
            mesh.material.map = texture;
            mesh.material.normalMap = normalMap;
            mesh.material.roughnessMap = roughnessMap;
            mesh.material.aoMap = aoMap;
            mesh.material.displacementScale = 0.1;
            mesh.material.roughness = 0.5;
            mesh.material.metalness = 0.2;
            mesh.material.reflectivity = 0.5;
            mesh.material.clearcoat = 1.0;
            mesh.material.clearcoatRoughness = 0.1;
            // item.material.color = new THREE.Color("#9C9C9C");
        } else {
            mesh.material.map = texture;
            mesh.material.normalMap = normalMap;
            mesh.material.roughnessMap = roughnessMap;
            mesh.material.aoMap = aoMap;
            mesh.material.displacementScale = 0.1;
            mesh.material.roughness = 0.5;
            mesh.material.metalness = 0.2;
            mesh.material.reflectivity = 0.5;
            mesh.material.clearcoat = 1.0;
            mesh.material.clearcoatRoughness = 0.1;
            mesh.material.color = new THREE.Color("#50A0D7");
        }

    })
}
