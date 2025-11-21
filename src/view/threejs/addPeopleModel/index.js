// 引入Three.js
import * as THREE from 'three';
// 引入gltf模型加载库GLTFLoader.js
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
// 人物步行动作
let WalkAction = null;
// 加载人物模型
async function addPeopleModel () {
    // 创建gltf模型加载器
    const gltfLoader = new GLTFLoader();
    const gltf = await gltfLoader.loadAsync("./worker.glb");
    return new Promise(resolve => {
        // 创建人物模型组对象
        const peopleGroup = new THREE.Group();
        peopleGroup.name = '人物模型组对象';
        gltf.scene.scale.set(0.6, 0.6, 0.6);
        // 开启人物模型产生阴影和接收阴影
        gltf.scene.children[0].children.map(obj => {
            obj.castShadow = true;
            obj.receiveShadow = true;
        })

        gltf.scene.name = '人物模型';
        peopleGroup.add(gltf.scene);
        // peopleGroup.position.y -= 0.1;
        // 创建播放器
        const mixer = new THREE.AnimationMixer(gltf.scene);
        // 添加步行动作动画
        WalkAction = mixer.clipAction(gltf.animations[0]);
        WalkAction.play();
        // 默认权重休息动画
        // IdleAction.weight = 1.0;
        WalkAction.weight = 1.0;
        resolve({ peopleGroup: peopleGroup, mixer: mixer })
    });
}
export { addPeopleModel, WalkAction }
