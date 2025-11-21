
// 引入threejs
import * as THREE from 'three';
// 引入gltf模型加载器
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
// 添加围栏函数
import { addFence } from '../addFence/index.js';
// 添加树模型函数
import { addPlant } from "../addPlant/index.js";



// 添加污水厂模型函数
async function addSewageModel (envMap) {
    // 创建模型组对象
    const model = new THREE.Group();
    model.rotateY(-Math.PI / 2);
    model.name = '污水厂模型';

    // 进度条元素
    const progressDiv = document.getElementsByClassName('ant-progress-bg')[0];
    // 进度条文字百分比元素
    const progressText = document.getElementsByClassName('ant-progress-text')[0];

    // 创建gltf模型加载器
    const gltfLoader = new GLTFLoader();

    return new Promise(resolve => {
        // http://211.143.122.110:18062/model/sewage.glb
        // 加载污水厂模型
        gltfLoader.load('./sewageModel.glb', (gltf) => {
            gltf.scene.traverse(function (obj) {
                if (obj.name.includes('玻璃')) {
                    //console.log(obj, 'obj')
                    obj.material.envMap = envMap;
                    obj.material.metalness = 0.3;
                    obj.material.roughness = 0.5;
                    obj.material.transparent = true;
                    obj.material.opacity = 0.9;
                    obj.material.refractionRatio = 0.5;
                    obj.material.envMapIntensity = 1;
                    obj.material.reflectivity = 0.9;
                    obj.material.transmission = 1.0;
                    obj.material.thickness = 0.5;


                    // obj.material = new THREE.MeshPhysicalMaterial({
                    //     color: '#A0CDE8',
                    //     metalness: 0.3,
                    //     roughness: 0.3,
                    //     transparent: true,
                    //     transmission: 0.5,
                    //     refractionRatio: 0.5,
                    //     reflectivity: 0.9,
                    //     opacity: 0.9,
                    //     thickness: 0.5,
                    //     envMap: envMap
                    // })
                }
                if (obj.isMesh) {
                    // 开启产生阴影
                    obj.castShadow = true;
                    // 开启接受阴影
                    obj.receiveShadow = true;
                }
            })
            model.add(gltf.scenes[0]);
            // 添加围栏
            addFence(gltf.scenes[0]);
            // 添加树模型
            addPlant(gltf.scenes[0]);


            // 延迟几秒再隐藏进度条
            setTimeout(() => {
                // 隐藏进度条
                document.getElementsByClassName('progress')[0].style.display = 'none';
            }, 2000);
            resolve(model);
        },
            (xhr) => {
                // 模型加载百分比进度
                const percent = ((xhr.loaded / xhr.total) * 100).toFixed(1);
                // 设置加载进度(由于进度条动画存在一定延迟，所以在基础上加一点)
                progressDiv.style.width = (percent - '') + 6 + '%';
                if (percent === '100.0') {
                    // 加载进度完成时告诉用户正在初始化项目
                    progressText.innerHTML = `项目正在初始化`;
                } else {
                    // 告诉用户加载进度百分比
                    progressText.innerHTML = `模型加载中${percent}%`;
                }
            })
    })
}

export { addSewageModel }
