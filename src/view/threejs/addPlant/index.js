// 引入threejs
import * as THREE from 'three';
// 引入gltf模型加载器
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';

// 声明树木的模型变量
let pine, autumnTree, shortTree1, shortTree2, tree1, tree2, tree3, tree4, tree5, tree6;
// 创建gltf模型加载器
const gltfLoader = new GLTFLoader();
gltfLoader.loadAsync(`./plant/pine.glb`).then(gltf => {
    pine = gltf;
    pine.scene.scale.set(2, 2, 2);
})
gltfLoader.loadAsync(`./plant/autumnTree.glb`).then(gltf => {
    autumnTree = gltf;
})
gltfLoader.loadAsync(`./plant/shortTree1.glb`).then(gltf => {
    shortTree1 = gltf;
})
gltfLoader.loadAsync(`./plant/shortTree2.glb`).then(gltf => {
    shortTree2 = gltf;
})
gltfLoader.loadAsync(`./plant/tree1.glb`).then(gltf => {
    tree1 = gltf;
})
gltfLoader.loadAsync(`./plant/tree2.glb`).then(gltf => {
    tree2 = gltf;
})
gltfLoader.loadAsync(`./plant/tree3.glb`).then(gltf => {
    tree3 = gltf;
})
gltfLoader.loadAsync(`./plant/tree4.glb`).then(gltf => {
    tree4 = gltf;
})
gltfLoader.loadAsync(`./plant/tree5.glb`).then(gltf => {
    tree5 = gltf;
})
gltfLoader.loadAsync(`./plant/tree6.glb`).then(gltf => {
    tree6 = gltf;
})

function addPlant (model) {
    // 树木名称对象，通过键名匹配对应的模型变量
    const treeNameObj = {
        '松树坐标': pine,
        '秋天树2坐标': tree6,
        '秋天树坐标': tree5,
        '矮树坐标': tree6,
        '大树坐标': tree6,
        '小树2坐标': tree6,
        '高树坐标': tree6,
        '旧树坐标': tree6,
        // '松树坐标': pine,
        // '秋天树坐标': pine,
        // '秋天树坐标': pine,
        // '矮树坐标': tree5,
        // '大树坐标': tree5,
        // '小树2坐标': tree5,
        // '高树坐标': tree6,
        // '旧树坐标': tree6,
    }
    // 创建一个植物组对象，存储所有植物
    const plantGroup = new THREE.Group();
    plantGroup.position.y = -0.1;
    plantGroup.name = '植物';

    for (let name in treeNameObj) {
        const treePos = model.getObjectByName(name);
        // 获取到对应的树模型
        const tree = treeNameObj[name].scene;
        // 给树模型添加阴影效果
        tree.traverse(obj => {
            obj.position.set(0, 0, 0);
            if (obj.isMesh) {
                // 允许产生阴影
                obj.castShadow = true;
            }
        })
        treePos.children.map((item, index) => {
            // 每次遍历克隆新的树
            const cloneTree = tree.clone();
            // 将空对象位置复制到树模型位置
            cloneTree.position.copy(treePos.position);
            cloneTree.position.add(item.position);
            plantGroup.add(cloneTree)
        });
    }
    model.add(plantGroup);
}

export { addPlant }
